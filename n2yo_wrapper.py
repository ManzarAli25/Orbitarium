import requests
from datetime import datetime, timezone


class N2YOClient:
    """
    A unified client for interacting with the N2YO satellite tracking API.
    
    Attributes:
        api_key (str): Your N2YO API key for authentication.
        base_url (str): The base URL for the N2YO API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the N2YO API client.
        
        Args:
            api_key (str): Your N2YO API key.
        """
        if not api_key:
            raise ValueError("API key is required.")
        
        self.api_key = api_key
        self.base_url = "https://api.n2yo.com/rest/v1/satellite"
    
    def get_tle(self, sat_id: int) -> dict:
        """
        Fetches the Two Line Elements (TLE) data for a satellite.

        Args:
            sat_id (int): The NORAD ID of the satellite (e.g., 25544 for ISS).

        Returns:
            dict: Satellite info and TLE data split into two lines.
        """
        if not sat_id:
            raise ValueError("sat_id is required.")

        url = f"{self.base_url}/tle/{sat_id}&apiKey={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "tle" not in data:
                raise ValueError("Invalid response: 'tle' field missing from API response.")

            tle_lines = [line for line in data["tle"].split("\r\n") if line.strip()]

            return {
                "satid": data["info"]["satid"],
                "satname": data["info"]["satname"],
                "transactions": data["info"]["transactionscount"],
                "tle": {
                    "line1": tle_lines[0] if len(tle_lines) > 0 else None,
                    "line2": tle_lines[1] if len(tle_lines) > 1 else None
                }
            }

        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
            raise
        except ValueError as e:
            print(f"Data error: {e}")
            raise

    def get_visual_passes(
        self,
        sat_id: int,
        lat: float,
        lng: float,
        alt: float,
        days: int = 2,
        min_visibility: int = 60,
        convert_to_local: bool = False
    ) -> dict:
        """
        Retrieve predicted visual passes of a satellite relative to an observer's location.
        
        Args:
            sat_id (int): NORAD ID of the satellite (e.g., ISS = 25544).
            lat (float): Observer latitude in decimal degrees.
            lng (float): Observer longitude in decimal degrees.
            alt (float): Observer altitude in meters.
            days (int): Number of days to predict (max 10).
            min_visibility (int): Minimum visible duration (seconds).
            convert_to_local (bool): Convert UTC timestamps to local system time.
        
        Returns:
            dict: Satellite name and list of passes with timing and visibility info.
        """
        url = (
            f"{self.base_url}/visualpasses/"
            f"{sat_id}/{lat}/{lng}/{alt}/{days}/{min_visibility}/&apiKey={self.api_key}"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "passes" not in data or not data["passes"]:
                return {"satellite": data.get("info", {}).get("satname", "Unknown"), "passes": []}

            passes = []
            for p in data["passes"]:
                start_time = datetime.fromtimestamp(p["startUTC"], tz=timezone.utc)
                end_time = datetime.fromtimestamp(p["endUTC"], tz=timezone.utc)
                if convert_to_local:
                    start_time = start_time.astimezone()
                    end_time = end_time.astimezone()

                passes.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_sec": p["duration"],
                    "start_direction": p["startAzCompass"],
                    "end_direction": p["endAzCompass"],
                    "max_elevation_deg": p["maxEl"],
                    "brightness_mag": p["mag"]
                })

            return {
                "satellite": data["info"]["satname"],
                "passes": passes
            }

        except requests.RequestException as e:
            print(f"⚠️ API request failed: {e}")
            return None

    def get_positions(
        self,
        sat_id: int,
        observer_lat: float,
        observer_lng: float,
        observer_alt: float,
        seconds: int
    ) -> dict:
        """
        Fetches future groundtrack positions for a given satellite.

        Args:
            sat_id (int): NORAD ID of the satellite (e.g., 25544 for ISS)
            observer_lat (float): Observer's latitude in decimal degrees
            observer_lng (float): Observer's longitude in decimal degrees
            observer_alt (float): Observer's altitude above sea level in meters
            seconds (int): Number of seconds of future positions (max 300)

        Returns:
            dict: Satellite info and list of position data points.
        """
        if not all([sat_id, observer_lat, observer_lng]):
            raise ValueError("Missing required parameters (sat_id, lat, lng).")

        if seconds > 300:
            raise ValueError("Seconds parameter cannot exceed 300 (per API limit).")

        url = (
            f"{self.base_url}/positions/"
            f"{sat_id}/{observer_lat}/{observer_lng}/{observer_alt}/{seconds}/&apiKey={self.api_key}"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "positions" not in data:
                raise ValueError("Invalid response: 'positions' field missing from API response.")

            positions = []
            for p in data["positions"]:
                positions.append({
                    "latitude": p["satlatitude"],
                    "longitude": p["satlongitude"],
                    "altitude": p.get("sataltitude"),
                    "azimuth": p["azimuth"],
                    "elevation": p["elevation"],
                    "ra": p["ra"],
                    "dec": p["dec"],
                    "timestamp": p["timestamp"]
                })

            return {
                "satid": data["info"]["satid"],
                "satname": data["info"]["satname"],
                "transactions": data["info"]["transactionscount"],
                "positions": positions
            }

        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
            raise
        except ValueError as e:
            print(f"Data error: {e}")
            raise

    def get_radio_passes(
        self,
        sat_id: int,
        lat: float,
        lng: float,
        alt: float,
        days: int = 2,
        min_elevation: int = 30,
        convert_to_local: bool = False
    ) -> dict:
        """
        Retrieve predicted radio passes of a satellite relative to an observer's location.
        
        Args:
            sat_id (int): NORAD ID of the satellite (e.g., ISS = 25544).
            lat (float): Observer latitude in decimal degrees.
            lng (float): Observer longitude in decimal degrees.
            alt (float): Observer altitude above sea level in meters.
            days (int): Number of days to predict (max 10).
            min_elevation (int): Minimum acceptable max elevation (degrees).
            convert_to_local (bool): Convert UTC timestamps to local system time.
        
        Returns:
            dict: Satellite name and list of radio passes.
        """
        url = (
            f"{self.base_url}/radiopasses/"
            f"{sat_id}/{lat}/{lng}/{alt}/{days}/{min_elevation}/&apiKey={self.api_key}"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "passes" not in data or not data["passes"]:
                return {"satellite": data.get("info", {}).get("satname", "Unknown"), "passes": []}

            passes = []
            for p in data["passes"]:
                start_time = datetime.fromtimestamp(p["startUTC"], tz=timezone.utc)
                max_time = datetime.fromtimestamp(p["maxUTC"], tz=timezone.utc)
                end_time = datetime.fromtimestamp(p["endUTC"], tz=timezone.utc)

                if convert_to_local:
                    start_time = start_time.astimezone()
                    max_time = max_time.astimezone()
                    end_time = end_time.astimezone()

                passes.append({
                    "start_time": start_time,
                    "max_time": max_time,
                    "end_time": end_time,
                    "duration_sec": int((end_time - start_time).total_seconds()),
                    "start_direction": p["startAzCompass"],
                    "end_direction": p["endAzCompass"],
                    "max_elevation_deg": p["maxEl"],
                })

            return {
                "satellite": data["info"]["satname"],
                "passes": passes
            }

        except requests.RequestException as e:
            print(f"⚠️ API request failed: {e}")
            return None

    def get_objects_above(
        self,
        lat: float,
        lng: float,
        alt: float,
        search_radius: int = 90,
        category_id: int = 0
    ) -> dict:
        """
        Retrieve all satellites currently above an observer within a given search radius.

        Args:
            lat (float): Observer latitude in decimal degrees.
            lng (float): Observer longitude in decimal degrees.
            alt (float): Observer altitude above sea level in meters.
            search_radius (int): Search radius (0–90 degrees). 90 returns all satellites above the horizon.
            category_id (int): Satellite category ID (use 0 for all).

        Returns:
            dict: Category name, count, and list of satellites currently above the observer.
        """
        url = (
            f"{self.base_url}/above/"
            f"{lat}/{lng}/{alt}/{search_radius}/{category_id}/&apiKey={self.api_key}"
        )

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "above" not in data or not data["above"]:
                return {
                    "category": data.get("info", {}).get("category", "Unknown"),
                    "count": 0,
                    "satellites": []
                }

            satellites = []
            for sat in data["above"]:
                try:
                    launch_date = datetime.strptime(sat["launchDate"], "%Y-%m-%d")
                except Exception:
                    launch_date = None

                satellites.append({
                    "id": sat["satid"],
                    "name": sat["satname"],
                    "intl_designator": sat["intDesignator"],
                    "launch_date": launch_date,
                    "latitude": sat["satlat"],
                    "longitude": sat["satlng"],
                    "altitude_km": sat["satalt"],
                })

            return {
                "category": data["info"]["category"],
                "count": data["info"]["satcount"],
                "satellites": satellites
            }

        except requests.RequestException as e:
            print(f"⚠️ API request failed: {e}")
            return None


# Example usage:
if __name__ == "__main__":
    # Initialize the client
    import os
    from dotenv import load_dotenv
    import requests

    # Load environment variables from .env
    load_dotenv()

    API_KEY = os.getenv("N2YO_KEY")
    client = N2YOClient(api_key=API_KEY)
    # Use any method without passing the API key again
    tle_data = client.get_tle(sat_id=25544)
    passes = client.get_visual_passes(sat_id=25544, lat=40.7, lng=-74.0, alt=10)
    positions = client.get_positions(sat_id=25544, observer_lat=40.7, observer_lng=-74.0, observer_alt=10, seconds=60)
    satellites = client.get_objects_above(lat=40.7, lng=-74.0, alt=10)