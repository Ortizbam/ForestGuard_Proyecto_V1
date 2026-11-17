"""Envía una lectura simulada. Uso: python scripts/send_demo.py normal|prealert|alert"""
import os
import sys
from pathlib import Path

import requests

level = sys.argv[1] if len(sys.argv) > 1 else "alert"
if level not in {"normal", "prealert", "alert"}:
    raise SystemExit("Estado no válido. Usa normal, prealert o alert.")

base_url = os.getenv("FORESTGUARD_API_URL", "http://localhost:8000").rstrip("/")
api_key = os.getenv("FORESTGUARD_API_KEY", "CAMBIA_ESTA_CLAVE_LOCAL")
payload = {
    "node_id": "FG-DEMO-01",
    "temperature_c": 24.8 if level == "normal" else 31.2,
    "humidity_pct": 40.0 if level == "normal" else 25.0,
    "smoke_raw": 180 if level == "normal" else 650,
    "battery_v": 3.82,
    "alert_level": level,
    "packet_seq": 2,
    "rssi_dbm": -91,
    "snr_db": 6.5,
}

try:
    response = requests.post(
        base_url + "/api/telemetry",
        json=payload,
        headers={"X-API-Key": api_key},
        timeout=10,
    )
    print(f"HTTP {response.status_code}: {response.text}")
    response.raise_for_status()
except requests.RequestException as exc:
    raise SystemExit(f"No se pudo enviar la lectura: {exc}")
