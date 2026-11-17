# ForestGuard — proyecto inicial de monitoreo forestal

**Versión:** 0.2.0 · **Idioma:** español · **Estado:** prototipo académico para desarrollo y pruebas controladas.

ForestGuard es una propuesta de sistema distribuido para monitorear condiciones ambientales y comunicar posibles alertas desde zonas rurales o montañosas. El nodo instalado en el cerro no necesita Internet: transmite por LoRa a una estación receptora. La estación puede almacenar mensajes localmente y, cuando dispone de Internet, enviarlos al servidor y a la plataforma web.

> **Importante:** este paquete es una base de software para un prototipo académico. No es un sistema certificado de detección de incendios ni debe utilizarse como único medio de seguridad o respuesta ante emergencias. Los sensores deben calibrarse y validarse en pruebas controladas.

## 1. Qué contiene esta carpeta

```text
ForestGuard_Proyecto/
├── README_ES.md                 # Guía general
├── INICIO_RAPIDO_WINDOWS.md     # Pasos en Windows y VS Code
├── main.py                      # API FastAPI y modelos de datos
├── requirements.txt             # Dependencias Python
├── Dockerfile                   # Imagen del servidor
├── docker-compose.yml           # API + PostgreSQL
├── .env.example                 # Configuración de ejemplo
├── .gitignore
├── static/
│   ├── index.html               # Interfaz web
│   ├── styles.css               # Diseño adaptable
│   ├── app.js                   # Mapa y conexión con la API
│   └── logo.svg
├── scripts/
│   ├── seed_demo.py             # Crea nodos ficticios
│   ├── send_demo.py             # Envía lecturas simuladas
│   └── add_node.py              # Registra un nodo y coordenadas
├── gateway/
│   ├── bridge_serial.py         # Puente USB/serial → API
│   └── README_PUENTE.md
├── docs/
│   ├── 01_ARQUITECTURA.md
│   ├── 02_CONTRATO_API.md
│   ├── 03_ROLES_EQUIPO.md
│   ├── 04_PLAN_DE_PRUEBAS.md
│   └── 05_SEGURIDAD_Y_LIMITACIONES.md
└── .vscode/
    ├── extensions.json
    └── tasks.json
```

## 2. Arquitectura del sistema

```text
ESP32 + sensores
      │
      │ LoRa (sin Internet en el cerro)
      ▼
Receptor LoRa / estación local
      │
      ├── guarda mensajes si no hay conexión
      │
      └── USB-serial hacia una computadora o Raspberry Pi
                         │
                         ▼
                 Puente de comunicación
                         │ Internet disponible
                         ▼
                    FastAPI
                         │
                         ▼
                    PostgreSQL
                         │
                         ▼
                ForestGuard Web
```

La página web no recibe la señal de radio directamente. La estación receptora debe entregar los mensajes a la API. El archivo `gateway/bridge_serial.py` es una plantilla para el caso en que el receptor envíe un JSON por línea a través de USB-serial.

## 3. Requisitos para ejecutar en Windows

- Windows 10/11 de 64 bits.
- Visual Studio Code.
- Docker Desktop con Docker Compose (recomendado para iniciar el paquete completo).
- Un navegador actualizado.
- Conexión a Internet durante la primera descarga de imágenes de Docker y para cargar los mapas base de OpenStreetMap y la biblioteca Leaflet desde CDN.

No necesitas tener los sensores físicos para probar la web: el paquete incluye nodos y lecturas de demostración.

## 4. Inicio rápido

Consulta `INICIO_RAPIDO_WINDOWS.md`. Resumen de comandos, desde la terminal de VS Code abierta en esta carpeta:

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

Abre `.env` y cambia `FORESTGUARD_API_KEY` por una clave local propia. Después ejecuta:

```powershell
docker compose up --build -d
docker compose exec api python scripts/seed_demo.py
```

Abre en el navegador:

- Página: http://localhost:8000
- Salud de API y base de datos: http://localhost:8000/api/health
- Documentación interactiva: http://localhost:8000/docs

Para simular una alerta, en otra terminal de PowerShell:

```powershell
$env:FORESTGUARD_API_KEY="TU_CLAVE_LOCAL"
py -m pip install requests
py scripts/send_demo.py prealert
py scripts/send_demo.py alert
py scripts/send_demo.py normal
```

Sustituye `TU_CLAVE_LOCAL` por el mismo valor que guardaste en `.env`.

Para detener los contenedores sin borrar los datos:

```powershell
docker compose down
```

Para detenerlos y eliminar también la base de datos local de demostración:

