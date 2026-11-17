# 01 — Arquitectura y alcance

## Propósito

Desarrollar un prototipo académico de monitoreo ambiental con capacidad de comunicar desde una zona sin Internet hacia una estación receptora. La plataforma permite visualizar los datos y registrar eventos cuando el servidor recibe la información.

## Flujo propuesto

1. ESP32 recoge mediciones de sensores.
2. El firmware prepara un paquete con ID de nodo, número de secuencia y mediciones.
3. El módulo LoRa transmite el paquete.
4. El receptor LoRa valida el paquete y lo entrega a una estación local.
5. La estación puede almacenar temporalmente los mensajes sin Internet.
6. Cuando existe conexión, un puente USB/serial o proceso equivalente los envía a FastAPI.
7. FastAPI valida el formato y guarda la medición en PostgreSQL.
8. El frontend consulta la API y representa noPdos, lecturas y alertas.

## Alcance mínimo recomendado

Construir y demostrar primero **un nodo transmisor y una estación receptora** en un entorno autorizado de pruebas. No desplegar varios nodos hasta que el flujo completo funcione y haya sido medido.

## Fuera del alcance del primer prototipo

- No identificar con certeza el inicio de un incendio forestal.
- No reemplazar a brigadas, autoridades ni sistemas oficiales.
- No garantizar cobertura LoRa de una distancia fija antes de medirla.
- No mostrar datos nuevos en un servidor remoto si toda la estación carece de Internet; en ese caso se almacenan localmente y se sincronizan después.

## Componentes lógicos

- Nodo: microcontrolador, sensores, radio, alimentación.
- Receptor: radio compatible, lógica de recepción, alarma local y memoria.
- Gateway: puente entre el receptor y la API.
- Backend: FastAPI y PostgreSQL.
- Frontend: HTML, CSS, JavaScript y Leaflet.
