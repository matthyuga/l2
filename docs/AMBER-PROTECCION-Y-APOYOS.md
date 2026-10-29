# Amber: protección del amo, summons y curanderos

Actualización 2026-10-10. Activar **Asistencia de Amber** después de invocarla. Sigue comenzando en modo manual.

- El daño real contra su amo aumenta la prioridad del agresor. Una amenaza mucho mayor puede interrumpir la espera habitual entre cambios de objetivo; no necesita una orden de Atacar.
- Si el agresor tiene un servitor, Amber intenta quitarlo preventivamente, aunque Transfer Pain todavía esté apagado. Con TP activo valora además el porcentaje real de transferencia, el alcance nativo de 1000 y el esfuerzo aproximado de matar al summon frente al jugador. No exige que el enemigo tenga seleccionada una clase específica.
- Detecta curas efectivas de HP y CP sobre agresores recientes y sus summons. Cuanto más restaura un curandero, mayor es su prioridad. Incluye curas normales, porcentuales y periódicas. No interpreta regeneración natural, autocuras o curaciones que no restauran nada como apoyo de otro enemigo.
- Si el amo está por debajo del 30% de HP, aumenta mucho la prioridad de cortar al atacante directo. Distancia, defensas, vida restante y peligro siguen formando parte de la decisión; no es un orden rígido de objetivos.
- **Atacar manualmente mantiene el foco elegido.** Seguir, Detener y apagar el activable suspenden la IA; cambiar el modo borra las amenazas y curas recordadas. Las observaciones caducan a los seis segundos sin actividad nueva.
- Conserva las restricciones de party, paz, NO_PVP, instancia, invisibilidad, invulnerabilidad, alcance y visibilidad. No inicia PK contra un curandero blanco ajeno fuera de arena. El flag del agresor, del curandero y del amo continúa siguiendo las reglas nativas. La reacción a daño real permite responder a un agresor del mismo clan cuando el ataque sea válido; los compañeros que no intervienen siguen protegidos.

La lluvia conserva la selección de controles, UD y concentraciones de enemigos ya implementada. Estas prioridades gobiernan principalmente el objetivo del arco; no cambian daño, estadísticas, coste de soulshots ni animaciones.

## Implementación y comprobación

Cambios limitados a AmberAssist.java, AmberContract.java, AmberContractVerification.java y seis handlers de curación (Heal, HealPercent, HealOverTime, CpHeal, CpHealPercent, CpHealOverTime). Los handlers únicamente notifican a Amber después de restaurar HP/CP: no alteran la fórmula ni la cantidad curada. No hubo cambios de cliente ni GameServer.jar; se preservan V10, cámara y catálogo.

Prueba opt-in `lab.amber.verify=true` y `lab.amber.protection.only=true`: tres personajes reservados en una instancia privada, ataque nativo real contra el dueño, selección del summon antes y después de activar el TP real, curas nativas, variantes porcentuales/periódicas, urgencia, foco manual y regresión de reglas PvP. Los probes se desconectan y limpian al terminar. Un ataque único podía fallar por evasión; el ensayo usa combate continuo para esperar un impacto real sin forzar su daño.

Backup: `backups/amber-protection-2026-10-10/`. Fuentes espejadas en source/dist y cloud overlay, sin commit/push. Resultado final en `research/client-comfort/amber-protection-installed.json` y `amber-protection-verification.log`.

Logs de selección: `AMBER_AI ... reason=protect-owner`, `deny-transfer-pain`, `enemy-healer` u `opportunity`. Permiten revisar decisiones en el próximo TvT; las ponderaciones son heurísticas y todavía requieren observación de combate por el usuario.

Resultado final: **48 comprobaciones PASS**. Incluye regresi�n de objetivos/PvP, impacto real sobre el due�o, prioridad preventiva antes de TP, TP activo/rango/HP, cambio a curandero, las seis variantes de cura, urgencia, foco manual, toggle y caducidad. Compilaci�n Java correcta; nueve fuentes coinciden en las tres ubicaciones.
