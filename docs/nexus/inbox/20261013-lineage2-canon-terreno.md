# Canon Cathedral: terreno e interiores ? 13/10/2026

El mapa 17_17 contiene TerrainInfo0 con altura16 Arenas_MT.Height.19_13. Nueve slots de capas, ocho activos y uno Texture=None/AlphaMap=None. Recuperados height16, visibilidad, diagonales y ocho texturas con matrices y mascaras. License28 requiere reservar4bytes antes de mipmaps; extendida lectura generica.

Todas las ubicaciones de los actores estaticos estan entre Z=-12598 y-11275; el terreno esta entre Z=-3805 y3220. Son salas bajo el relieve exterior. Agregado terreno al glTF pero oculto inicialmente (terrain_visible=false). Boton Mostrar terreno/Ocultar terreno en escenas con terrain_included, habilitado al cargar vista3D. Mismo control disponible para R4. No agregar tierra artificial alrededor de salas ni inferir un exterior continuo alrededor de la catedral.

65536vertices,130050triangulos de terreno. Miniatura renderizada ocultando terreno para preservar vista de interiores. Dependencias, fechas de miniatura y API/UI resources HTTP verificados. No se hizo prueba interactiva WebGL viva; no afirmar que se hizo. No cliente/servidor modificado. Backup JS/HTML/viewer en backups/canon-terrain-toggle-20261013 y JSON en research/scenario-batches/gallery-before-canon-terrain.json.

Abrir http://127.0.0.1:32280/?model=scenario_batch1_canon_cathedral&view=3d y Ctrl+F5.
