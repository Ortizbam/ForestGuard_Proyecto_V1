# Puente USB/serial de la estación receptora

Esta carpeta contiene una plantilla de integración; **no es firmware LoRa**. El integrante 2 debe adaptar el firmware del receptor para imprimir un objeto JSON por línea a través del puerto serial USB.

## Formato esperado por línea

```json
{"node_id":"FG-01","temperature_c":24.8,"humidity_pct":40,"smoke_raw":180,"battery_v":3.82,"alert_level":"normal","packet_seq":25,"rssi_dbm":-91,"snr_db":6.5}
```

## Preparación en Windows

En PowerShell, desde la raíz de ForestGuard:

```powershell
py -m pip install requests pyserial
$env:SERIAL_PORT="COM5"
$env:SERIAL_BAUD="115200"
$env:FORESTGUARD_API_URL="http://localhost:8000"
$env:FORESTGUARD_API_KEY="TU_CLAVE_LOCAL"
py gateway/bridge_serial.py
```

Cambia COM5 por el puerto que aparezca en el Administrador de dispositivos. No abras el mismo puerto serial en dos programas a la vez.

## Cola sin conexión

Si no se puede contactar con FastAPI, los paquetes se agregan a `gateway/pending.jsonl`. El puente intenta enviar la cola nuevamente. Para un piloto real hay que diseñar confirmación, deduplicación, límite de tamaño, rotación de archivos, recuperación ante apagados y política de retención.
