# Biblioteca de cielos, clima, VFX y audio para L2

Solicitud de Kevin: descargar todos los recursos de la lista de la conversación del 21/10/2026.
Ruta: `E:\l2-local\research\atmosphere-library`.

Completado y verificado al entregar: seis ZIP pequeños y los 118 archivos de los 59 cielos de Poly Haven (1,36 GB). Sonniss continúa en segundo plano; Freesound queda pendiente de login. Consultar los registros de avance para el estado posterior.

## Estado y controles

- `ESTADO.cmd`: muestra progreso real, archivos terminados y errores.
- `PAUSAR.cmd`: detiene únicamente el gestor de esta carpeta y sus dos trabajadores; conserva `.part`.
- `REANUDAR.cmd`: continúa las descargas pendientes. No ejecutar otros descargadores de esta carpeta simultáneamente.
- `progress.json` y `polyhaven-progress.json`: progreso persistido. Un archivo sólo está terminado cuando figura `complete` y tiene su `.source.json`.
- `download.log` y `polyhaven.log`: registros. `run.json`: PID del gestor y trabajadores.

El gestor continúa en segundo plano mientras la PC permanezca encendida y conectada. No se inicia automáticamente al reiniciar Windows; para continuar después, usar `REANUDAR.cmd`.

## Contenido solicitado

| Carpeta | Contenido | Fuente | Licencia |
|---|---|---|---|
| cloudy | Dos ZIP: los mismos 25 cielos en cubemap y panorama | https://opengameart.org/content/cloudy-skyboxes-0 | CC0 |
| kenney-sky | Pack Skyboxes completo | https://kenney.nl/assets/skyboxes | CC0 |
| kenney-particles | Pack Particle Pack completo | https://kenney.nl/assets/particle-pack | CC0 |
| kenney-smoke | Pack Smoke Particles completo | https://kenney.nl/assets/smoke-particles | CC0 |
| spritepilot | Weather & Ambient completo, estilo pixel art | https://spritepilot.com/free-game-assets/weather | CC0 según proveedor |
| polyhaven | Todos los 59 cielos de Pure Skies del catálogo consultado, HDR 2K y JPG tonemapped original | https://polyhaven.com/hdris/pure-skies | CC0 |
| sonniss | 78 ZIP: archivo GDC 2015–2024 y bundle 2026, sin duplicar espejos | https://sonniss.com/gameaudiogdc/ y https://gdc.sonniss.com/ | Sonniss GDC Bundle |
| freesound | **Pendiente: originales requieren cuenta/inicio de sesión** | https://freesound.org/people/IllusiaProductions/packs/15337/ | Revisar cada sonido antes de usar |

Sonniss comprende bibliotecas generales de sonido, no únicamente clima. El archivo publicado ronda los 215 GB contando 2026; es la parte de larga duración. Se conservan comprimidos y se genera una lista de contenido por ZIP para poder localizar sonidos después. No se descargan productos pagos ni duplicados de cada espejo. En Poly Haven se cubre cada cielo de la categoría elegida, no todas las resoluciones y formatos repetidos. Powered by Poly Haven: metadatos obtenidos mediante su API pública.

Los seis ZIP pequeños se extraen en su subcarpeta `extracted`. Los HDR/JPG conservan metadatos y checksums originales. Todos los ZIP descargados se verifican con CRC; cada descarga terminada registra SHA-256 y procedencia en `.source.json`. Los archivos de Poly Haven también se contrastan con el MD5 publicado por el proveedor.

## Freesound pendiente

El enlace oficial de descarga redirigió al formulario de inicio de sesión. Se conserva esa respuesta en `sources/freesound-download-response.html`; no contiene audio. No se descargó un HTML como si fuera el pack. Los WAV originales de Rain and Thunder quedan pendientes de una sesión autorizada en Freesound. Descargar el ZIP oficial dentro de `freesound` cuando esté disponible.

## Uso en el proyecto

Estos recursos están descargándose como biblioteca fuente. No se instalaron en el cliente ni se ha comprobado compatibilidad visual dentro de Interlude. Los cielos requieren conversión/importación; los gráficos de partículas requieren emisores, y los sonidos requieren preparación para el cliente.

Las páginas fuente y licencias consultadas se conservan en `sources`. Para Sonniss, el texto publicado en su web al descargar prevalece sobre licencias antiguas incluidas en los ZIP. Uso en proyectos permitido bajo esa licencia; no publicar los sonidos como biblioteca independiente. No subir los binarios de esta biblioteca al repositorio público.
