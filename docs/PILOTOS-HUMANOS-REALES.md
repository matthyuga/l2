# Pilotos humanos reales — 8 de octubre de 2026

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
