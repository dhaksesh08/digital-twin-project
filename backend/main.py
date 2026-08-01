"""
Digital Twin Backend
---------------------
Owned by: Member B

Responsibilities:
- Ingest sensor readings from the simulator (POST /data)
- Store recent history in memory (swap for a DB later if needed)
- Expose readings to the twin model and frontend (GET endpoints)
- Accept twin model output (POST /twin/status) and expose it (GET /twin/status)

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Digital Twin Backend")

# Allow the frontend (served from a different port/file) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Shared data schema. Agree on this as a team BEFORE building further. ----
class SensorReading(BaseModel):
    timestamp: str
    device_id: str
    temperature: float
    vibration: float
    speed: float


class TwinStatus(BaseModel):
    timestamp: str
    device_id: str
    predicted_temperature: float
    predicted_vibration: float
    predicted_speed: float
    status: str          # "normal" | "warning" | "critical"
    anomaly_reason: Optional[str] = None


# ---- In-memory stores (fine for a one-day demo) ----
readings: List[SensorReading] = []
twin_states: List[TwinStatus] = []
MAX_HISTORY = 200  # keep memory bounded


@app.get("/")
def root():
    return {"message": "Digital Twin backend is running"}


# ---- Real sensor data (from simulator) ----
@app.post("/data")
def ingest_data(reading: SensorReading):
    readings.append(reading)
    if len(readings) > MAX_HISTORY:
        readings.pop(0)
    return {"status": "ok", "stored": reading}


@app.get("/data/latest", response_model=Optional[SensorReading])
def get_latest_reading():
    return readings[-1] if readings else None


@app.get("/data/history", response_model=List[SensorReading])
def get_history(limit: int = 50):
    return readings[-limit:]


# ---- Twin model output ----
@app.post("/twin/status")
def post_twin_status(status: TwinStatus):
    twin_states.append(status)
    if len(twin_states) > MAX_HISTORY:
        twin_states.pop(0)
    return {"status": "ok", "stored": status}


@app.get("/twin/status/latest", response_model=Optional[TwinStatus])
def get_latest_twin_status():
    return twin_states[-1] if twin_states else None


@app.get("/twin/status/history", response_model=List[TwinStatus])
def get_twin_history(limit: int = 50):
    return twin_states[-limit:]
