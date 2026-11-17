# 04 — Plan de pruebas y criterios de aceptación

Todas las pruebas físicas deben realizarse en un ambiente controlado, con autorización y sin provocar incendios ni quemas.

## Pruebas de software

| Prueba | Procedimiento | Resultado esperado |
|---|---|---|
| Servicio | Consultar `/api/health` | `status=ok`, `database=connected`. |
| Carga inicial | Ejecutar `scripts/seed_demo.py` | Aparecen tres nodos ficticios. |
| Telemetría normal | Enviar `normal` | Se registra una lectura. |
| Prealerta | Enviar `prealert` | Se registra lectura y alerta al cambiar de estado. |
| Alerta | Enviar `alert` | Se registra lectura y evento de posible incendio. |
| Nodo no registrado | Enviar ID desconocido | API responde 404. |
| Clave inválida | Enviar sin API key válida | API responde 401. |
| Sin Leaflet o Internet | Abrir interfaz sin CDN | El mapa muestra aviso; los paneles no deben romperse. |

## Pruebas de integración

- Receptor entrega un JSON válido al gateway.
- Gateway entrega la telemetría a FastAPI.
- La lectura aparece en `/api/readings`.
- El dashboard refleja cambios sin recargar manualmente.
- Al perder Internet, la estación conserva mensajes pendientes.
- Al recuperar Internet, se sincronizan y se comprueba que no haya duplicaciones (la deduplicación es trabajo pendiente de la siguiente versión).

## Pruebas de hardware y radio

- Comparar lectura del sensor con instrumento de referencia apropiado.
- Registrar voltaje y consumo en diferentes modos de funcionamiento.
- Medir alcance en ubicaciones controladas y autorizadas; no prometer una distancia antes de medirla.
- Registrar porcentaje de paquetes recibidos, RSSI y SNR.
- Comprobar recuperación tras pérdida de alimentación y reconexión.
- No realizar pruebas con fuego abierto ni generar humo peligroso.

## Evidencias

Guardar fecha, configuración, condiciones, capturas, archivos de log, resultados y limitaciones. Separar datos simulados de datos reales.
