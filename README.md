# Digital Twin Project

A basic digital twin: a simulator generates sensor data for a device, a backend
stores and serves it, a twin model mirrors the device's state and flags
anomalies, and a dashboard visualizes real vs. twin data live.

## Architecture

```
simulator/  ->  POST /data  ->  backend  ->  GET /data/latest   ->  twin-model
                                    ^                                    |
                                    |____________ POST /twin/status _____|

backend  ->  GET /data/latest, /twin/status/latest  ->  frontend (dashboard)
```

## Team ownership

| Folder        | Owner    | Responsibility                                  |
|---------------|----------|--------------------------------------------------|
| `simulator/`  | Member A | Generates fake/real sensor readings              |
| `backend/`    | Member B | Stores & serves data via REST API                |
| `twin-model/` | Member C | Mirrors device state, detects anomalies          |
| `frontend/`   | Member D | Live dashboard (charts + status)                 |

## Data schema (agree on this before changing it)

```json
{
  "timestamp": "ISO-8601 string",
  "device_id": "string",
  "temperature": "float",
  "vibration": "float",
  "speed": "float"
}
```

## Setup & run (each in its own terminal)

**1. Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**2. Simulator**
```bash
cd simulator
pip install requests
python generate_data.py
```

**3. Twin model**
```bash
cd twin-model
pip install requests
python twin.py
```

**4. Frontend**
Just open `frontend/index.html` directly in a browser
(or serve it: `cd frontend && python -m http.server 5500`, then visit `http://localhost:5500`).

Once all four are running, the dashboard updates live every 2 seconds.

## API reference (backend)

| Method | Endpoint                | Purpose                             |
|--------|--------------------------|--------------------------------------|
| POST   | `/data`                  | Simulator pushes a new reading       |
| GET    | `/data/latest`           | Latest sensor reading                |
| GET    | `/data/history?limit=50` | Recent readings                      |
| POST   | `/twin/status`           | Twin model pushes computed state     |
| GET    | `/twin/status/latest`    | Latest twin state                    |
| GET    | `/twin/status/history`   | Recent twin states                   |

## Git workflow for the team

```bash
# one-time setup (first person)
git init
git add .
git commit -m "Initial project structure"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main

# everyone else
git clone <your-repo-url>

# each member works in their own branch
git checkout -b feature/<your-part>   # e.g. feature/frontend
git add <files-you-changed>
git commit -m "Describe your change"
git push origin feature/<your-part>
# then open a Pull Request into main on GitHub, or merge directly if short on time

# stay in sync
git pull origin main
```

## Next steps if time allows
- Swap the threshold-based twin logic in `twin-model/twin.py` for a small
  regression or isolation-forest anomaly detector.
- Persist readings in a real database (SQLite/Postgres) instead of in-memory lists.
- Push twin/data updates over WebSockets instead of polling.
- Support multiple `device_id`s at once on the dashboard.
