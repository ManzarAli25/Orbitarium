
## 🧩 **Project Overview: "Orbitarium"**

**Goal:** A platform + bot system that
1️⃣ visualizes real-time satellite motion on an interactive globe,
2️⃣ predicts potential orbit collisions or close approaches, and
3️⃣ posts daily, auto-generated space insights to Reddit.

---

# 1️⃣ INTERACTIVE VISUALIZATION (Frontend)

### 🪐 **What to visualize**

You have several possibilities from the `N2YOClient`:

| N2YO Method                                  | Data You Can Visualize             | Description                               |
| -------------------------------------------- | ---------------------------------- | ----------------------------------------- |
| `get_objects_above()`                        | Satellite positions above a region | Real-time positions of visible satellites |
| `get_positions()`                            | Predicted groundtrack              | Animate the satellite moving across Earth |
| `get_tle()`                                  | Orbital path (from TLEs)           | Draw orbit path on globe                  |
| `get_visual_passes()` / `get_radio_passes()` | Visibility over time               | Mark when a satellite will be visible     |

---

### 🌍 **How to visualize (interactive globe)**

Use **CesiumJS** or **Three.js + Globe.gl**.
Both support 3D Earth + real-time plotting of satellites.

#### 🔹 Option A — CesiumJS (most accurate, NASA-style)

* Built-in support for TLE-to-orbit rendering (via `satellite.js`).
* You can render each satellite’s orbit arc and current position.
* Use WebSocket or polling to update every 30 seconds.

Example architecture:

```
Frontend (Next.js + CesiumJS)
↓
Backend (FastAPI / Flask)
↓
N2YOClient (fetches positions)
```

#### 🔹 Option B — Globe.gl (simpler, quick prototype)

```bash
npm install globe.gl satellite.js
```

Example snippet:

```js
import Globe from 'globe.gl';
import * as satellite from 'satellite.js';

const globe = Globe()(document.getElementById('globe'))
  .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg');

fetch('/api/above')  // your backend endpoint using N2YOClient.get_objects_above
  .then(res => res.json())
  .then(({ satellites }) => {
    globe.pointsData(satellites.map(s => ({
      lat: s.latitude,
      lng: s.longitude,
      size: 0.6,
      color: 'orange',
      label: s.name
    })));
  });
```

**💡 Nice enhancement:**
Clicking a satellite can show its `tle`, predicted path (`get_positions`), and next visible pass.

---

# 2️⃣ COLLISION PREDICTION (ML / Simulation Component)

### 🎯 **Goal: Predict potential close approaches**

You want to flag if two satellites will pass dangerously close (< X km).

---

### 🧠 **Approach A — Physics-based (recommended start)**

* Use **TLE → orbital coordinates** conversion (`satellite.js` in JS or `sgp4` in Python).
* Propagate each satellite’s orbit 24 hours into the future (e.g., every 10s).
* Compute **Euclidean distances** between all pairs.
* Flag when `distance < threshold (e.g., 5 km)`.

```python
from sgp4.api import Satrec, jday
import numpy as np

def predict_collision(tle1, tle2, hours=24, step=10):
    sat1 = Satrec.twoline2rv(tle1['line1'], tle1['line2'])
    sat2 = Satrec.twoline2rv(tle2['line1'], tle2['line2'])
    jd, fr = jday(2025, 10, 8, 0, 0, 0)

    min_dist = float('inf')
    for t in range(0, hours * 3600, step):
        e1, r1, v1 = sat1.sgp4(jd, fr + t / 86400)
        e2, r2, v2 = sat2.sgp4(jd, fr + t / 86400)
        if e1 == 0 and e2 == 0:
            dist = np.linalg.norm(np.array(r1) - np.array(r2))
            min_dist = min(min_dist, dist)
    return min_dist < 5  # collision threshold
```

You can fetch current TLEs for all “above” satellites from N2YO and check close approaches.

---

### 🤖 **Approach B — ML-based (optional, advanced)**

Train a model to predict potential close approaches using features such as:

* `altitude difference`
* `velocity difference`
* `relative inclination`
* `historical near misses`

You could use:

* **Isolation Forest** for anomaly detection (unusual orbit intersections)
* **RandomForestClassifier** for binary “will-collide / won’t-collide” predictions
* **LSTM** for sequence-based trajectory prediction (if you have historical telemetry)

**However**, since N2YO gives limited samples, a physics-based model (SGP4) is more accurate and interpretable initially.

---

### ⚙️ **Pipeline**

```
get_objects_above(lat, lng, alt)
  ↓
get_tle() for each satellite
  ↓
simulate orbits via SGP4
  ↓
compute pairwise distances
  ↓
visualize "red arcs" for possible collisions on globe
```

---

# 3️⃣ REDDIT BOT (LLM + N2YO Integration)

### 💬 **Goal:** Post a daily satellite-related insight on Reddit.

---

### 🔹 Step 1 — Reddit Bot Setup

Use `praw` (Python Reddit API Wrapper):

```bash
pip install praw
```

```python
import praw
import os
from dotenv import load_dotenv

load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent="orbitarium-bot",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
)
```

---

### 🔹 Step 2 — Generate Nerdy Satellite Post

Use your `N2YOClient` to fetch a random satellite’s TLE or visible pass and combine with an LLM like OpenAI GPT or Gemini.

Example:

```python
from openai import OpenAI
import random

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

satellites = n2yo.get_objects_above(lat=40.7, lng=-74.0, alt=10)['satellites']
random_sat = random.choice(satellites)
tle = n2yo.get_tle(random_sat['id'])

prompt = f"""
Write a short, nerdy Reddit post about the satellite "{random_sat['name']}".
Include its launch date ({random_sat['launch_date']}) and something interesting about its orbit using this TLE:
{tle['tle']}
Make it sound fun but scientific.
"""

post = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
text = post.choices[0].message.content

reddit.subreddit("space").submit(title=f"Satellite Spotlight: {random_sat['name']}", selftext=text)
```

You can run this daily with a **cron job** or **GitHub Action**.

---

# 🧠 Putting It All Together

| Component           | Tech Stack                     | Purpose                                    |
| ------------------- | ------------------------------ | ------------------------------------------ |
| Visualization       | Next.js + CesiumJS or Globe.gl | Interactive 3D satellite globe             |
| Backend API         | FastAPI or Flask + N2YOClient  | Fetch & serve satellite data               |
| Collision Predictor | Python (SGP4 + NumPy)          | Simulate orbits & detect proximity events  |
| Reddit Bot          | Python + PRAW + LLM API        | Auto-generate & post daily satellite facts |
| Optional DB         | MongoDB / PostgreSQL           | Cache TLEs, logs, predictions              |

---

# 🚀 Suggested Roadmap

1️⃣ **Phase 1:** Backend setup → N2YOClient + Flask REST API
2️⃣ **Phase 2:** Globe visualization with live satellite tracking
3️⃣ **Phase 3:** Add collision simulation backend
4️⃣ **Phase 4:** Reddit Bot automation with OpenAI API
5️⃣ **Phase 5:** Deploy frontend + backend (e.g., on Vercel + Render)

---

Would you like me to **sketch the architecture diagram** (showing data flow between these components)? It’ll help you see how N2YO, SGP4, LLM, and Reddit fit together.
