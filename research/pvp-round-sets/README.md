# Tandas de bots y sorteo por ronda

15/10/2026. Activo en PID27412 sin reiniciar la ronda del usuario. Se conservan expresamente las parties de jugadores reales, segun respuesta del usuario. Las parties de bots se disuelven y vuelven a formar dentro del equipo correspondiente.

Al terminar una ronda, `PvpRoundRooms.roundFinished` sortea conjuntamente el orden de admision de participantes reales y bots de la tanda siguiente. `RoundState.join` reparte ese orden entre los equipos menos poblados: diferencia maxima de un participante. Se reinician marcador, votos y contadores por personaje como antes. El mapa sigue siendo el ganador de la votacion; los modos conservan instancias independientes. El sorteo no garantiza igualdad de habilidad/clases ni un ganador distinto.

`PvpRoundSets` prepara de forma asincrona otra tanda del mismo tamano/perfil de votos. Reserva perfiles nativos libres antes del final: la tanda siguiente no comparte personajes con la activa ni con otras salas. No aparece en combate hasta el relevo. En el limite de ronda se retiran/restauran los perfiles anteriores y se entrega la tanda preparada al arranque normal de bots, conservando sus condiciones de entrada y la creacion de parties. Los jugadores reales tambien participan del sorteo de colores, aun cuando solo haya uno; no quedan siempre en rojo por entrar primero.

Si la tanda no esta lista o faltan perfiles, se conserva la actual y se vuelven a sortear equipos/parties. La preparacion fallida libera sus reservas parciales y reintenta despues de60s. `.salas bots estado` muestra `Proxima tanda: ... n/n`; parar una sala cancela y libera tambien sus reservas, incluida una preparacion en curso. No se reiniciaron bots en otros modos.

## Identidad e instancias

Dos salas pueden jugar Elven simultaneamente sin verse. La instancia separa el espacio, no duplica el objeto `Player` ni su identidad en World/DB. Este sistema reserva un personaje nativo solo una vez. Dos Noctis simultaneos requieren actores independientes derivados de una misma plantilla (objectIds distintos y nombres/alias compatibles con el core); eso aun no esta implementado. No se copio el mismo personaje vivo a dos instancias ni se altero la unicidad de nombres.

El roster es finito. Preparar una siguiente tanda requiere perfiles adicionales libres; con muchas salas al maximo puede aplicarse el fallback. Estos perfiles prestados no quedan disponibles para otro laboratorio de siege mientras estan activos o preparados. Mantener el procedimiento de detener bots antes de apagar: el snapshot de restauracion todavia no es persistente ante crash.

## Evidencia

- Compilacion completa de los scripts aprobada y redefinicion de tres clases, helper nuevo; sin cliente/core/animaciones.
- `verification.txt`: fixture con nombre de Script distinto del lobby, dos bots originales reemplazados por otros dos en instancia aislada; los anteriores salieron de World, generacion aumento, marcador quedo en cero y equipos1/1. Cien simulaciones de admision aleatoria mantuvieron2/2/2 y produjeron44particiones distintas. Fixture retirado; registro del lobby real, instancia y party de Hellkevin intactos.
- La primera construccion de fixture fallo antes de cargar personajes por falta del contexto de ScriptEngine. Se corrigio solo en el banco V2, preservando/restaurando `_currentExecutingScript`; no se recargo el lobby.
- `live-audit.txt`: seis activos y seis preparados en produccion con identidades distintas, lobby registrado correcto. Aun no se forzo una transicion en la sala del usuario: se verifico con la misma logica en el fixture aislado.
- `installation-audit.json`: hashes de la cadena vigente, incluyendo esta etapa. Los verificadores de etapas anteriores no incluyen estos cambios.

## Archivos y rollback

Doce fuentes en runtime/source/overlay, `installation.json` y respaldo `E:/l2-local/backups/pvp-round-sets-20261015-155557`. `PvpRoundRooms`, `PvpRoomBots`, `PvpSiegeRoster` y nuevo `PvpRoundSets`. `prepare.py` registra la transformacion inicial, no debe ejecutarse otra vez sobre fuentes ya modificadas. Los fixtures/agentes estan solo en research.

Para revertir: `.salas bots parar todas`, esperar que termine la cancelacion de preparaciones, detener GameServer y ejecutar `python E:/l2-local/research/pvp-round-sets/restore.py`; luego iniciar por lanzador normal. Revertir esta etapa antes de pvp-bot-combat o siege-bots.
