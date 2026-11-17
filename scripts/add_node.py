"""Registra o actualiza un nodo con coordenadas verificadas.
Ejemplo desde la raíz: python scripts/add_node.py FG-01 "Nodo piloto 01" -13.52 -71.97 "Sector autorizado"
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import SessionLocal, Device

parser = argparse.ArgumentParser(description="Registrar un nodo ForestGuard")
parser.add_argument("node_id", help="ID único, por ejemplo FG-01")
parser.add_argument("name", help="Nombre visible del nodo")
parser.add_argument("latitude", type=float, help="Latitud decimal")
parser.add_argument("longitude", type=float, help="Longitud decimal")
parser.add_argument("location_note", nargs="?", default="", help="Referencia del lugar")
args = parser.parse_args()
if not (-90 <= args.latitude <= 90 and -180 <= args.longitude <= 180):
    raise SystemExit("Coordenadas fuera de rango")

with SessionLocal() as db:
    device = db.get(Device, args.node_id)
    if device is None:
        device = Device(id=args.node_id, name=args.name, latitude=args.latitude,
                        longitude=args.longitude, location_note=args.location_note,
                        current_state="unknown")
        db.add(device)
    else:
        device.name = args.name
        device.latitude = args.latitude
        device.longitude = args.longitude
        device.location_note = args.location_note
    db.commit()
print(f"Nodo {args.node_id} registrado/actualizado.")
print("Verifica que el nombre y las coordenadas correspondan a una ubicación real autorizada.")
