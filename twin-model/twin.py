"""
Digital Twin Model
--------------------
Owned by: Member C

Pulls the latest sensor reading from the backend, computes a "twin" state
(a simple rolling-average prediction) and flags anomalies using threshold
rules, then pushes that twin status back to the backend.

This is intentionally simple (rule-based) so it's buildable in a day.
If time allows, swap the rule-based check for a small regression /
isolation-forest model.

Run:
    pip install requests
    python twin.py
"""

import time
import requests
from collections import deque
from datetime import datetime, timezone

BACKEND_URL = "http://localhost:8000"
POLL_INTERVAL = 2
WINDOW_SIZE = 10  # rolling window for the "predicted" (mirrored) state

# Thresholds — tune these to your actual device/domain
TEMP_WARNING = 85
TEMP_CRITICAL = 95
VIBRATION_WARNING = 1.0
VIBRATION_CRITICAL = 2.0

history = {
    "temperature": deque(maxlen=WINDOW_SIZE),
    "vibration": deque(maxlen=WINDOW_SIZE),
    "speed": deque(maxlen=WINDOW_SIZE),
}


def get_latest_reading():
    try:
        resp = requests.get(f"{BACKEND_URL}/data/latest", timeout=3)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return None


def compute_twin_state(reading):
    history["temperature"].append(reading["temperature"])
    history["vibration"].append(reading["vibration"])
    history["speed"].append(reading["speed"])

    predicted_temp = sum(history["temperature"]) / len(history["temperature"])
    predicted_vibration = sum(history["vibration"]) / len(history["vibration"])
    predicted_speed = sum(history["speed"]) / len(history["speed"])

    status = "normal"
    reason = None

    if reading["temperature"] >= TEMP_CRITICAL or reading["vibration"] >= VIBRATION_CRITICAL:
        status = "critical"
        reason = "Temperature or vibration exceeded critical threshold"
    elif reading["temperature"] >= TEMP_WARNING or reading["vibration"] >= VIBRATION_WARNING:
        status = "warning"
        reason = "Temperature or vibration exceeded warning threshold"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device_id": reading["device_id"],
        "predicted_temperature": round(predicted_temp, 2),
        "predicted_vibration": round(predicted_vibration, 2),
        "predicted_speed": round(predicted_speed, 2),
        "status": status,
        "anomaly_reason": reason,
    }


def push_twin_status(twin_status):
    try:
        resp = requests.post(f"{BACKEND_URL}/twin/status", json=twin_status, timeout=3)
        print(f"Twin status: {twin_status['status']:<9} -> pushed ({resp.status_code})")
    except requests.exceptions.RequestException:
        print("Could not push twin status. Is the backend running?")


def run():
    print("Starting twin model loop. Ctrl+C to stop.")
    while True:
        reading = get_latest_reading()
        if reading:
            twin_status = compute_twin_state(reading)
            push_twin_status(twin_status)
        else:
            print("No reading available yet...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run()