```powershell
docker compose down -v
```

## 5. Funciones incluidas

- Dashboard con cantidad de nodos, nodos en línea, nodos sin comunicación y alertas pendientes.
- Mapa Leaflet con marcadores por dispositivo y colores según estado.
- Tabla de dispositivos, batería y último mensaje.
- Listado de alertas recientes con acción para marcarlas como atendidas.
- Vista de última medición recibida.
- Actualización periódica de la interfaz cada cinco segundos.
- API FastAPI con endpoints para telemetría, dispositivos, alertas, lecturas y resumen.
- Persistencia de datos en PostgreSQL dentro de Docker.
- Nodos ficticios para pruebas y script de envío de lecturas simuladas.
- Plantilla opcional de puente USB-serial con cola de mensajes pendientes cuando no se puede contactar con el servidor.

## 6. Estados de ejemplo

- `normal`: no hay una condición que el algoritmo de prueba haya clasificado como alerta.
- `prealert`: condiciones ambientales que requieren atención según criterios que deberán definirse y validarse.
- `alert`: posible evento que requiere verificación humana.
- `offline`: estado calculado por el servidor cuando no llegan mensajes dentro del periodo configurado.

Estos estados son etiquetas de software. Los umbrales no están calibrados ni deben inferirse a partir de las mediciones ficticias.

## 7. Integración con el equipo

- Integrante 1: entrega lecturas del ESP32 y mediciones de sensores con unidades y calibración documentadas.
- Integrante 2: entrega paquetes LoRa recibidos y el formato JSON que el receptor imprime por serial.
- Integrante 3: mantiene FastAPI, PostgreSQL y el contrato de API.
- Integrante 4: mantiene frontend, mapa, dashboard, alertas, usabilidad y evidencias de pruebas.

El formato de mensaje se documenta en `docs/02_CONTRATO_API.md` y las tareas por integrante en `docs/03_ROLES_EQUIPO.md`.

## 8. Ubicaciones de demostración

`seed_demo.py` crea tres nodos con coordenadas ilustrativas en el área de Cusco. **No representan instalaciones reales.** Antes de una demostración de campo, regístrense únicamente las coordenadas de los lugares realmente inspeccionados y autorizados.

Ejemplo para registrar un nodo real, desde la raíz del proyecto:

```powershell
docker compose exec api python scripts/add_node.py FG-01 "Nodo piloto 01" -13.52 -71.97 "Sector autorizado de prueba"
```

Las coordenadas del ejemplo son ficticias; reemplázalas por las medidas del lugar real.

## 9. Solución de problemas

**`docker` no se reconoce:** instala Docker Desktop, cierra y abre VS Code, luego vuelve a probar `docker --version`.

**Docker no puede conectarse al daemon:** abre Docker Desktop y espera a que indique que está en ejecución.

**El puerto 8000 está ocupado:** cierra la aplicación que lo utiliza o cambia el puerto de la izquierda en `docker-compose.yml` (por ejemplo `127.0.0.1:8001:8000`) y abre `http://localhost:8001`.

**No aparecen los mapas:** Leaflet y el mapa base requieren conexión a Internet en esta versión. El resto del panel puede cargar aunque el mapa no esté disponible.

**La API devuelve 401:** comprueba que el encabezado `X-API-Key` use el mismo valor que `FORESTGUARD_API_KEY` en `.env`.

**El nodo devuelve 404:** primero registra el `node_id` en la base de datos con `scripts/add_node.py` o utiliza los nodos creados por `seed_demo.py`.

**No aparece una alerta nueva:** el backend crea alertas cuando el estado cambia a `prealert` o `alert`. Envía primero `normal` y después `alert`, o usa un nodo en estado normal.

## 10. Qué falta antes de un piloto real

- Validar la configuración de radiofrecuencia y los módulos permitidos para Perú.
- Definir y probar la ubicación de la estación receptora y la cobertura LoRa en el terreno.
- Calibrar y seleccionar sensores apropiados; MQ-2 no es un detector certificado de incendios forestales.
- Diseñar el ahorro de energía y dimensionar panel, batería y control de carga mediante mediciones de consumo.
- Incorporar autenticación de usuarios y autorización antes de exponer la web a Internet.
- Añadir deduplicación y confirmación de entrega a los paquetes retransmitidos.
- Añadir sincronización horaria, copias de seguridad, registros y supervisión del servidor.
- Ejecutar pruebas de pérdida de radio, batería, clima, falsas alarmas y recuperación de Internet.
- Validar el prototipo con responsables y autoridades locales; no presentarlo como sistema operativo de emergencia.

