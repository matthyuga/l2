# Combate de bots de salas

15/10/2026. Correccion activa en GameServer PID27412, sin reiniciar el lobby ni mover/restaurar recursos de Hellkevin. Al comenzar esta etapa habia seis bots en THREE_TEAMS: los grupos anteriores habian sido detenidos a las15:23 y esta sala reiniciada a las15:24. No se reiniciaron otras salas automaticamente.

Los perfiles nativos del siege estaban cargados con builds/equipo/subclases, pero la adaptacion de su IA era incompleta: no entregaba ni utilizaba consumibles y el mago podia terminar en autoataque fisico. Ahora:

- Stock por vida:50CP,60MP,60HP;4000soulshots y4000blessed spiritshots del grado del arma; flechas si usa arco; consumibles de habilidades conocidas. Se repone al preparar/reaparecer el bot, sin MP infinito durante la pelea.
- Consumo por los handlers nativos, condiciones y reutilizacion reales. La retirada normal del roster conserva su compensacion por cantidades originales. No se tocan builds ni consumibles de jugadores reales.
- Habilidades ofensivas conocidas, preferencia magia para magos y fisicas para guerreros; cura propia/de party cuando disponible. Magos sin un casteo viable dejan de ordenar autoataques fisicos.
- Invocaciones conocidas mediante casteo nativo, ataque de la invocacion y Transfer Pain si existe summon y skill1262. Las invocaciones con requisitos incumplidos no se fuerzan; aceptar una orden no prueba que la invocacion haya aparecido.
- Contadores separados para orden aceptada y evento nativo ON_CREATURE_SKILL_USE. Listeners propios se retiran al liberar el bot.

## Verificacion

`live-audit.txt`: muestra de seis bots activos, hechizos ejecutados1230/1239/1234/1245, curas1218/1401; guerrero ArenaArden ejecuto habilidades3/255/401 y consumio21cargas de soulshots en la muestra. Se observo consumo nativo de728MP,1539HP,5592CP,3952BSS. ArenaMyrentha tenia summon vivo y TP activo, con eventos1333 y1262 ejecutados. Los perfiles son hibridos del laboratorio: las habilidades conocidas de sus subclases pueden aparecer aunque el nombre de la clase activa sea otro.

`combat-verification.json` valida estos hechos contra los contadores, no contra dano inventado ni solo ordenes aceptadas. `installation-audit.json` comprueba52archivos vigentes de la cadena de salas. Se compilo el conjunto de scripts y se recompilaron los ultimos cambios del brain antes de cada redefinicion.

La primera redefinicion fue rechazada por cambios de metodos sinteticos generados por lambdas; se sustituyeron por bucles compatibles y se aplico correctamente mediante CombatPatchV3, seguido por RefreshSiegeBrain. No usar los agentes fallidos como instaladores. La definicion inicial del helper ya existe en este proceso.

Tambien se detectaron timeouts transitorios del pool DB de10conexiones mientras se preparaba la activacion. La causa del rechazo de redefinicion fue independiente. No se modifico el pool ni la telemetria. La auditoria posterior y la entrega de consumibles completaron; queda pendiente diagnosticar saturacion si se repite bajo carga.

La seleccion basica de acciones esta mejorada; no equivale a una IA tactica humana completa. No se ha certificado cada skill/arma/clase ni las invocaciones que requieren cadaveres. Estas ultimas deben respetar las reglas nativas.

## Instalacion y retirada

Nueve archivos en runtime/source/overlay, manifiesto `installation.json`, respaldo `E:/l2-local/backups/pvp-bot-combat-20261015-154130`. Sin cambios de cliente, animaciones ni core. La nueva clase se carga normalmente en el siguiente arranque.

Mantener el procedimiento del roster: detener bots con `.salas bots parar todas` antes de cerrar el servidor; el snapshot de restauracion no es persistente ante crash. Para revertir esta etapa, retirar bots, detener GameServer y ejecutar `python E:/l2-local/research/pvp-bot-combat/restore.py`; luego arrancar por el lanzador normal. No revertir fuentes mientras hay bots activos.
