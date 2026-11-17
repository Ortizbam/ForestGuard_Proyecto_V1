# 02 — Contrato de integración API

El contrato debe acordarse entre los integrantes 2, 3 y 4. No cambien nombres de campos sin coordinar y actualizar este documento.

## Mensaje de telemetría

`POST /api/telemetry`

Encabezado requerido: `X-API-Key: <clave configurada en el servidor>`.

Cuerpo de ejemplo (valores ficticios):

```json
{
  "node_id": "FG-01",
  "temperature_c": 24.8,
  "humidity_pct": 40.0,
  "smoke_raw": 180,
  "battery_v": 3.82,
  "alert_level": "normal",
  "packet_seq": 25,
  "rssi_dbm": -91,
  "snr_db": 6.5
}
```

## Campos

| Campo | Tipo | Descripción |
|---|---|---|
| `node_id` | texto | Identificador registrado del dispositivo. |
| `temperature_c` | número o null | Temperatura en grados Celsius. |
| `humidity_pct` | número o null | Humedad relativa porcentual. |
| `smoke_raw` | entero o null | Lectura cruda del ADC; no equivale a ppm. |
| `battery_v` | número o null | Voltaje medido de batería. |
| `alert_level` | texto | `normal`, `prealert` o `alert`. |
| `packet_seq` | entero o null | Secuencia generada por el nodo. |
| `rssi_dbm` | entero o null | Potencia recibida por radio. |
| `snr_db` | número o null | Relación señal/ruido reportada por el receptor. |

## Endpoints disponibles

| Método | Ruta | Uso |
|---|---|---|
| GET | `/api/health` | Comprueba API y base de datos. |
| GET | `/api/overview` | Totales para el dashboard. |
| GET | `/api/devices` | Lista de dispositivos y estado calculado. |
| GET | `/api/alerts` | Alertas recientes. |
| POST | `/api/alerts/{id}/ack` | Marca una alerta como atendida. |
| GET | `/api/readings` | Lecturas recientes; acepta `node_id` y `limit`. |
| POST | `/api/telemetry` | Recibe telemetría autenticada con API key. |

## Criterios de integración

- El `node_id` debe estar registrado antes de enviar telemetría; si no, la API responde 404.
- La API responde 401 si falta o no coincide la API key.
- La API valida rangos básicos de formato, pero no calibra los sensores.
- Las mediciones deben conservar unidades documentadas.
- `alert_level` debe ser calculado por la lógica acordada y validada; los ejemplos no son umbrales de incendio.
- El backend registra el momento de recepción del servidor. La sincronización de hora de medición del nodo debe acordarse para una siguiente versión.
- El número de secuencia se incluye para facilitar futuras funciones de deduplicación; esta versión todavía no implementa deduplicación por secuencia.
