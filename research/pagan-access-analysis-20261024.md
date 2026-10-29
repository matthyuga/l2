# Pagan Temple: acceso Interlude (2026-10-24)

Diagnostico de solo lectura. No se cambiaron configuracion, spawns ni estado del juego.

- WorldContent.ini: CustomWorldOnly=True, spawns solo data/lab/world-spawns. ScriptEngine filtra scripts con WorldContentConfig.allowsScript: ai/areas/PaganTemple no permitido.
- RuneNPCs.xml lineas 120-121 conserva espejo 32039 en (34842,-49756,-763) y espejo 32040 en (-11986,-35903,-10857), pero el perfil no carga los spawns clasicos.
- PaganTeleporters.java: onFirstTalk del NPC 32039 teletransporta a (-12766,-35840,-10856); 32040 devuelve a (36640,-51218,718). La conexion depende del NPC, no de abrir una pared caminando. No se inspecciono geometria UNR; identificar exactamente la superficie roja de la captura sigue pendiente.
- Las puertas internas 19160001, 19160010 y 19160011 dependen tambien del script y NPCs 32034-32037. Crear solo el espejo no basta con la AI excluida.
- Comando GM comprobado en AdminTeleport.java: //move_to -12766 -35840 -10856 (destino original del espejo). Solo sugerido al usuario, no ejecutado.

REA: open_binary + inspect_artifact summary de E:/l2-local/server/libs/GameServer.jar, SHA256 749e841f831b4de8870517ae683f154e58ba99eaa09155deacb8309c9c4c89b7. Inventario estatico de archivo, no decompilacion Java ni verificacion runtime. Evidencia ev_7fa1698a29a309919b9bb6778ef319de323b2480d42e70e1a9ac2f3e20fa8deb. La conclusion funcional procede de scripts/configuracion/codigo locales, no del inventario REA por si solo.
