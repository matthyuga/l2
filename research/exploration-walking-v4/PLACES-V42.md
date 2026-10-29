# V4.2 — nombres de lugares y primeros descubrimientos

El usuario confirmó que V4.1 despeja el terreno. NexusMapFog.log confirma
RECEIVED complete chunked personal/global exploration snapshot. Ketra no anunciaba
descubrimiento porque V4/V4.1 sólo consultaban TownManager y Ketra no es TownZone.

ExplorationPlaces carga places.xml:167 destinos con nombre de teleporters/town,
círculos de entrada de3000 unidades y tolerancia vertical1200. Si el nombre coincide
con un archivo de spawns se añaden sus polígonos originales (1227 en total), con
tolerancia vertical200. Ketra tiene su entrada y34 polígonos internos del XML
Goddard/KetraOrcOutpost.xml. Los círculos son geometría de exploración aproximada,
NO límites oficiales completos de ZoneName del cliente. El catálogo puede editarse
para cubrir caminos/huecos u otras ubicaciones. No altera spawns ni zonas de combate.

TownZone real tiene prioridad; entre lugares superpuestos gana el ancla más cercana
en distancia ponderada por altura. Se requieren dos observaciones consecutivas
y12seg entre avisos para evitar spam en fronteras. Primera visita muestra
Lugar descubierto: <nombre> durante5seg y deja registro en chat; vuelta a lugar
conocido muestra sólo nombre durante3seg. Entrar al juego también identifica el
lugar actual. La niebla sigue revelándose al caminar independientemente del catálogo.

Persistencia por personaje: FOG4_PLACE_<id estable SHA256 del nombre>. Las ciudades
conservan FOG4_TOWN_<townId>; no vuelve a otorgarse descubrimiento a ciudades
previamente visitadas. No hay recompensas. Sigue el ensayo sólo para GM humano.
Sin cambios de DLL, datos originales del cliente o esquema de base de datos.

Pruebas: compilación contra libs actuales y22 comprobaciones: Ketra en su entrada
y profundo interior, altura, zona desconocida, entrada estable, salida/reentrada,
cooldown y oscilación de fronteras. Aún falta prueba visual real del nuevo aviso.
Instalar con install-places.py tras desconectar al jugador y reiniciar sólo
GameServer. El manifiesto original se actualiza para conservar restore.py hacia V3.
