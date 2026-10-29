# PvP rounds implementation

Documento funcional, limites, pruebas y pendientes: [SALAS-PVP-RONDAS.md](../../SALAS-PVP-RONDAS.md).

Archivos principales:

- `src/custom/ElvenPvpRoom/RoundState.java`: reloj, votos, participantes y puntaje independientes del servidor.
- `PvpRoomConfig.java`: configuracion y verificacion de spawns contra geodata cargada.
- `PvpRoundRooms.java`: lobby, cuatro salas, marcador, Top 10, panel, limites y cambios de mapa.
- `src/org/.../RoomCombatRules.java`: membresia explicita limitada a estas instancias; cinco clases existentes consultan esta regla para ataques/daño/debuffs/areas.
- `ScanPvpTerrainV2.java`, `terrain.csv`, `analyze-terrain.py`, `prepare-maps.py`, `maps.json`: eleccion reproducible de sectores.
- `geodata-sources.json`, `geodata-deployment.txt`: procedencia y carga de dos regiones.
- `TestRoundState.java`, `state-verification.txt`, `VerifyRoundRoomsV4.java`, `server-verification-v4.txt`: pruebas.
- `installation.json`, `final-installation-audit.json`, `final-runtime-audit.json`: manifiesto y comprobaciones.
- `restore.py`: restauracion con hashes y GameServer detenido.

Fallos de fixtures conservados: primer ensayo no establecia el contexto de carga requerido por Script/Quest; V2 comparaba con equals un titulo nulo valido. V3/V4 corrigen las precondiciones del banco. No representan pruebas aprobadas. El log de deleteMe sobre el probe offline es del cleanup de prueba; auditoria final confirma ausencia de probes. Los agentes son herramientas de laboratorio, no se incluyen en el core ni se ejecutan al arranque normal.

Activacion en frio y observacion visual pendientes porque el usuario mantiene el juego abierto. Actualmente estan cargadas las reglas de combate con registro vacio y la geodata, pero el lobby de produccion sigue siendo el anterior hasta reinicio. `support.jar` fue cargado solo en la JVM de laboratorio actual; al siguiente arranque los scripts se compilan desde las fuentes instaladas.
