# Asistencia de Amber: activable — 10/10/2026

La asistencia IA se controla con **Asistencia de Amber**, una quinta habilidad temporal del contrato. Amber se invoca en **manual**. En Alt+K se puede arrastrar el activable a la barra: un clic enciende la IA y otro la apaga. Usa el icono nativo de Arcane Power como icono provisional; no modifica atributos ni consume MP, HP o shots.

Seguir y Detener apagan también el activable. Una orden de Atacar conserva la prioridad manual mientras el blanco siga válido. `.amber auto` y `.amber manual` siguen disponibles y comparten el mismo estado e indicador del activable.

Se puede apagar durante la carga de lluvia: deja de tomar decisiones automáticas, pero termina la lluvia que ya había iniciado y pagado. No interrumpe su carga ni devuelve sus recursos. La IA, fuego, lluvia, arco y selección de blancos mantienen las reglas documentadas en `AMBER-ASISTENCIA-IA.md`.

Al morir o retirar a Amber se apaga el activable. Al salir del juego se retira el summon y se limpia el estado; al volver o reinvocarla comienza manual. Romper el contrato retira las cinco habilidades y cualquier activable pendiente. Usarlo sin Amber invocada o sin contrato no deja un indicador activo. El prototipo sigue reservado a GM.

## Implementación

- Skill servidor y cliente **19014**, nivel 1, `operateType=T`, SELF, coste cero, efecto `AmberAssistToggle` sin funciones de estadísticas.
- `AmberAssist.enable` aplica o retira el efecto nativo; `onStart`/`onExit` sincronizan el controlador. `Player.useMagic` resuelve el segundo clic con la lógica nativa de toggles. No se cambió el core.
- Cliente activo: `E:\l2\system-hud`. Se añade una fila a cada catálogo actual `skillgrp.dat` y `skillname-e.dat`, conservando los 29839 registros anteriores byte por byte; nuevo total 29840. Se preservan las revisiones visuales instaladas por otras sesiones.
- Constructor reproducible: `research/amber-l2/scripts/build_amber_assist_toggle_client.py`. Rechaza ID ya existente y solo prepara los DAT; no instala ni reinicia. Protocolo413, roundtrip y conservación de filas comprobados.
- Respaldo: `backups/amber-assist-toggle-2026-10-10`. Registros de cliente: `research/amber-l2/exports/contract/assist-toggle/verification.json`.

## Validación

**123 comprobaciones PASS** en el servidor real, con los Players reservados de `ambercontracttest` dentro de una instancia privada. Incluye inicio manual sin desactivación previa artificial, clic nativo ON/OFF, icono de estado, coste cero y estadísticas del dueño intactas, sincronización con comandos y Seguir/Detener, cambio durante carga, contrato sin summon, muerte del summon, ruptura y limpieza completa. Conserva la regresión de arco, fuego, lluvia, IA, controles y panorama. Evidencia: `backups/amber-assist-toggle-2026-10-10/verification-123-checks.log`.

Compilación contra el core instalado y roundtrip de ambos DAT: PASS. No usa Hellkevin ni sus consumibles. Las pruebas inmovilizan los actores de la escena de panorama y comparan la recarga nativa con el contador persistido, evitando depender de una espera corta durante la carga del roster. Reporte: `reports/amber-assist-toggle-verification.json`. La presentación visual final del icono requiere la revisión del usuario en el cliente.
