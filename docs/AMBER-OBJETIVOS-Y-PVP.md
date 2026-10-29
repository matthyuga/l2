# Amber: objetivos y reglas PvP — 2026-10-10

## Causa del bloqueo

`ArenaNoctis` y `Hellkevin` pertenecen a Hellsing (clan268474389). El predicado propio de Amber rechazaba clan/alianza antes de consultar las reglas nativas, incluso dentro del Coliseo. Además exigía zona PVP tanto para dueño como objetivo, y la IA sólo escaneaba jugadores/summons. Esto impedía atacar monstruos fuera del Coliseo y descartaba NPC del combate automático.

## Comportamiento corregido

- **Coliseo:** orden manual contra jugadores válidos sigue el criterio nativo; un compañero de clan puede ser rival de entrenamiento. No exige bandera violeta. La IA sigue protegiendo a compañeros que no sean rivales.
- **`.ia mago` / `.ia fisico`:** `LabCombatPilots.isCombatOpponent` publica una relación de combate temporal y de sólo lectura entre el controlador y su piloto. Incluye los summons del piloto. Sólo es válida durante combate, después de la preparación. Por eso Noctis deja de ser considerado un aliado durante esa prueba.
- **IA:** puede seleccionar jugadores enemigos, summons enemigos y monstruos, incluidos los NPC Monster de laboratorio. No inicia ataques contra jugadores blancos ajenos por estar cerca. Un foco manual puede priorizar el rival elegido, incluso del mismo clan en arena. Guardias u otros NPC combatibles se aceptan como foco manual, sin incluirlos indiscriminadamente en el escaneo automático.
- **Campo abierto:** un jugador blanco requiere **Ctrl + Atacar del summon**. La autorización corresponde a ese objetivo concreto; seguir/detener o cambiar de modo la retira. Siguen aplicándose los controles de instancia, paz, NO_PVP, party, aliados de asedio, duelos/Olimpiadas, invisibilidad e invulnerabilidad.
- **Monstruos comunes:** orden manual e IA pueden atacarlos fuera de zona PvP; no ponen violeta al dueño. Amber no ataca a su NPC de contrato ni al marcador de lluvia.
- **Bandera:** el arco ya usa `Creature.doAttack` con el dueño como jugador actuante, por lo que aplica las reglas nativas. La lluvia aplica HP mediante código propio; ahora llama también a `Player.updatePvPStatus` para atribuir al dueño la agresión. Conserva las opciones existentes de fake players, raids y champions. Atacar a un PK o hacerlo en arena conserva sus excepciones nativas; no se fuerza violeta para todo caso.
- **Mensajes:** la orden manual explica el motivo concreto: invulnerabilidad/preparación, paz, otra instancia, party, Ctrl requerido, etc. El mensaje genérico de «enemigo en zona PvP» fue sustituido.

La IA puede elegir primero **Nightshade** en vez de Noctis según amenaza y puntuación. Para concentrar el arco en el mago, seleccionar a Noctis y pulsar **Atacar**. Debe haber aparecido el aviso de comienzo de la prueba; durante la preparación el piloto es invulnerable. Invulnerabilidad GM del dueño, muerte, estados de control, carga de lluvia, alcance y línea de visión también pueden pausar o impedir acciones.

## Cambios y validación

Cinco fuentes modificadas: AmberContract.java, AmberServitor.java, AmberAssist.java, AmberContractVerification.java y LabCombatPilots.java. En el piloto sólo se añade el getter y publicación volatile del estado; no se modifica su build, stats ni lógica de combate. Fuentes compiladas y espejadas en source/dist y cloud overlay. Sin modificaciones de JAR ni cliente; se preservan V10, cámara y catálogo por clase.

Backup: `backups/amber-target-policy-2026-10-10/`. La prueba opt-in usa probes reservados y una sesión real de `.ia mago` contra ArenaNoctis, etiquetada `test_mode=AMBER_TARGET`. Reproduce mismo clan sólo en metadatos del probe en memoria, restaurados al terminar. No cambia la membresía de Noctis ni Hellkevin.

Comprueba daño real a monstruo fuera de PvP, daño real con Ctrl a jugador blanco, bandera del dueño, autorización retirada con Stop, bandera de lluvia, ausencia de bandera en arena, preparación invulnerable, relación temporal con Noctis, eventos reales de daño de Amber al piloto o su summon y foco manual contra Noctis. Los eventos excluyen falsos positivos por autocostes de HP de Noctis. También se ejecutan las pruebas completas existentes de contrato, iconos, arco, soulshots, fuego, lluvia, controles, selección de áreas, toggle y limpieza. El arnés espera la ejecución efectiva de Flechas de fuego hasta3s porque el clic puede quedar encolado después de un disparo.

La fase de `.ia mago` espera a que expire naturalmente el estado de combate del probe anterior. Durante esa fase, sólo AmberOwnerProbe recibe una reserva temporal de100000HP, retirada en finally antes de guardarlo: su equipo de prueba sin joyería PvP era vulnerable a morir de un solo golpe de Noctis y cortar la observación. No concede invulnerabilidad, no modifica a Noctis y no sirve como medición de balance. La sesión queda etiquetada AMBER_TARGET.

Resultado final y estado del servidor: `research/client-comfort/amber-target-installed.json` y `research/client-comfort/amber-target-verification.log` al concluir la ejecución. La sesión se deja iniciada y las verificaciones opcionales se desactivan en el siguiente arranque habitual.

Resultado final: **25 comprobaciones específicas PASS**, incluidos eventos de daño real con selección autónoma de un rival válido y foco manual contra el Noctis Player. La batería general anterior pasó146 comprobaciones (log archivado en pass146-verification.log). Una repetición posterior de esa batería falló al preparar un root aleatorio; se amplió su número máximo de intentos en el arnés y se aisló la prueba de objetivos con lab.amber.targets.only=true. Noctis conserva Hellsing y queda desconectado al terminar; ambos probes quedan desconectados y sin clan. GameServer permanece iniciado; prueba opt-in terminada.
