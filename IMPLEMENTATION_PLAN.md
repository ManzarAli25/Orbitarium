Perfect question — because now, with the **MCP-based architecture** added, your project has evolved from “a cool visualization + API wrapper” into a **modular AI + automation ecosystem** for real-time satellite data intelligence and social engagement 🚀

Let’s lay out the **full updated project overview** step-by-step:

---

# 🌌 **Orbitarium — Intelligent Satellite Tracking & Automation Platform**

### 🧠 **Overview**

**Orbitarium** is an open-source system that combines **real-time satellite visualization**, **predictive modeling**, and **automated public engagement** using the N2YO API, CesiumJS, and the MCP (Model Context Protocol) framework.

It’s composed of modular services — each responsible for a specific domain — and orchestrated by an intelligent agent client that connects everything together.

---

## 🧩 **System Architecture**

```mermaid
flowchart LR
    subgraph N["🛰️ N2YO MCP Server"]
        N1[get_objects_above()]
        N2[get_tle()]
        N3[get_positions()]
    end

    subgraph R["🤖 Reddit MCP Server"]
        R1[generate_post_content()]
        R2[post_to_reddit()]
    end

    subgraph C["🧩 Orbitarium Agent Client"]
        C1[LLM Integration (OpenAI/Gemini)]
        C2[Cron Scheduler / Daily Automation]
        C3[Task Orchestrator]
    end

    subgraph V["🌍 Visualization Layer"]
        V1[CesiumJS 3D Globe]
        V2[Web Dashboard (Next.js / React)]
    end

    C3 --> N
    C3 --> R
    N --> V
```

---

## 🏗️ **Main Components**

### 1. 🛰️ **N2YO MCP Server**

* Wraps your `N2YOClient` class into an MCP-compatible API.
* Exposes tools like:

  * `get_tle(sat_id)`
  * `get_objects_above(lat, lng, alt)`
  * `get_positions(...)`
* Acts as a **data service** that any agent or app can consume.

📍 **Purpose:** Provide structured satellite data (TLEs, positions, passes) to other systems.

---

### 2. 🤖 **Reddit MCP Server**

* Handles Reddit automation using **PRAW** (Python Reddit API Wrapper).
* Integrates with an **LLM (e.g. GPT-4 or Gemini)** to auto-generate engaging posts about satellites.
* Exposes tools like:

  * `generate_post_content(satellite_name, tle)`
  * `post_to_reddit(subreddit, title, content)`

📍 **Purpose:** Create and post nerdy daily content on subreddits like r/space or r/askscience.

---

### 3. 🧠 **Orbitarium Agent Client**

* A single **MCP client** that connects to both servers.
* Fetches live data from N2YO, uses the LLM to generate Reddit content, and posts it via the Reddit MCP.
* Can be extended to integrate other APIs (Twitter, Discord, Mastodon, etc.).
* Optionally runs **on a cron schedule** (daily automation).

📍 **Purpose:** Acts as the **orchestrator and brain** of the system — automating workflows between multiple MCP servers.

---

### 4. 🌍 **Visualization Layer**

* **CesiumJS 3D Globe** to visualize satellites and their orbits in real-time.
* Connects to your `N2YO MCP` server via REST or WebSocket.
* Optionally uses **Next.js** or **React** to serve a dashboard showing:

  * Active satellites above an observer’s location
  * Ground tracks and predicted orbits
  * Collision probability overlays

📍 **Purpose:** Provide an interactive global view of satellite motion and analytics.

---

### 5. ⚙️ **(Optional) Collision Predictor**

A future module (can be integrated into N2YO MCP or a separate MCP service):

* Uses **machine learning / physics-based models** to predict potential orbital conjunctions.
* Could rely on:

  * N2YO’s position data
  * NASA or Celestrak catalog data
* Core idea: compute **spatial proximity** and **relative velocity** between satellites → estimate “close approach” probabilities.

📍 **Purpose:** Early warning system for possible orbital collisions.

---

## 🪐 **System Workflow Example**

1. **Data Layer**

   * N2YO MCP fetches new satellite data for the day.
   * Sends positions, TLEs, or visibility passes.

2. **AI Layer**

   * The Orbitarium agent asks an LLM to summarize something like:

     > “Write a short post about how ISS passes over NYC tonight.”

3. **Social Layer**

   * The Reddit MCP posts the generated content to `/r/space`.
   * Logs post metadata (URL, timestamp, engagement stats).

4. **Visualization**

   * CesiumJS dashboard updates in real-time with ISS trajectory and other satellites overhead.

---

## 📁 **Directory Structure**

```
orbitarium/
│
├── core/
│   └── n2yo_client.py
│
├── mcp_servers/
│   ├── n2yo_mcp_server.py
│   ├── reddit_mcp_server.py
│
├── client/
│   └── orbitarium_agent_client.py
│
├── web/
│   ├── cesium_dashboard/   # CesiumJS + Next.js front-end
│
├── models/
│   └── collision_predictor.py  # optional ML module
│
├── .env
├── requirements.txt
└── README.md
```

---

## 🧰 **Tech Stack**

| Layer           | Technology                        | Purpose                    |
| --------------- | --------------------------------- | -------------------------- |
| Backend         | Python, FastMCP                   | Satellite & Reddit servers |
| Client          | MCP Client SDK                    | Orchestrator agent         |
| Visualization   | CesiumJS + Next.js                | Interactive 3D globe       |
| ML / Prediction | Scikit-learn / PyTorch (optional) | Collision detection        |
| Automation      | Cron / APScheduler                | Daily Reddit posting       |
| LLM Integration | OpenAI API / Gemini API           | Content generation         |

---

## ⚙️ **Example Daily Automation Flow**

```bash
🕒 Every day at 10 AM UTC
   ↓
🤖 Orbitarium Agent wakes up
   ↓
🛰️ Calls N2YO MCP → get random visible satellite
   ↓
💬 Calls LLM → generate nerdy post about it
   ↓
🚀 Calls Reddit MCP → post to r/space
   ↓
✅ Logs URL and satellite metadata
```

---

## 🧩 **Why the Multi-Server Architecture Works**

| Benefit                       | Description                                                         |
| ----------------------------- | ------------------------------------------------------------------- |
| 🧠 **Separation of concerns** | N2YO, Reddit, ML — each isolated in its own server.                 |
| 🔐 **Secure API keys**        | No cross-leak of Reddit vs N2YO credentials.                        |
| 🚀 **Scalable**               | Each service can scale independently (microservices style).         |
| 🔄 **Interoperable**          | Any other MCP client (LLM, CLI, app) can use your servers.          |
| 🔧 **Extensible**             | Add new tools (e.g., “post_to_twitter”, “fetch_iss_stream”) easily. |

---

## 🌟 **Potential Extensions**

* Add a **Twitter MCP server** for cross-posting.
* Introduce a **Discord MCP bot** to notify users of visible passes.
* Implement **historical trajectory replay** on Cesium.
* Connect to **NASA’s Open Data API** for event-based triggers (e.g., launches).
