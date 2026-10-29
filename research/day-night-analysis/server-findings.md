# Servidor Interlude: reloj, ambiente y altura

Analisis estatico del codigo local en `E:\l2-local\source\L2J_Mobius_CT_0_Interlude`. No se ejecuto el juego ni se modifico servidor/cliente.

Todas las rutas siguientes son relativas a esa raiz.

## Reloj y sincronizacion

- `java/org/l2jmobius/gameserver/taskmanagers/GameTimeTaskManager.java:45-50`: ticks=10/s, tick=100ms, IG_DAYS_PER_DAY=6, dia=14.400.000ms=4h reales, 144.000 ticks por dia.
- `GameTimeTaskManager.java:64-69`: referencia = medianoche local de la fecha de arranque del servidor, mediante Calendar.getInstance(). No guarda progreso en BD ni empieza necesariamente en una hora fija al arrancar.
- `GameTimeTaskManager.java:79-81`: gameTicks=floor((currentTimeMillis-referenceTime)/100); gameTime=(gameTicks %144000)/100; gameHour=gameTime/60. gameTime son minutos enteros 0..1439; un minuto de juego dura10s reales.
- `GameTimeTaskManager.java:83-116`: noche cuando gameHour<6; noche [00:00,06:00), 1h real; dia [06:00,24:00), 3h reales. Cambios disparan Shadow Sense de elfos oscuros, DayNightSpawnManager y evento OnDayNightChange.
- `java/org/l2jmobius/gameserver/managers/DayNightSpawnManager.java:60-70,94-115,161-165`: elimina spawns del periodo anterior y activa los del nuevo.
- `java/org/l2jmobius/gameserver/network/serverpackets/CharSelected.java:77`: manda la hora del juego %1440 durante seleccion/entrada del personaje.
- `java/org/l2jmobius/gameserver/network/serverpackets/ClientSetTime.java:39-41`: paquete definido con dos int: minutos del juego y velocidad6. Importante: busqueda de toda java y dist/game/data/scripts no encontro ningun uso de esta clase que efectivamente la envie. No afirmar que hay resincronizacion periodica con ese paquete en esta base.
- `java/org/l2jmobius/gameserver/network/ServerPackets.java:56-57,213,280`: SunRise=0x1C, SunSet=0x1D, ClientSetTime=0xEC, ExRedSky=0xFE/0x40.
- `dist/game/data/scripts/handlers/chat/commands/user/Time.java`: comando /time consulta este mismo reloj.

## Overrides de atmosfera

- `dist/game/data/scripts/handlers/chat/commands/admin/AdminEffects.java:651-684`: //atmosphere sky day|night|red [duration] selecciona SunRise, SunSet o ExRedSky y difunde el paquete a todos los jugadores conectados.
- Esa funcion no cambia GameTimeTaskManager: override visual y reloj/logica del servidor son cosas distintas.
- `java/org/l2jmobius/gameserver/network/serverpackets/SunRise.java:38` y `SunSet.java:38` solo escriben opcode. No mandan posicion, direccion o intensidad del sol.
- `java/org/l2jmobius/gameserver/network/serverpackets/ExRedSky.java:38-39` solo escribe opcode y duracion. La interpretacion visual y unidad efectiva requieren comprobar cliente.
- `java/org/l2jmobius/gameserver/entity/actor/holders/player/CursedWeapon.java:226`: usa ExRedSky(10) para arma maldita.
- No se establece mediante estos archivos como interpola el cliente su cielo, si hay luz direccional dinamica o posicion astronomica del sol. Eso pertenece al renderer/configuracion cliente.

## Altura y coordenadas

- `java/org/l2jmobius/gameserver/entity/World.java:62-80`: tile=32768; X [-131072,229376], Y [-262144,262144]; WORLD_Z_MIN=-16000, WORLD_Z_MAX=16000 y regiones verticales de2000.
- No interpretar +/-16000 como clamp universal. `World.java:2538-2551` calcula region y agrupa valores inferiores a-16000 en region0 y superiores a16000 en ultima region. No cambia Z real.
- Posible fallo estatico de borde: exactamente z=16000 entra en formula (16000+16000)/2000=16, pero hay16 regiones (indices0..15) segun `World.java:89,102`. GetRegion captura excepcion y puede disponer del objeto, segun `World.java:2504-2515,2563-2598`. No se probo en runtime.
- `java/org/l2jmobius/gameserver/network/clientpackets/ValidatePosition.java:84-93`: Z reportado por cliente fuera de[-20000,20000] es anormal; intenta volver a lastServerPosition y retorna. Es una restriccion practica separada; no prueba limite del renderer.
- `java/org/l2jmobius/gameserver/network/clientpackets/MoveToLocation.java:49-54` y `serverpackets/CharSelected.java:54-56`: XYZ se leen/escriben como int32. El ancho del paquete no establece altura jugable segura.
- `java/org/l2jmobius/gameserver/geoengine/geodata/blocks/ComplexBlock.java:56` y `MultilayerBlock.java:237`: altura codificada = (short)(data &0xFFF0)>>1; representable -16384..16376 en pasos8. Es limite de esa representacion geodata, no del cielo. FlatBlock.java:33-37 usa short puro.
- `java/org/l2jmobius/gameserver/entity/WorldObject.java:635-659`: setXYZInvisible corrige X/Y a bordes pero conserva Z.

## Implicacion para el sol propuesto

Un sol visual en el cielo no tiene por que ser NPC/objeto servidor ni seguir las coordenadas Z del jugador. Lo correcto es conservar una unica fuente de hora (servidor) y adaptar el renderer cliente/cielo a esa fase. Estos hallazgos no demuestran por si solos que Interlude permita mover una luz con sombras dinamicas por todo el mapa; eso requiere evidencia del cliente. Las sombras pintadas o precalculadas tampoco se convierten automaticamente en dinamicas al mover un disco solar.
