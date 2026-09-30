"""Single data-access facade every screen imports from.

DEMO_MODE toggles between the synthetic simulator and the real ESP32
gateway path (dashboard_state.json / brave_live.csv written by a serial
bridge script, same contract as the BRAVE 2.0 gateway). Screens never
import data.simulator directly, so flipping this flag is the only change
needed to go live with real hardware.
"""

import json
import time
from pathlib import Path

import pandas as pd

import config
from data import simulator

DEMO_MODE = True

_STATE_PATH = Path(config.STATE_FILE)
_CSV_PATH = Path(config.CSV_FILE)


def _read_real_state(max_age_s=5.0):
    try:
        raw = json.loads(_STATE_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"connected": False, "demo_mode": False, "data_source": "No signal from gateway"}

    age = time.time() - raw.get("gateway_time", 0)
    connected = age <= max_age_s
    return {
        "timestamp": raw.get("pc_time"),
        "connected": connected,
        "demo_mode": False,
        "data_source": "ESP32 gateway" if connected else "Gateway offline",
        "mpu6050_ok": raw.get("mpu6050_ok", False),
        "temp_ok": raw.get("temp_ok", False),
        "oled_ok": raw.get("oled_ok", False),
        "vibration_mm_s": raw.get("vibration_rms"),
        "temperature_c": raw.get("temperature_c"),
        "rpm": raw.get("rpm"),
        "position_mm": raw.get("position_mm"),
        "trend_pct": {},
        "health_score": raw.get("health_score"),
        "risk_index": raw.get("risk_index"),
        "status": raw.get("status", "WAITING"),
        "top_cause": raw.get("top_cause", "NONE"),
        "active_joint": f"J-{raw.get('zone', 1):02d}",
        "active_zone": f"Z-{raw.get('zone', 1):02d}",
    }


def _read_real_history(rows=600):
    try:
        df = pd.read_csv(_CSV_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()
    return df.tail(rows)


def get_live_state():
    if DEMO_MODE:
        return simulator.get_live_state()
    return _read_real_state()


def get_history(minutes=60, points=60):
    if DEMO_MODE:
        return simulator.get_history(minutes=minutes, points=points)
    return _read_real_history()


def get_belt_health_trend(hours=24, points=48):
    return simulator.get_belt_health_trend(hours=hours, points=points)


def get_joints():
    return simulator.get_joints()


def get_joint_signature(joint_id=None):
    return simulator.get_joint_signature(joint_id)


def get_anomaly_trend(minutes=60, points=60):
    return simulator.get_anomaly_trend(minutes=minutes, points=points)


def get_current_anomaly():
    return simulator.get_current_anomaly()


def get_recent_anomalies():
    return simulator.get_recent_anomalies()


def get_fault_location():
    return simulator.get_fault_location()


def get_predictive():
    return simulator.get_predictive()


def get_alerts():
    return simulator.get_alerts()


def get_sensor_network():
    return simulator.get_sensor_network()


def get_live_stream(rows=6):
    return simulator.get_live_stream(rows=rows)
