# Lineage 2: armas PvP

Proyecto: `E:\l2-local`, 11/10/2026. Usuario probó Giran V9 y pidió retirar poles.

Darius: Saint Spear6370+4 sustituida por Heaven’s Divider Focus6607+4 mediante inventario nativo, persistencia y broadcast. Aplicado sin reiniciar GameServer/cliente ni modificar humanos o parties. El usuario finalizó su siege durante el trabajo; el cambio quedó guardado para nuevas preparaciones. La lanza anterior permanece desequipada en inventario para rollback.

Arden901100 y Darius901124 tenían ataque POLE en XML: corregidos a SWORD (también para espada de dos manos, según enum nativo), alcance40, con el modelo6607 de Darius. Receta NormalNpcRoster, ficha NPC/cache, verificador y documentación actualizados; espejos fuente/cloud sincronizados. Clases/subs intactas. Backup y snapshots privados en `backups/pvp-weapons-2026-10-11`.

Java compilado, XML contra npcs.xsd validado, inventario Darius6607+4 confirmado. La comparación global histórica NPC=Player puede diferir después de combate real (ya fallaba en Selene tras siege por snapshots/buffs); no se reconfiguraron los demás bots para forzar esa comparación. Pausas cortas de IA observadas por el usuario quedan para afinación posterior.
