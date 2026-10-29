# Primera IA de combate: Riven y Noctis

2026-10-09. Instalado y activo. Piloto experimental, no conversion general de los 19 NPC.

## Uso en el Coliseo

- `.ia fisico`: Riven, humano Adventurer, subs Tyrant / Titan / Shillien Knight.
- `.ia mago`: Noctis, orco Dominator, subs Bishop / Shillien Knight / Phantom Summoner.
- `.ia estado`: estado de la prueba.
- `.ia cancelar`: terminar y retirar al piloto.

Solo GM, vivo, sin invulnerabilidad, fuera de combate, dentro del suelo PvP
del Coliseo. Hay 20 segundos iniciales de preparacion y un limite de seis
minutos. No se puede ejecutar simultaneamente con una secuencia `.arena`.
Si entra otro Player cercano, la prueba se cancela para evitar dano colateral.

Se cargan los perfiles tecnicos reservados ArenaRiven / ArenaNoctis como
Players reales sin cliente. Los originales y las fichas de los 19 NPC no se
reemplazan. `.arena` mantiene su IA anterior; `.ia` prueba estas conductas nuevas.
Raza fija, nivel 80, equipo +4, dyes, buffs y reglas de segunda acumulada /
tercera exclusiva activa. No hay FuncSet ni multiplicadores artificiales de IA.

## Conductas

Riven: cubics, totem, stance, Mirage, Bluff, Arrest, Hex, golpes de daga,
Backstab cuando esta detras, Trick/Switch, Dash; emergencias Guts o Frenzy,
Zealot y Ultimate Defense. Solo intenta skills aprendidas y con condiciones
legales: una restriccion de arma, HP, MP, rango o reutilizacion no se salta.

Noctis: Nightshade, Transfer Pain, cubics, curacion propia y de summon,
Soul Guard / Arcane Power, silencio contra casteo, root, maldicion y Steal
Essence. El summon ataca al contrincante designado. Hasta dos invocaciones
confirmadas por duelo. No tiene Anchor: esa build no lo aprende.

Ambos usan shots y pociones mediante los handlers reales; presupuesto por
duelo: 10 HP, 50 CP, 30 MP, con stock y reutilizaciones normales. El equipo
no cambia para eludir condiciones. Guts y Frenzy no se apilan. No se cura
automaticamente al jugador operador ni se cambian sus buffs.

## Auditoria y verificacion

`lab_ai_runs` guarda inicio, final, contrincante, rol y resultado.
`lab_ai_actions` guarda decisiones, skill/item, HP/CP/MP y aceptacion/rechazo.
Una solicitud de casteo aceptada NO equivale a efecto aplicado; los eventos
reales de habilidades/dano siguen en la telemetria existente.

335 comprobaciones de politica pasan: umbrales, limites, histeresis de
activables y mapeo de cubics. Autoprueba de integracion optativa:
`-Dlab.ai.smoke=true`, solo en arranque, en instancia privada, sin atacar al
usuario. Comprueba summon, dos cubics, TP, totem, UD, dos curas y potas CP/MP.
El resultado real debe consultarse en game-stderr.log: AI_SMOKE SUCCESS 10/10.

Resultado confirmado 06:07:45: AI_SMOKE SUCCESS 10/10; runs3/4 SMOKE_PASS,
ambos perfiles retirados y offline0. Primera corrida runs1/2 SMOKE_FAIL
conservada como evidencia del error SK anterior. Despues: verificacion del
roster SUCCESS19/19 y copias7/7. Falta duelo manual, no se afirma PvP validado.

Pendiente: combate manual, eficacia/resistencias de controles, posicionamiento
avanzado, cambios de arma y estrategias de escuadron. No es aun una IA de siege.
Backup: E:\l2-local\backups\player-combat-pilots-2026-10-09.

Correccion de receta historica: la sub SK de Kaelis, Riven y Noctis usaba
erroneamente ID107 (Spectral Dancer). Se migra solo esa sub de esos tres
perfiles tecnicos a ID106 (Shillien Templar), nivel80 y dyes, mediante el
metodo normal modifySubClass. No se cambian otros107 del roster.

Actualizacion2026-10-09: NOCTIS-IA-Y-TELEMETRIA-V2.md, activa tras reinicio.
Sustituye el limite anterior por DOS solicitudes aceptadas de invocacion,
incluida inicial (las interrumpidas tambien consumen presupuesto).
Cura no urgente espaciada, recall del summon y apagado prioritario de toggles.
Observaciones de ambos lados cada500ms, reporte read-only duel-report.js.
Resistencias/causa exacta de buff retirado todavia no instrumentadas.
