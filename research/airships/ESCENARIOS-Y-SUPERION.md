# Escenarios y Superion — 12/10/2026

Kevin pidió descargar las estructuras de Internet y añadirlas al visor existente.

Disponibles en la galería local:

- [Gludio: muelle aéreo](http://127.0.0.1:32280/?model=airship_scene_gludio&view=3d). Arquitectura del mapa 15_25, ocho actores de Glacia_kserth_S. Se excluyeron los portales distantes para que la plataforma pueda examinarse con un encuadre útil.
- [Keucereus: base y muelles](http://127.0.0.1:32280/?model=airship_scene_keucereus&view=3d). Arquitectura del mapa 14_25, 224 actores.
- [Gracia: zona aérea 13_25](http://127.0.0.1:32280/?model=airship_scene_aerial&view=3d). Arquitectura del mapa 13_25; identificación con Aerial Cleft todavía por confirmar. El plano publicado por deMEV muestra esta zona circular al oeste de Keucereus.
- [Superion: biblioteca de componentes](http://127.0.0.1:32280/?q=Superion). 106 mallas exteriores y 58 interiores, con miniaturas y texturas representativas. Se abren en WebGL y UModel. Se identifican expresamente como componentes, no como la fortaleza completa.
- [Superion: fortaleza ensamblada](http://127.0.0.1:32280/?model=airship_scene_superion&view=3d). Se recuperó el mapa 22_22 de Helios: 643 actores Superion (607 exteriores y 36 interiores), todas sus referencias resueltas. Distribución, escalas y rotaciones proceden del mapa. Las partes animadas o giratorias permanecen en su orientación guardada y no se simulan sus efectos.

Los escenarios conservan las posiciones, rotaciones y escalas de los actores originales. No incluyen terreno, cielo, partículas, personajes ni iluminación original. Los shaders complejos se aproximan mediante materiales del visor. El montaje procede de mapas y no de posiciones inventadas. Archivos editables: gludio-architecture.blend, keucereus-architecture.blend y aerial-architecture.blend. Las auditorías *-assembly-audit.json enumeran los actores incluidos.

Fuentes de descarga:

- Gracia: manifest público de [L2Pride](https://l2pride.us/updater/manifest.json). Mallas, texturas y mapas comprobados contra tamaño y SHA-256 publicado.
- Superion: índice público de [Exilium StaticMeshes](https://launcher.exiliumworld.com/patch/StaticMeshes/) y [Textures](https://launcher.exiliumworld.com/patch/Textures/). Los archivos .bz2 se descomprimieron localmente. Se guardaron hashes locales y URLs; no había hashes publicados que permitieran autenticar la procedencia original.
- Mapa de referencia publicado por el autor del port: [deMEV, 2016](https://maxcheaters.com/topic/200222-keucereus-alliance-base-gludio-airship-field-aerial-cleft-seed-of-destructioninfinity-for-interlude/), copia local demev-zones-reference.jpg.

El mapa 22_22 del cliente público de Exilium no contiene actores Superion. La reconstrucción usa una copia Helios de lineage2.org.uk: se recuperaron 22_21, 22_22 y 23_22 mediante lecturas HTTP parciales de un 7z sólido, con comprobación CRC por py7zr. Fue necesario leer y descomprimir los datos anteriores: 2.483.069.996 bytes de red; solo se conservaron los tres mapas (29.886.970 bytes). El cliente completo no se guardó ni se ejecutó. 22_22 contiene Superion; los otros dos mapas no incluyen actores de esos paquetes. URLs y cantidades en helios-maps-source.json. Los ZIP públicos Superion P502 y Sakura P557 de lineage2.org.uk no tienen un directorio ZIP válido y no se usaron como fuente.

Chaos' Air Fortress de Sakura Isle sigue pendiente. Se encontró un cliente RAR de 16,51 GB publicado por Keucereus; no se ha descargado completo. El intento de indexar por rangos leyó al menos 200 cabeceras (1,6 MB) y se cerró sin recuperar un índice completo ni modelos de esa fortaleza; estado en sakura-extraction-status.json. Chaos_S.usx/Chaos_T.utx del índice Exilium contienen piezas antiguas de naturaleza y estructuras orgánicas; no se identificaron como la fortaleza de 2026 y no se añadieron a la galería con ese nombre.

No se ha hecho la adaptación a Interlude ni se han instalado estos recursos en el cliente del juego o GameServer. La apertura en UModel y la conversión a glTF no prueban compatibilidad dentro del juego.

Verificación: todas las nuevas mallas tienen enlaces de buffers y texturas locales; las miniaturas se renderizaron con Blender. verify_webgl_live.py espera la carga real del glTF y captura WebGL de los escenarios y componentes representativos. La API del visor abrió Superion_S.superion_statue_01 y UModel respondió. Auditorías: all-downloads-audit.json y new-structures-verification.json. Estado final de catálogo: 841 registros y 840 miniaturas; búsqueda «Estructuras aéreas» reúne 198 vistas, incluida la nave de Gracia preparada antes.
