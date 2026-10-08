# Pilotos humanos reales — 8 de octubre de 2026

Actualización posterior: los siete pilotos ya tienen tres subs de tercera
profesión nivel 80. Se usan skills por slot activo, con raza fija; la preparación
y validación actuales están en [CLASE-ACTIVA-Y-TRES-SUBS.md](CLASE-ACTIVA-Y-TRES-SUBS.md).
Las recetas sin subs descritas a continuación son la referencia histórica.

Estos pilotos son personajes persistentes `Player`, no `Monster` con aspecto
de jugador. Se preparan con las APIs del servidor; no se escriben manualmente
P.Atk, M.Atk, defensas, velocidades, críticos ni recursos máximos.

| Perfil | Caelan | Ignara |
|---|---|---|
| Raza y sexo | Humano, masculino | Humana, femenino |
| Principal | Sagittarius | Archmage (fuego: Prominence) |
| Subclases | Ninguna | Ninguna |
| Nivel | Máximo configurado, actualmente 80 | Igual |
| Arma real | Draconic Bow — Focus +4 | Arcana Mace — Acumen +4 |
| Armadura real | Draconic Leather completa +4 | Arcana Robe completa +4, Imperial Crusader Shield +4 |
| Joyas reales | Tateossian: dos anillos, dos pendientes y collar, todo +4 | Igual |
| Dyes | +4 STR/-4 CON y +4 DEX/-4 CON | +4 INT/-4 MEN y +4 WIT/-4 MEN |
| Cuenta existente del laboratorio | telemetryf | telemetrym |

La raza humana y la ausencia de subclases se comprueban antes y después de
recargar el personaje desde la base. Principal activa: índice cero. Skills
aprendidas mediante `rewardSkills`, sólo de su principal. No se modifica
Hellkevin ni ninguno de los nueve anclas. Esta primera referencia no prueba
combinaciones: cuando se añadan subs será una por vez y sin tercera profesión,
reservada a la principal. Las masteries no se acumulan para inflar stats.

## Buffs explícitos, duración normal

Comunes: Wind Walk 2, Shield 3, Magic Barrier 2, Blessed Body 6, Blessed Soul 6,
Mental Shield 4 y Berserker Spirit 2.

Caelan: Might 3, Haste 2, Guidance 3, Death Whisper 3, Focus 3, Agility 3,
Prophecy of Wind 1; Dance of Warrior, Inspiration, Fire y Fury; Song of Hunter,
Water, Earth, Warding, Wind y Vitality (nivel 1).

Ignara: Acumen 3, Empower 3, Concentration 6, Wild Magic 2, Prophecy of Water 1;
Dance of Mystic, Concentration y Siren; Song of Earth, Warding, Wind, Vitality
y Renewal (nivel 1).

El script aplica los efectos reales y guarda la captura final; no los vuelve
permanentes ni los mantiene automáticamente durante una pelea. Cada arranque
recarga únicamente estos dos pilotos desconectados, valida su receta y
renueva la captura buffeada. Un piloto conectado nunca se modifica.
No activa todavía UD, Transfer Pain, Arcane Power ni otros toggles: esos estados
se medirán por separado, utilizando sus costes y condiciones reales.

## Persistencia y visibilidad

`custom/RealHumanPilots/RealHumanPilots.java` prepara los dos personajes quince
segundos después del arranque. `lab_real_human_pilots` guarda receta y fecha de
verificación. Se verifica nuevamente con `Player.load`, y LabTelemetry guarda
el perfil y `lab_player_stats`, sin inventar golpes de combate.
Los personajes aparecerán en **Personajes** del Laboratorio L2 y se podrán
seleccionar como referencias de comparación.

El inventario incluye CP pots, shots y flechas para el arquero. Esto no implica
que ya sepan consumirlos. No tienen aún un controlador de combate autónomo,
ni reemplazan al roster del Coliseo. La siguiente etapa es usar estos mismos
objetos Player con una IA que ejecute acciones normales y registre decisiones,
curaciones, potas, daño transferido y summons; nunca copiar sus números a un NPC.

La implementación compila contra el GameServer local. Los dos personajes ya
fueron creados y verificados por recarga, con cero subclases, raza humana y
stats idénticas antes/después de recargar. Caelan tiene 54 skills y 24 efectos;
Ignara tiene 74 skills y 20 efectos. Las dos cuentas permanecen desconectadas.

| Lectura buffeada | Caelan | Ignara |
|---|---:|---:|
| P.Atk | 3.392,22 | 496,23 |
| M.Atk | 330,40 | 4.221,08 |
| P.Def | 1.130,06 | 929,35 |
| M.Def | 1.114,73 | 1.508,38 |
| Atk. Speed | 729 | 413 |
| Casting Speed | 230 | 1.180 |
| HP | 6.073 | 5.356 |
| CP | 2.422 | 1.526 |
| MP | 2.711 | 5.060 |

Son capturas del motor con los efectos de esta receta, sin activables propios,
boss jewels ni skills de subclases. No equivalen a una medición de DPS en combate.

## Ampliación: Dominator orco y Mystic Muse elfa

Se añaden Korvash (orco, masculino, Dominator 115: tercera de Overlord) y
Aelira (elfa, femenino, Mystic Muse 103: tercera de Spellsinger). Ambos al
máximo 80, sin subclases, en la cuenta del laboratorio `telemetrym`.

Usan el mismo equipo y buffs mágicos que Ignara: Arcana Mace Acumen +4,
Arcana Robe completa +4, Imperial Crusader Shield +4, Tateossian completa +4,
buffs comunes y el bloque mágico de la receta, con duración normal. No se
activan Arcane Power, Soul Cry ni otras habilidades propias de forma automática.

