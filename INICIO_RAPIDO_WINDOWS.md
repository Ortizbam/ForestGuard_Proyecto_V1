# Inicio rápido — Windows + Visual Studio Code

Sigue los pasos en orden. La primera prueba usa dispositivos ficticios; no requiere conectar ESP32 ni LoRa.

## A. Extraer y abrir la carpeta

1. Descarga `ForestGuard_Proyecto.zip`.
2. En Descargas, haz clic derecho y elige **Extraer todo**.
3. Abre Visual Studio Code.
4. Selecciona **Archivo → Abrir carpeta** y elige `ForestGuard_Proyecto`.
5. Abre **Terminal → Nueva terminal**. Comprueba que la ruta de la terminal termina en `ForestGuard_Proyecto`.

## B. Comprobar Docker

En la terminal PowerShell ejecuta uno a uno:

```powershell
docker --version
docker compose version
docker info
```

Si `docker` no se reconoce, instala Docker Desktop para Windows desde el sitio oficial `https://www.docker.com/products/docker-desktop/`. Si ya está instalado pero `docker info` falla, abre Docker Desktop y espera a que inicie. Si Windows solicita WSL 2, sigue el asistente oficial y reinicia cuando lo solicite.

## C. Crear la configuración local

```powershell
Copy-Item .env.example .env
```

Abre `.env` en VS Code y cambia el valor de `FORESTGUARD_API_KEY` por una clave local propia. Usa exactamente esa misma clave cuando ejecutes el simulador.

## D. Levantar API y base de datos

```powershell
docker compose up --build -d
docker compose ps
```

La primera vez Docker necesita descargar las imágenes y construir el servidor. En `docker compose ps` los servicios `api` y `db` deben aparecer ejecutándose (la base de datos debe pasar su comprobación de salud).

Para ver los mensajes del servidor:

```powershell
docker compose logs -f api
```

Presiona `Ctrl + C` para salir de los registros; esto no detiene los contenedores.

## E. Crear dispositivos de demostración

```powershell
docker compose exec api python scripts/seed_demo.py
```

El script registra nodos ficticios y una lectura de muestra. No son instalaciones reales.

## F. Abrir la aplicación

- ForestGuard: `http://localhost:8000`
- Estado de API y base de datos: `http://localhost:8000/api/health`
- Documentación interactiva de API: `http://localhost:8000/docs`

La respuesta de salud debe indicar `status: ok` y `database: connected`.

## G. Simular una lectura y una alerta

Abre una segunda terminal de PowerShell en VS Code, dentro de la misma carpeta:

```powershell
$env:FORESTGUARD_API_KEY="TU_CLAVE_LOCAL"
py -m pip install requests
py scripts/send_demo.py prealert
py scripts/send_demo.py alert
```

Cambia `TU_CLAVE_LOCAL` por la clave que guardaste en `.env`. Vuelve al navegador: el panel consulta los datos cada cinco segundos.

Puedes enviar una lectura normal después:

```powershell
py scripts/send_demo.py normal
```

## H. Detener la aplicación

```powershell
docker compose down
```

Este comando conserva el volumen de PostgreSQL. Para borrar los datos de demostración y reiniciar desde cero:

```powershell
docker compose down -v
docker compose up --build -d
docker compose exec api python scripts/seed_demo.py
```

**Advertencia:** `down -v` elimina permanentemente la base de datos local del proyecto.

## I. Errores habituales

- `Copy-Item` dice que no encuentra `.env.example`: revisa que abriste la carpeta correcta y que la terminal se encuentra en la raíz del proyecto.
- `docker compose` falla: abre Docker Desktop y ejecuta `docker info`.
- Error de puerto: cambia el mapeo `127.0.0.1:8000:8000` en `docker-compose.yml` a `127.0.0.1:8001:8000`; reinicia y usa `http://localhost:8001`.
- Error 401 al simular: la API key del terminal y de `.env` deben coincidir.
- No se ve el mapa: requiere conexión a Internet para descargar Leaflet y las teselas de OpenStreetMap; los demás paneles deben seguir funcionando.
