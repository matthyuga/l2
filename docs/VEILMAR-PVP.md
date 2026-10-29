# Agite en Veilmar

Instalación local: 12/10/2026. Los paquetes originales están en E:/l2; el servidor tiene geodata generada, 26 puertas y una sala PvP compartida bajo demanda (plantilla 3052). No se necesita otro cliente ni otra cuenta. La galería 3D continúa disponible.

## Jugar

1. Abre **2-JUGAR.cmd** y entra con tu personaje equipado y buffeado. El launcher espera que termine de prepararse el laboratorio.
2. Escribe **.veilmar**: llegas a la superficie dentro de una instancia compartida de combate libre. Conservas equipo y build; se restauran HP/CP/MP y se aplica Noblesse.
3. Como GM, escribe **.veilmar agite** para activar nueve combatientes de las mismas plantillas de la sala Elven. Usan su IA y habilidades normales, pelean entre ellos y contra jugadores, y reaparecen cada 20 segundos. No son los once pilotos Player del evento .agite del Coliseo.
4. Si eres GM, desactiva la invulnerabilidad con el control habitual para poder recibir daño. **.veilmar calma** detiene los nueve combatientes. También desaparecen al quedar la sala sin jugadores conectados.
5. **.veilmar revivir** te devuelve a la entrada si moriste. **.veilmar volver** regresa al lugar desde el que entraste; espera a salir del combate.

Para un duelo usa **.ia mago** o **.ia fisico** en lugar del agite grupal: invoca el piloto existente cerca de ti, con 20 segundos de preparación. **.ia cancelar** termina esa prueba. Conviene cancelar el duelo antes de cambiar de zona.

Otros accesos: **.veilmar interior**, **.veilmar interior2**, **.veilmar superficie**, **.veilmar estado**. Viajar requiere estar vivo, fuera de combate y sin otro teleport pendiente; si estás en otra instancia primero debes salir de ella. El agite de nueve combatientes se inicia en la superficie. Otros jugadores que escriban .veilmar entran a la misma sala; también necesitan los paquetes del cliente.

## Qué está preparado y qué falta revisar

Los originales del autor se instalaron en maps, animations, staticmeshes, textures y sounds. El mapa ocupa 17_24; tres accesos permiten inspeccionar superficie e interiores. Las puertas usan los IDs originales, polígonos del autor y alturas derivadas de sus mallas; están abiertas para esta prueba.

La geodata del autor no estaba incluida. Se generó una versión local desde terreno, mallas con colisión, BSP y BlockingVolume usando [L2 Geodata Toolkit](https://github.com/StylerHub/l2-geodata-toolkit), con revisión fijada en research/veilmar/installation.json. Se procesaron 955.459 triángulos de mallas con colisión, con cero actores requeridos omitidos. El archivo generado mide 10.964.704 bytes e incluye múltiples alturas para interiores.

Las comprobaciones del servidor cubren pisos de los tres destinos, zona PvP, summons, puertas, recorrido de entrada, un obstáculo interior, daño de un ataque PvP nativo y aparición/limpieza del grupo. No equivalen a revisar cada escalera, puerta o rincón. La primera entrada visual con este cliente Interlude y el recorrido de las estructuras quedan por comprobar jugando; no se ha afirmado compatibilidad visual por haber exportado el mapa al visor.

## Respaldo

research/veilmar/installation.json indica la carpeta backups/veilmar-ingame-* con el mapa anterior, archivos del servidor y hashes de cada cambio. research/veilmar/Restore-Veilmar.ps1 permite restaurar esos archivos cuando cliente y GameServer estén cerrados; aborta si algún archivo cambió después de esta instalación. No se modificaron builds, cuentas, equipo ni estadísticas de los personajes del usuario.
