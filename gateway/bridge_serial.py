"""Puente USB/serial: JSON recibido del receptor LoRa -> API ForestGuard.
El receptor debe escribir un objeto JSON por línea. Si la API no responde,
los paquetes se guardan en pending.jsonl y se reintentan al reconectar.

Variables: SERIAL_PORT=COM5, SERIAL_BAUD=115200,
FORESTGUARD_API_URL=http://localhost:8000, FORESTGUARD_API_KEY=...
"""
import json
import os
import time
from pathlib import Path

import requests
import serial

PORT = os.getenv("SERIAL_PORT", "COM5")
BAUD = int(os.getenv("SERIAL_BAUD", "115200"))
BASE_URL = os.getenv("FORESTGUARD_API_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("FORESTGUARD_API_KEY", "CAMBIA_ESTA_CLAVE_LOCAL")
PENDING = Path(__file__).with_name("pending.jsonl")


def send_packet(packet: dict) -> bool:
    try:
        response = requests.post(
            BASE_URL + "/api/telemetry",
            json=packet,
            headers={"X-API-Key": API_KEY},
            timeout=8,
        )
        response.raise_for_status()
        print("Paquete enviado:", packet.get("node_id"), response.status_code)
        return True
    except requests.RequestException as exc:
        print("No se pudo enviar; se conservará en cola:", exc)
        return False


def flush_pending() -> None:
    if not PENDING.exists():
        return
    lines = PENDING.read_text(encoding="utf-8").splitlines()
    remaining = []
    for line in lines:
        try:
            packet = json.loads(line)
            if not isinstance(packet, dict):
                continue
        except json.JSONDecodeError:
            print("Se omitió una línea JSON dañada de la cola")
            continue
        if not send_packet(packet):
            remaining.append(line)
    PENDING.write_text("\n".join(remaining) + ("\n" if remaining else ""), encoding="utf-8")


def main() -> None:
    print(f"Abriendo puerto {PORT} a {BAUD} baudios")
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        print("Puente activo. Presiona Ctrl+C para finalizar.")
        while True:
            flush_pending()
            line = ser.readline().decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                packet = json.loads(line)
                if not isinstance(packet, dict):
                    raise ValueError("El mensaje debe ser un objeto JSON")
                required = {"node_id"}
                if not required.issubset(packet):
                    raise ValueError("Falta el campo node_id")
            except (json.JSONDecodeError, ValueError) as exc:
                print("Línea serial ignorada:", exc)
                continue
            if not send_packet(packet):
                with PENDING.open("a", encoding="utf-8") as file:
                    file.write(json.dumps(packet, ensure_ascii=False) + "\n")
            time.sleep(0.05)


if __name__ == "__main__":
    main()
