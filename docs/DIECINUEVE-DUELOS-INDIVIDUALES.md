# Coliseo: diecinueve rivales y pruebas individuales

2026-10-09. Activado y verificado a las06:02:41: roster19/19 preparado.

Se mantienen los doce rivales anteriores. Se añaden copias de combate de los
siete pilotos, sin editar sus personajes Player originales. Los NPC nuevos
son901112–901118: Caelan, Ignara, Aelira, Korvash, Morvain, Sylira y Velith.
Usan perfiles técnicos ArenaCaelan…ArenaVelith, cuenta telemetryarena3,
misma principal/raza/subs que los pilotos, nivel80, equipo/joyas+4, dyes y buffs.
Se compararán sus nueve stats principales con los pilotos originales.

## Uso

- `.arena lista`: muestra los diecinueve nombres y números.
- `.arena probar Arden` o `.arena probar 1`: sólo un rival.
- Recuperar HP/CP/MP, buffs y consumibles antes de pedir otro rival. El servidor
  no cura ni cambia buffs del jugador automáticamente.
- `.arena probar Caelan`: prueba individual contra la copia del piloto.
- `.arena cancelar`: cancela el duelo actual.
- `.arena iniciar` / `.arena repetir`: secuencia completa de diecinueve,
  manteniendo diez segundos entre victorias. No son el modo individual.

Orden: Arden, Selene, Eryndor, Lethiel, Vaelkor, Myrentha, Gorvak, Zhurak,
Brunna, Kaelis, Riven, Noctis, Caelan, Ignara, Aelira, Korvash, Morvain,
Sylira y Velith. Los siete añadidos esperan en tercera fila interior. La
entrada segura al duelo y el fallback al centro se mantienen. Revisar
visualmente la tercera fila después del arranque; aún no verificada en cliente.

## Telemetría y límites

Cada prueba individual abre un run propio, con test_mode=INDIVIDUAL y
selected_npc_id. Se conserva registro WIN/LOSS, duración y recursos de cada
duelo; ataques/skills/daño siguen en lab_combat_events. SEQUENCE queda
identificado aparte; los registros previos conservan ese valor por defecto.
Contador de victorias independiente del número del rival seleccionado.

Sirve para medir daño y resistencia bajo la IA actual, no el potencial PvP
completo de cada build: siguen pendientes uso táctico de curas, summons/TP,
cubics, potas, toggles y defensivos. No equiparar esta prueba con un jugador
que emplea todo su repertorio. Mantener iguales las condiciones del jugador
entre rivales para evitar confundir desgaste con diferencia de poder.

## Verificación

Actualizacion IA 2026-10-09: piloto independiente en IA-PILOTOS-PLAYER.md,
comandos `.ia fisico` / `.ia mago`; `.arena` conserva la IA previa de los19.
Corregidas las subs SK de Kaelis/Riven/Noctis de107 (Spectral Dancer) a106
(Shillien Templar). Roster recalculado y check19/19+copias7/7 confirmado
despues de esa correccion y de AI_SMOKE10/10.

- Java compilado; sintaxis JS y XML correctos, diecinueve templates.
- Selector:57 casos válidos y6 inválidos PASS (nombres, minúsculas y números).
- Arranque confirmado: preparación19/19,152 checks de slots/recarga y
  verify-arena-roster.js SUCCESS19/19, con nueve stats NPC=Player y copias7/7.
- Pendiente prueba manual de comandos y posición visual en cliente. La otra
  sesión continúa desarrollando las conductas de combate (potas/summons/skills).
- Check read-only: `lab-panel/scripts/verify-arena-roster.js`.
- Respaldo SQL/archivos: E:\l2-local\backups\nineteen-individual-arena-2026-10-09.
- No reiniciar ni desconectar mientras haya cliente establecido en7777.
