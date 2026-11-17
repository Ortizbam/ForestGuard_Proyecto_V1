"""Crea tres nodos y lecturas ficticias de demostración (idempotente)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import SessionLocal, Device, Reading, utc_now

DEMO_DEVICES = [
    ("FG-DEMO-01", "Nodo demostración 01", -13.53195, -71.96746, "Ubicación ficticia; reemplazar"),
    ("FG-DEMO-02", "Nodo demostración 02", -13.52000, -71.95000, "Ubicación ficticia; reemplazar"),
    ("FG-DEMO-03", "Nodo demostración 03", -13.54500, -71.98500, "Ubicación ficticia; reemplazar"),
]

with SessionLocal() as db:
    now = utc_now()
    for node_id, name, lat, lon, note in DEMO_DEVICES:
        device = db.get(Device, node_id)
        if device is None:
            device = Device(id=node_id, name=name, latitude=lat, longitude=lon,
                            location_note=note, last_seen=now, battery_v=3.85,
                            current_state="normal")
            db.add(device)
            db.flush()
            db.add(Reading(node_id=node_id, received_at=now, temperature_c=22.0,
                           humidity_pct=42.0, smoke_raw=180, battery_v=3.85,
                           alert_level="normal", packet_seq=1, rssi_dbm=-88, snr_db=7.5))
    db.commit()
print("Nodos ficticios de demostración preparados.")
print("ATENCIÓN: las coordenadas y mediciones son datos simulados, no instalaciones reales.")
