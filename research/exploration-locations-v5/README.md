# Reconocimiento nativo de ubicaciones V5 — 26/10/2026

Pedido: usar REA para encontrar y reconocer las ubicaciones del juego, ampliando
los167 destinos aproximados de V4.2. Proyecto E:\l2-local; cliente E:\l2\system-hud.

## Resultado y cobertura

ZoneName-e.dat contiene362 registros y242 nombres distintos. l2zonename.utx
contiene204 máscaras P8 de128x128, cada una para un sector32768x32768 unidades.
Se cargan TODOS los registros y máscaras sin modificar archivos del cliente.
Las máscaras referencian355 registros/241 nombres. Un registro de _Lyonn Territory
tiene intervalo29999<z<30000 sin coordenada entera válida; además el nombre
genérico Talking Island no tiene píxeles. Resultado visitable comprobado:
354 registros,240 nombres. Los otros7 registros sin color en su sector no agregan
nombres activos exclusivos: ver coverage.json. No inventar límites para datos
inactivos. Huntingzone-e.dat aporta220 registros con puntos de referencia, usado
para contrastar Ketra y otras ubicaciones, no como sustituto de las máscaras.

Ketra Outpost y Ketra Village son áreas distintas. Tower of Insolence se separa
por pisos usando altura. El destino GK llamado Ketra Orc Outpost está todavía en
Goddard Territory según la máscara original; el aviso de Ketra aparece al entrar
realmente al área. Esta diferencia es esperada frente al círculo aproximado V4.2.

## Evidencia REA y extracción

REA/Ghidra analizó binarios originales en lectura. NWindow.dll GetCurrentZoneName
RVA143850 delega a Engine.FL2GameData. Engine.dll SHA256
214984fda24a9acc6544c2e22238b7439f61e31f57ec777f6356ab4fd901649c.

- RVA162970: processGetZoneNameInfo calcula sector, carga textura, lee byte P8 y
  busca nombre por color/sector/altura.
- RVA1584b0: GetZoneNameTexture forma explícitamente L2ZoneName.%d_%d.
- RVA14bf90: colores menores200 son globales; los otros dependen de sector.
- RVA162780: selección estricta bottom<z<top entre variantes de altura.
- RVA2887b0: GetSWMapXY; constantes360448,294912,1/32768,+9 equivalen en el
  continente a floor(x/32768)+20 y floor(y/32768)+18.

Evidencia completa en rea-*.json. Los parsers locales acmi/l2io y Python son
extracción ordinaria complementaria, no resultados atribuidos a REA. Se usaron
esquemas locales Interlude de L2ClientDat para decodificar dat y se verificó el
trailer SafePackage. Raw textures conservan índices originales, no colores RGB
reconvertidos. UModel/Pillow verifica independientemente orientación y16384píxeles
de Ketra. Rizin no estuvo disponible; el análisis funcional quedó confirmado por
Ghidra. Los hashes de entradas están en coverage.json.

## Implementación

NativeExplorationZones.java carga native-zones.xml y zone-masks.bin. Consulta
directa del byte correspondiente256x256 unidades, clave por color/sector y rango
vertical original. Prioridad: TownZone real del servidor, máscara nativa, catálogo
aproximado anterior sólo si no hay coincidencia nativa. No modifica zonas de
combate, geodata, spawns, teleport, economía ni recompensas. Mantiene ensayo GM.

ExplorationWalking conserva Tracker de dos observaciones y cooldown12seg. Primera
visita: título Lugar descubierto y chat. Reentrada: nombre. IDs de descubrimiento
usan el mismo hash de nombre V4.2; ciudades mantienen FOG4_TOWN_. Las capas de
niebla y variables anteriores no se borran. Sin nueva DLL ni cambio de protocolo.

## Verificación e instalación

Compilación contra libs actuales. NativeZonesTest:731 comprobaciones, todos los
354 registros visitables/240 nombres, puntos Giran/Goddard/Ketra/Gludin, pisos
de TOI, límites estrictos y coordenadas negativas. verify-assets.py compara
índices/colores con exportación independiente. Falta prueba visual real V5.

install.py valida hashes V4.2 y ausencia de jugadores, respalda8archivos runtime/
fuente, instala y actualiza el manifiesto de V4 para conservar restore.py hacia
V3. Backup backups/exploration-native-v5-20261026-001555. GameServer se reinició
sin jugadores conectados. Estado exacto de carga en installation.json.

Prueba sugerida: entrar en Ketra al norte de la llegada del GK, avanzar al poblado
interior; después cambiar de piso en TOI. Nombres nuevos deben dar primer aviso,
regresar muestra sólo nombre. Los títulos no aparecen cada celda de la niebla.