Aelira usa dyes +4 INT/-4 MEN y +4 WIT/-4 MEN. Korvash usa sólo +4 WIT/-4 MEN:
el dye +INT 175 no admite Dominator en `hennaList.xml`; no se fuerza su uso.
El código separa sexo, raza, rol, skill principal y shots. Los consumibles
dependen de si el perfil es arquero o mágico, no del sexo del personaje.
El nombre histórico del script y de la tabla se mantiene para preservar los
dos pilotos existentes; la validación usa ahora la raza explícita de cada uno.

Creación y recarga verificadas: Korvash `268473977`, 79 skills; Aelira
`268473992`, 75 skills. Ambos nivel 80, cero subclases, 20 efectos y stats
idénticas antes/después de recarga. Capturas visibles en Personajes del panel.

| Lectura buffeada | Korvash (Dominator) | Aelira (Mystic Muse) |
|---|---:|---:|
| P.Atk | 582,24 | 483,00 |
| M.Atk | 2.372,73 | 3.572,15 |
| P.Def | 993,75 | 929,35 |
| M.Def | 1.602,43 | 1.518,83 |
| Atk. Speed | 426 | 426 |
| Casting Speed | 922 | 1.365 |
| HP | 7.366 | 5.322 |
| CP | 3.198 | 1.516 |
| MP | 5.386 | 5.096 |
| STR / DEX / CON | 27 / 24 / 31 | 21 / 24 / 25 |
| INT / WIT / MEN | 32 / 20 / 36 | 42 / 28 / 30 |

Son clases distintas de razas distintas y con dyes legales distintos; no es
una comparación aislada del efecto de la raza. No se midió combate ni DPS.

## Soultaker humano

Morvain se añade como HUMAN, masculino, Soultaker 95, nivel 80, sin subclases,
en `telemetryf` (séptimo personaje de esa cuenta). Equipo, dyes y buffs mágicos
idénticos a Ignara. No activa Transfer Pain, invocaciones ni otros toggles
automáticamente; esta captura es la referencia de principal equipada/buffeada.

Creado y verificado por recarga: `268473971`, 81 skills, 20 efectos, cero subs.
M.Atk 4221.08, P.Atk 496.23, P.Def 929.35, M.Def 1508.38, casteo 1180,
Atk.Speed 413, HP 5356, CP 1526, MP 5060; STR/DEX/CON 22/21/27,
INT/WIT/MEN 46/25/29. Coincide con Ignara en estos stats bajo la misma receta,
pero no en su conjunto de skills ni necesariamente en desempeño de combate.

## Comparación Storm Screamer: elfo oscuro frente a elfo claro

El usuario pidió crear los dos: Velith (DARK_ELF) y Sylira (ELF), ambas Storm
Screamer 110, femeninas, nivel 80, sin subclases. Equipo, dyes y buffs mágicos
idénticos a Ignara/Aelira/Morvain. No se modifican atributos manualmente ni
el core para fabricar una diferencia entre ellas.

Se agrupan en `telemetryx` porque telemetryf y telemetrym ya tienen siete
personajes cada una. Player.create guarda estos personajes; esta tarea no
establece una contraseña para esa cuenta. El login local permite registro
automático normal al entrar con un usuario nuevo.

El core conserva la raza guardada, pero los seis atributos base todavía
proceden de la plantilla de clase activa; un cambio sólo de `_race` no
transforma esos atributos. No se cambió esa semántica en esta prueba.

Ambas ya creadas y verificadas: Velith `268473890` (race=2, DARK_ELF), Sylira
`268473929` (race=1, ELF). Se compararon las filas PAPERDOLL con enchant,
hennas, effect_key, cantidad de skills y 29 valores de `lab_player_stats`:
equipo, dyes y buffs idénticos, 74 skills y 20 efectos cada una, cero subs.
No hay diferencias en ninguno de los 29 valores, salvo identidad y tiempo
de captura que se excluyeron de la comparación.

| Stat | Velith DARK_ELF | Sylira ELF |
|---|---:|---:|
| P.Atk | 516,08 | 516,08 |
| M.Atk | 4.727,93 | 4.727,93 |
| P.Def | 929,35 | 929,35 |
| M.Def | 1.477,03 | 1.477,03 |
| Atk. Speed | 422 | 422 |
| Casting Speed | 1.125 | 1.125 |
| HP / CP / MP | 5191 / 1479 / 4951 | 5191 / 1479 / 4951 |
| Accuracy / Evasion | 129 / 110 | 129 / 110 |
| Physical / Magic critical (valores internos) | 41 / 190 | 41 / 190 |
| Run Speed | 168,528 | 168,528 |
| STR / DEX / CON | 23 / 23 / 24 | 23 / 23 / 24 |
| INT / WIT / MEN | 49 / 24 / 27 | 49 / 24 / 27 |

Conclusión: la identidad racial persiste correctamente, pero la raza guardada
no gobierna los atributos base del motor actual. No concluir que elfo claro
y oscuro son equivalentes; el cruce ELF/Storm Screamer está recibiendo la
plantilla de stats de esa clase. Corregir una separación real raza/clase
sería un cambio de core y de reglas globales, no un ajuste manual de estos NPC.
# Actualización: regla racial fija (8 de octubre de 2026)

El core ya usa raza + perfil inicial para STR/DEX/CON/INT/WIT/MEN.
Las lecturas anteriores que muestran a Sylira y Velith iguales son históricas.
Ahora Sylira registra M.Atk 3572.15 y casteo 1365; Velith M.Atk 4727.93 y
casteo 1125, con equipo/dyes/buffs iguales. Ver `RAZA-Y-PERFIL-FIJO.md` para
la regla, métricas completas, pruebas y límites del cambio. Las curvas base
de HP/MP/CP por clase todavía no se independizaron.
