''' the main entry point to our app'''
import os
from dotenv import load_dotenv
from n2yo_wrapper import N2YOClient

def main():
    """
    Main function to demonstrate the N2YOClient functionality.
    """
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.getenv("N2YO_KEY")

    if not api_key:
        print("Error: N2YO_KEY not found in .env file.")
        return

    # Initialize the client
    client = N2YOClient(api_key=api_key)

    # Observer location: New York City (approx. from example)
    observer_lat = 40.7
    observer_lng = -74.0
    observer_alt = 10  # Altitude in meters

    # --- Example 1: Get TLE data for ISS (NORAD ID: 25544) ---
    print("--- Fetching TLE data for the International Space Station (ISS) ---")
    try:
        iss_tle = client.get_tle(sat_id=25544)
        print(f"Successfully fetched TLE for: {iss_tle['satname']} (ID: {iss_tle['satid']})")
        print(f"  Line 1: {iss_tle['tle']['line1']}")
        print(f"  Line 2: {iss_tle['tle']['line2']}")
        print("-" * 20)
    except Exception as e:
        print(f"An error occurred while fetching TLE data: {e}")

    # --- Example 2: Get Visual Passes for ISS from a specific location ---
    print("\n--- Predicting visual passes for ISS over New York City ---")
    try:
        visual_passes = client.get_visual_passes(
            sat_id=25544,
            lat=observer_lat,
            lng=observer_lng,
            alt=observer_alt,
            days=5,
            min_visibility=100
        )
        if visual_passes and visual_passes['passes']:
            print(f"Found {len(visual_passes['passes'])} visual passes for {visual_passes['satellite']} in the next 5 days.")
            for p in visual_passes['passes']:
                print(f"  - Start: {p['start_time']} ({p['start_direction']}), "
                      f"End: {p['end_time']} ({p['end_direction']}), "
                      f"Duration: {p['duration_sec']}s, "
                      f"Max Elevation: {p['max_elevation_deg']}°")
        else:
            print("No visual passes found for the given parameters.")
        print("-" * 20)
    except Exception as e:
        print(f"An error occurred while fetching visual passes: {e}")

    # --- Example 3: Get Future Positions of ISS ---
    print("\n--- Getting future positions for ISS (next 60 seconds) ---")
    try:
        positions = client.get_positions(
            sat_id=25544,
            observer_lat=observer_lat,
            observer_lng=observer_lng,
            observer_alt=observer_alt,
            seconds=60
        )
        if positions and positions['positions']:
            print(f"Found {len(positions['positions'])} position points for {positions['satname']}.")
            # Print first 5 positions for brevity
            for pos in positions['positions'][:5]:
                print(f"  - Timestamp: {pos['timestamp']}, Lat: {pos['latitude']:.4f}, Lng: {pos['longitude']:.4f}, Alt: {pos['altitude']:.2f} km")
            if len(positions['positions']) > 5:
                print("  ...")
        else:
            print("Could not retrieve position data.")
        print("-" * 20)
    except Exception as e:
        print(f"An error occurred while fetching positions: {e}")

    # --- Example 4: Get Satellites Above a Location ---
    print("\n--- Getting satellites currently above New York City (45° radius) ---")
    try:
        satellites_above = client.get_objects_above(
            lat=observer_lat,
            lng=observer_lng,
            alt=observer_alt,
            search_radius=45 # search radius of 45 degrees
        )
        if satellites_above and satellites_above['satellites']:
            print(f"Found {satellites_above['count']} satellites in the '{satellites_above['category']}' category.")
            # Print first 5 satellites for brevity
            for sat in satellites_above['satellites'][:5]:
                print(f"  - Name: {sat['name']} (ID: {sat['id']}), Lat: {sat['latitude']:.4f}, Lng: {sat['longitude']:.4f}")
            if len(satellites_above['satellites']) > 5:
                print("  ...")
        else:
            print("No satellites found above this location currently.")
        print("-" * 20)
    except Exception as e:
        print(f"An error occurred while fetching objects above: {e}")


if __name__ == "__main__":
    main()