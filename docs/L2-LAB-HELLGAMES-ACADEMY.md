# L2 Lab, Hellgames y Academy

Separación solicitada por Kevin el 17/10/2026.

| Entorno | Carpeta | Dirección local | Uso |
|---|---|---|---|
| L2 Lab | `E:\l2-local` | 127.0.0.1 | Experimentos, pruebas y herramientas actuales |
| L2 Hellgames | `E:\l2-hellgames` | 127.0.0.2 | Base separada de la futura versión para jugadores |
| L2 Academy | `E:\l2-academy` | 127.0.0.3 | Versión local de un jugador, limitada al Coliseo |

Cada nueva versión tiene copia propia de runtime Java/MariaDB, JAR, contenido, configuración, cliente, base de datos, logs y lanzadores. No hay hardlinks, junctions ni sincronización automática con Lab. Las copias se basan en el estado actual; no representan automáticamente una release pública depurada.

Los puertos son iguales, pero las direcciones de escucha diferentes: login2106, juego7777, enlace19014, DB3307. Las tres direcciones son loopback y no requieren cambiar configuración de red de Windows. El cliente conecta con su dirección correspondiente.

## Uso

En cada nueva carpeta:

- `2-JUGAR.cmd`: inicia sus servicios y su cliente independiente.
- `1-INICIAR.cmd`: solo servicios.
- `5-DETENER.cmd`: detiene sus propios servicios. Pide salir antes si detecta cliente conectado.

Lab conserva `2-JUGAR.cmd` y todos sus accesos existentes. No se renombró ni movió su carpeta. No se alteraron cuentas, personajes ni inventarios existentes.

## Contenido inicial

Hellgames conserva el nacimiento en el muelle pacífico. Solo se habilita el script nuevo HellgamesArrival: `.muelle` y salida `.muelle giran`. Se separó del GludioSky del Lab porque esa carpeta también carga la tripulación experimental de una aeronave. No se encienden automáticamente asaltos de Giran, TV, cámaras, Dust2 o tripulaciones. Los recursos visuales son todavía la copia base del Lab, no un cliente público depurado. El selector de equipo, el servicio VIP y los shops públicos todavía deben implementarse aquí. Decisiones aprobadas y propuesta monetaria en `research/environments/HELLGAMES-DECISIONES-INICIALES.md`.

Academy inicia en `148900,46100,-3400`, carga servicios del Coliseo y el roster/duelos ya disponibles. El controlador AcademyWorld devuelve al personaje al Coliseo si sale del área habilitada. El límite cubre el recinto y sus accesos próximos; no recorta ni borra físicamente los archivos del mundo. Tras una salida por teleport puede existir el intervalo de retorno del controlador (500ms). Se permiten las entidades técnicas del roster, sin contarlas como otros jugadores.

Academy usa login, GameServer y base de datos locales: no se convirtió el ejecutable del cliente en un juego que funcione sin esos servicios. El límite configurado es un jugador conectado. La experiencia single player y su progresión podrán ampliarse sobre esta base. Para preparar rivales se usa `.roster preparar`, después `.roster estado` y `.arena iniciar`. En Academy ese comando está disponible al jugador sin exigir GM. La telemetría conserva el registro de duelos, pero se desactivaron las colas de benchmarks automáticos que dependen de personajes del Lab.

## Separación de datos y publicación

Las bases nuevas se inicializan con los esquemas SQL nativos, sin copiar cuentas ni personajes del Lab. Los scripts Academy pueden crear sus propios perfiles técnicos de rivales al arrancar; son datos de esa base, no personajes traídos del Lab.

Ambos entornos permanecen locales. No se abrieron puertos, cambiaron firewall/router ni conectaron cobros. Antes de una publicación habrá que seleccionar y validar una release de Hellgames; no copiar la carpeta Lab completa encima.

Las configuraciones de DB contienen contraseñas locales nuevas y distintas: no publicarlas ni incluir database/data, logs o credenciales en un repositorio.

## Construcción y pruebas

Preparación reproducible y fuentes del controlador/lanzadores: `research/environments/`. El preparador rechaza sobreescribir una raíz existente. Identidad de la copia y estado en `environment.json` de cada entorno. Los resultados de arranque se registran en `research/environments/VERIFICACION.md` al completarse.
