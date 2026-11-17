# 05 — Seguridad, privacidad y limitaciones

## Alcance de seguridad

Este código está configurado para desarrollo local. El puerto de la API se publica en `127.0.0.1`, no en todas las interfaces de red. Antes de desplegarlo en un servidor accesible desde Internet hace falta una revisión de seguridad.

## Antes de exponerlo externamente

- Sustituir todas las claves y contraseñas de demostración.
- Implementar inicio de sesión, roles y autorización para ver/atender alertas.
- Configurar HTTPS y un proxy inverso seguro.
- Restringir CORS si la API se separa del frontend.
- Proteger secretos con variables de entorno o gestor de secretos.
- Añadir límites de peticiones, auditoría y registros.
- Configurar copias de seguridad de PostgreSQL y pruebas de restauración.
- Revisar retención de datos y privacidad de ubicación.

## Limitaciones funcionales actuales

- No hay autenticación de usuarios para la interfaz ni para el endpoint de marcar alerta como atendida; mantener el sistema local mientras se desarrolla.
- La API requiere una API key para recibir telemetría, pero no implementa deduplicación de paquetes.
- El backend registra la hora de recepción; no conserva todavía una hora fiable de medición del nodo.
- La cola serial es una demostración inicial; requiere confirmación de entrega, control de tamaño, rotación y deduplicación.
- Leaflet y los mosaicos del mapa usan recursos externos; sin Internet el mapa base no aparece en esta versión.
- Las coordenadas y mediciones iniciales son ficticias.
- No hay lógica calibrada para inferir incendios: la API muestra la etiqueta que recibe.
- Un sensor MQ-2 no es por sí solo un detector certificado de incendios forestales.
- La plataforma web remota no puede recibir datos nuevos si toda la estación está desconectada; se sincronizan cuando vuelva el enlace.

## Uso responsable

ForestGuard es un prototipo académico. No reemplaza vigilancia humana, protocolos oficiales, autoridades, brigadas ni sistemas certificados. Toda alerta debe tratarse como indicio que requiere verificación humana.
