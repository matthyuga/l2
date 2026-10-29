# Amber: cadencia automática y órdenes manuales

10/10/2026. Diagnóstico de la prueba de Hellkevin contra Atlas. Análisis de registros y del código fuente, corroborado con javap del GameServer.jar instalado. No se modificó el servidor ni el cliente.

## Medición

El log registra asistencia activada a las 17:01:38, selección de Atlas y fuego a las 17:01:39. No hubo lluvia ni cambios de blanco durante ese tramo. La asistencia se desactivó a las 17:02:04. Telemetría: lab_combat_events, eventos 19639–19679, atacante Amber, blanco Atlas, skill_id=0.

| Tramo | Intervalo entre impactos/intentos registrados |
| --- | --- |
| IA, 17:01:41.097–17:02:03.672 | 9 intervalos: 2507–2510 ms; mediana 2508 ms |
| Ráfaga manual, 17:02:10.919–17:02:16.355 | 1379, 1427, 1358, 1272 ms; mediana 1368,5 ms |
| Repetición posterior, desde 17:02:16.355 | Vuelve a aproximadamente 2508 ms |

Los intervalos incluyen eventos MISS en el tramo posterior: fallar no elimina el tiempo del disparo. No hay captura de cada clic del usuario; el registro permite identificar el modo y la ráfaga, pero no contar cuántas órdenes manuales se enviaron.

## Causa

Amber usa SummonAI nativa. El asistente evalúa objetivos cada 500 ms, pero no vuelve a ordenar un ataque si la intención sigue siendo ATTACK hacia el mismo objetivo. La repetición del arco queda a cargo del temporizador nativo.

Creature.doAttack calcula la preparación `500000 / PAtkSpd` y AmberServitor.calculateReuseTime añade `1398 * 333 / PAtkSpd`. La siguiente notificación READY_TO_ACT se programa al completar preparación más recarga. En esta prueba el resultado observado es 2,508 s. No se mide PAtkSpd directamente en esta telemetría: no debe presentarse una inferencia como estadística capturada.

Para BOW, `_attackEndTime` sólo cubre aproximadamente la mitad del ciclo completo. Una orden repetida sobre el mismo blanco ejecuta notifyActionThink de nuevo. El bloqueo adicional `_disableBowAttackEndTime` se comprueba en canUseRangeWeapon para Player y Npc, pero Summon deriva de Playable y no pertenece a esas dos ramas. Por eso una orden manual puede lanzar otro disparo tras el bloqueo corto, antes de terminar la recarga completa. Esto explica el intervalo de alrededor de 1,37 s; luego el temporizador automático vuelve a aproximadamente 2,51 s.

Fuentes: AmberAssist.tick; AmberServitor.assistAttack/doSummonAttack/calculateReuseTime; CreatureAI.setIntentionAttack; Creature.canUseRangeWeapon/doAttack/doAttackHitByBow; SummonAI.thinkAttack. Se revisó el bytecode del JAR activo para confirmar las ramas Player/Npc del bloqueo del arco.

## Siguiente cambio a definir

Manual e IA deben compartir una sola cadencia y respetar la recarga, incluso ante órdenes repetidas. La cadencia deseada se debe ajustar explícitamente: conservar 2,51 s o hacer el ciclo del arco más rápido para ambos modos. No conviene acelerar la IA reenviando órdenes cada 500 ms, porque aprovecharía el mismo fallo. La fluidez visual requiere comprobar además las animaciones en el cliente; los registros aquí miden intentos/impactos, no el movimiento renderizado del modelo.
