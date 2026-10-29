# Salas PvP — Elven V1

Actualización 15/10/2026: auto-flag de jugadores integrado y probado. Ver [SALAS-PVP-ELVEN-AUTOFLAG.md](SALAS-PVP-ELVEN-AUTOFLAG.md) para el comportamiento vigente del flag y el respaldo de esta etapa. El resto de este documento conserva la descripción de la sala V1.

Implementada el 14/10/2026 en E:\l2-local (hora de Argentina).

## Acceso

- NPC **Salas PvP / HELLGAMES** en Giran: 83480,148120, suelo -3400 aprox.
- El mismo NPC en el muelle aéreo de Gludio: 149160,46700,12016.
- Ambos muestran el menú con Elven Village, modalidad todos contra todos y cantidad de jugadores.
- `.elvenpvp` / `.elvenpvp entrar` se conservan como acceso compatible.
- `.salas salir` y `.elvenpvp salir` inician la misma cuenta de 4 segundos; `.salas cancelar` cancela la salida por comando si el personaje sigue dentro del perímetro.

## Perímetro y salida

Primera delimitación rectangular: 42000 < X < 49200; 46600 < Y < 54000; -3800 < Z < -2000. Incluye la llegada y los nueve combatientes existentes. Cruzar cualquiera de estos límites inicia la cuenta; alejarse más no reinicia el plazo ni permite salir de la instancia sin completar la cuenta. Este perímetro es configurable en PvpRooms.java; no hay una pared física o una textura nueva pintada en el terreno.

La barra V1 es un indicador segmentado de texto en la parte superior de la pantalla, actualizado mientras se consume durante 4 segundos. Usa ExShowScreenMessage y no ocupa la barra de casteo ni bloquea movimiento o habilidades. Al llegar a cero se muestra el indicador vacío y el personaje vuelve a Giran, también si había entrado desde el muelle. El plazo usa tiempo monotónico y un controlador de 100 ms: resolución de salida normal de 0–100 ms, además de posibles demoras del servidor.

Si el personaje vuelve al interior antes del vencimiento, se cancela la cuenta y se desplaza a su última posición interior válida. El retorno detiene la acción en curso, pero conserva el actor visible y seleccionable en el servidor, sin protección de teleport, stun ni inmovilización añadidos. La transición visual/control del cliente requiere prueba ingame. Se actualizan posición autoritativa/cliente y bandera de desplazamiento para reducir correcciones por paquetes atrasados.

Durante la cuenta y después del retorno se puede recibir daño. Una muerte cancela la salida; no revive ni expulsa al personaje muerto. La salida por comando tampoco es instantánea. Un intento de cancelar al cumplirse los cuatro segundos termina la salida.

Al volver a entrar se usa la última posición interior guardada, validando suelo; si dejó de ser válida, se usa la llegada. Se conserva en memoria durante la ejecución del servidor y no sobrevive un reinicio. El ingreso requiere estar vivo, desmontado, fuera de combate, sin teleport pendiente, sin vehículo, fuera de duelo/Olympiad y sin otra instancia activa.

## Estado del personaje

Ni ingresar, salir, cancelar ni observar una reaparición cura HP/CP/MP, aplica Noblesse o limpia buffs/debuffs. El controlador anterior de Elven fue corregido para que no restaure recursos al entrar o detectar un revive. Daño, regeneración, consumos, duración de efectos, muerte y reaparición mantienen sus reglas normales; no se restaura una foto histórica del personaje.

El ingreso/salida entre instancias completa el teleport en el servidor y retira su protección nativa, sin esperar inmunidad durante la carga del cliente. El retorno dentro de la sala usa desplazamiento sin retirar el actor del mundo. Ninguna de estas rutas añade protección. La llegada exterior de Giran conserva la paz normal de esa ciudad.

Los nueve combatientes y su IA original continúan en la sala. No se modificaron builds, equipo, daño o respawn de esos NPCs. La sala sigue usando la plantilla 3051 y la telemetría existente.

## Verificación

Compilación contra el GameServer.jar instalado: PASS. Pruebas sobre los handlers activos con dos Player transitorios, sin cuentas/personajes persistentes: PASS.

Comprobado: ambos NPCs, menú, bypass real del NPC del muelle, ingreso compartido, conservación inmediata de HP/MP/CP y buff, daño durante la cuenta y después del retorno, cancelación hacia la última posición interior, independencia entre jugadores, ausencia de salida a 3,8 s y salida al vencer 4 s, regreso a Giran, reingreso en posición guardada, eliminación de cuentas viejas, salida por comando, cancelación por muerte y ausencia de curación al observar un revive.

Geodata: se encontraron cruces transitables en los cuatro lados del rectángulo, muestreados cada 64 unidades: oeste 29, este 42, sur 9, norte 82. Esto no certifica todos los trayectos visuales ni sustituye un recorrido humano.

**Pendiente de cliente:** revisar visibilidad de los dos NPCs, menú, indicador segmentado, recorrido del borde y respuesta de cámara/movimiento al retornar. No se certificó el render del cliente en esta sesión. La barra V1 no es todavía un widget gráfico personalizado.

Evidencias: `research/elven-rooms/verification.txt`, `deployment.txt`, `installation.json`. El servidor se reinició durante el trabajo por una operación ajena a este instalador y cargó los scripts a las 19:53; las actualizaciones posteriores se cargaron sin reiniciar y sin duplicar NPCs/timers.

## Archivos y respaldo

Runtime, source y overlay local sincronizados:

- `data/scripts/custom/ElvenPvpRoom/PvpRooms.java`
- `data/scripts/custom/ElvenPvpRoom/ElvenPvpRoom.java`
- `data/scripts/custom/ElvenPvpRoom/PvpFlaggingStopTask.java` (tarea nativa de flag PvP, cargada de forma aislada)
- `data/stats/npcs/custom/pvp_rooms.xml`
- `data/instances/custom/elven_village_pvp.xml` (salida de respaldo a Giran)

El folder ElvenPvpRoom ya está permitido por WorldContent.ini, por eso el nuevo script también carga al arrancar. No se cambió el core, el cliente ni otras salas. No se hizo commit/push.

Backup anterior: `backups/elven-rooms-20261014-195242`.

Restauración: cerrar GameServer y ejecutar `python research/elven-rooms/restore.py`. Verifica hashes antes de restaurar y se niega a sobrescribir modificaciones posteriores. Restaura solo los quince archivos registrados; al siguiente arranque vuelve el controlador anterior, incluyendo sus reglas previas de restauración de recursos.
