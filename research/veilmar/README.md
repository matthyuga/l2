# Veilmar y santuario del Monarca del Amanecer

Actualización: 12/10/2026. El usuario descargó el paquete; ya está extraído y preparado en la galería 3D. Reemplaza el estado anterior de descarga bloqueada.

Actualización posterior: integrado en el cliente E:/l2 y en el GameServer local, con respaldo, geodata generada, 26 puertas abiertas y sala PvP compartida bajo demanda. Acceso .veilmar; grupo opcional de nueve combatientes con .veilmar agite, detener con .veilmar calma. [Guía para jugar y límites de la prueba](../../VEILMAR-PVP.md). La primera inspección visual desde el cliente queda pendiente; las comprobaciones del servidor se registran en ingame-verification.json.

## Abrir en el visor

- [Superficie: fortaleza y santuario](http://127.0.0.1:32280/?model=veilmar_surface&view=3d): 941 actores estáticos y relieve original.
- [Salas subterráneas](http://127.0.0.1:32280/?model=veilmar_underground&view=3d): 466 actores; aparecen dos grupos de interiores del mismo mapa.

La galería se inicia con E:/l2-local/GALERIA-MODELOS-L2.cmd. Ambas vistas cargaron en WebGL; también se comprobó el montaje anterior de Gracia tras ajustar el encuadre.

## Procedencia y recuperación

- [Publicación de deMEV](https://maxcheaters.com/topic/254429-veilmar-fortress-sanctuary-of-the-dawn-monarch-for-all-l2-c/).
- [Sitio del autor](https://aden-territory.com/free-shared-maps-and-maps-for-sale/559-veilmar-fortress-sanctuary-of-the-dawn-monarch-for-all-l2-clients.html).
- [Descarga publicada](https://workupload.com/file/vc8SNBNGzbt).
- [Video del autor](https://www.youtube.com/watch?v=4zzAyEYF8fE).

RAR local: E:/l2-local/descarga de assets/Veilmar Fortress, Sanctuary of the Dawn Monarch.rar. Tamaño: 99.735.612 bytes. SHA256: de305fda099ad9bb2e97fb832e278e192b78d78e2f98bd91412e5455525da688; coincide con el publicado en la captura del usuario. UnRAR comprobó su integridad antes de extraer.

Contenido aislado en assets/: 17_24.unr, Veilmar_S.usx, Veilmar_T.utx, Veilmar_A.ukx, Veilmar_SND.uax, readme.txt, TP Data.txt y doors info raw data.txt. No se reemplazaron archivos del juego.

## Reconstrucción y límites

Se recuperaron las 233 mallas referidas por los 1.407 actores estáticos, con posiciones, rotaciones y escalas del mapa. El relieve usa el heightmap original de 16 bits, sus huecos y diagonales; las 11 capas de terreno se compusieron en una textura para el visor.

Esta es una vista de arquitectura. No reproduce el agua, partículas, iluminación, sonidos, NPCs ni puertas animadas del cliente. Algunos materiales especiales usan aproximaciones o carecen de textura; material-fallback-audit.json documenta las sustituciones. Cero mallas estáticas referidas quedaron sin exportar; eso no significa que todos los objetos y efectos del mapa estén incluidos.

Se conservan originales, escenas Blender y scripts de preparación. actors.json, scene-meshes.json y *-assembly-audit.json registran el montaje. verification.json comprueba archivo original, cobertura, dependencias y carga WebGL. Los glTF están en ../model-catalog/exports/scene-veilmar_surface y scene-veilmar_underground.

## Territorio y conexiones

El paquete contiene un único mapa 17_24, con superficie y espacios por debajo. Las dos entradas de galería permiten inspeccionarlos sin que el terreno oculte los interiores; no son mapas independientes ni instancias del servidor. La selección para interiores usa actores a Z≤-5000.

TP Data.txt propone estos destinos:

| Área | X | Y | Z |
| --- | ---: | ---: | ---: |
| Superficie | -78552 | 212264 | -2592 |
| Interior 1 | -86840 | 201512 | -7664 |
| Interior 2 | -93640 | 211000 | -7952 |

World.java de nuestro source define casillas de 32.768 unidades, origen de grilla X=20,Y=18 y rango X=16..26,Y=10..25. La casilla 17_24 ya entra en esos límites: X=[-98304,-65536), Y=[196608,229376). El cliente actual E:/l2/MAPS/17_24.unr carece de StaticMeshActor, según local-territory-audit.json, y no fue modificado. Las coordenadas no garantizan por sí mismas navegación o desembarco.

InstanceManager.java contiene createDynamicInstance(int templateId) y soporte de puertas/spawns por plantilla. La nueva plantilla 3052 crea una sala compartida para PvP; no implementa aún campañas por grupo, viaje en barco o progreso de misiones.

## Experiencia propuesta y siguiente prueba

Giran → inscripción de grupo → embarque → viaje/cinemática → traslado controlado → Veilmar → campaña/exploración → regreso.

Puede funcionar como una excursión estilo Point Lookout dentro del mismo mundo. No necesita otro GameServer ni cruzar físicamente el borde del mapa. El barco, la cámara y el traslado pueden controlar la transición; cada grupo podría entrar en una instancia con sus propios NPCs y estado.

La prueba en el visor y la integración local de PvP están preparadas. El readme del autor indica que la geodata no está incluida; se generó una versión local desde la geometría con L2 Geodata Toolkit. Las puertas se importaron usando IDs y polígonos originales y alturas de sus mallas. La primera entrada en nuestro Interlude debe confirmar carga visual y recorridos reales; una prueba de servidor no sustituye esa revisión. La campaña y el transporte quedan pendientes.

