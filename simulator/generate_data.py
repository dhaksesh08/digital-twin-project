"""
Sensor Data Simulator
----------------------
Owned by: Member A

Generates fake sensor readings and posts them to the backend every N seconds.
Replace random.uniform(...) calls with real sensor reads later if you get
actual hardware/IoT data.

Run:
    pip install requests
    python generate_data.py
"""

import time
import random
import requests
from datetime import datetime, timezone

BACKEND_URL = "http://localhost:8000/data"
DEVICE_ID = "machine-01"
INTERVAL_SECONDS = 2

# Occasionally simulate an anomaly spike so the twin model has something to catch
ANOMALY_CHANCE = 0.1


def generate_reading():
    is_anomaly = random.random() < ANOMALY_CHANCE

    temperature = random.uniform(60, 75) if not is_anomaly else random.uniform(90, 110)
    vibration = random.uniform(0.1, 0.5) if not is_anomaly else random.uniform(1.5, 3.0)
    speed = random.uniform(1400, 1600)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": DEVICE_ID,
        "temperature": round(temperature, 2),
        "vibration": round(vibration, 2),
        "speed": round(speed, 2),
    }


def run():
    print(f"Starting simulator -> {BACKEND_URL} every {INTERVAL_SECONDS}s. Ctrl+C to stop.")
    while True:
        reading = generate_reading()
        try:
            resp = requests.post(BACKEND_URL, json=reading, timeout=3)
            print(f"Sent: {reading}  -> status {resp.status_code}")
        except requests.exceptions.ConnectionError:
            print("Backend not reachable. Is it running on port 8000?")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
