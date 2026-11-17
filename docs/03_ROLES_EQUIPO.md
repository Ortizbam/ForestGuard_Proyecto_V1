# 03 — Roles, responsabilidades y entregables

## Integrante 1 — Hardware, sensores y energía

**Responsabilidad:** diseño y prueba del nodo sensor.

Entregables:
- Diagrama de conexión y lista final de componentes.
- Firmware que lea sensores y mida batería.
- Registro de unidades, rangos, calibración y limitaciones.
- Presupuesto energético medido y cálculo de panel/batería.
- Mensaje de prueba con los campos definidos en el contrato API.

## Integrante 2 — Telecomunicaciones y estación receptora

**Responsabilidad:** enlace LoRa y estación local.

Entregables:
- Modelo exacto de radio, frecuencia y configuración autorizada.
- Firmware emisor y receptor.
- Formato de paquete y salida JSON por serial.
- Mediciones de alcance, RSSI, SNR, pérdida de paquetes y obstáculos.
- Sirena local y almacenamiento de respaldo probados en entorno seguro.

## Integrante 3 — Backend, base de datos y API

**Responsabilidad:** recepción, validación y persistencia.

Entregables:
- Modelo de tablas y diagrama de base de datos.
- API FastAPI compatible con `docs/02_CONTRATO_API.md`.
- Configuración y respaldo PostgreSQL.
- Logs, sincronización diferida y pruebas de endpoints.
- Gestión de claves y autenticación antes de exposición externa.

## Integrante 4 — Frontend, mapas y documentación DRM

**Responsabilidad:** experiencia web y coordinación documental asignada.

Entregables:
- Dashboard adaptable a escritorio y celular.
- Mapa Leaflet con ubicaciones verificadas.
- Tabla de nodos, estados, alertas, lecturas e historial.
- Integración frontend con endpoints acordados.
- Capturas y evidencias de pruebas.
- Coordinación del documento según las fases DRM indicadas por el docente. Confirmar qué significa DRM y cuál es la plantilla exigida; no asumir un significado sin validación.

## Hitos compartidos

1. Nodo lee sensores.
2. Dos radios intercambian un mensaje.
3. Receptor entrega JSON a una computadora.
4. API acepta el JSON y guarda la lectura.
5. Página muestra la lectura y alerta simulada.
6. Integración con datos de hardware reales.
7. Pruebas documentadas y revisión de límites.
