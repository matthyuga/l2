# Coliseo: nueve rivales con perfiles normales

Estado histórico sin subs. El roster actual tiene doce rivales con tres subs;
ver `DOCE-RIVALES-SUBACUMULATIVOS.md`. Las cifras siguientes no son la lectura actual.

Actualizado: 2026-10-08. Implementación `normal-pvp-level80-s4-v1`.

Los NPC 901100–901108 conservan nombres, raza, tercera profesión, posición y
orden del gauntlet. Al arrancar, `NormalNpcRoster` prepara un `Player` técnico
por rival, calcula sus valores con el motor normal y los aplica al NPC. Los
nueve perfiles son nivel 80, sin subclases, con equipo S +4, joyería +4, dyes y
buffs. La raza queda fija a la del personaje ancla.

| Rival / clase activa | Raza | P.Atk | M.Atk | P.Def | M.Def | Vel. ataque | Casteo | HP | CP | MP |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Arden — Dreadnought | Humano | 1.259,65 | 330,40 | 1.445,04 | 1.114,73 | 841 | 230 | 8.662 | 3.703 | 2.422 |
| Selene — Cardinal | Humana | 496,23 | 4.101,03 | 961,55 | 1.508,38 | 413 | 1.180 | 5.911 | 2.357 | 5.060 |
| Eryndor — Moonlight Sentinel | Elfo | 3.074,18 | 363,84 | 1.130,06 | 1.132,15 | 725 | 269 | 5.496 | 1.565 | 2.749 |
| Lethiel — Mystic Muse | Elfa | 483,00 | 3.572,15 | 929,35 | 1.518,83 | 426 | 1.365 | 5.322 | 1.516 | 5.096 |
| Vaelkor — Ghost Hunter | Elfo oscuro | 1.250,75 | 389,98 | 1.130,06 | 1.132,15 | 1.062 | 244 | 5.024 | 1.574 | 2.749 |
| Myrentha — Storm Screamer | Elfa oscura | 516,08 | 4.727,93 | 929,35 | 1.477,03 | 422 | 1.125 | 5.191 | 1.479 | 4.951 |
| Gorvak — Titan | Orco | 1.746,90 | 298,58 | 1.445,04 | 1.140,86 | 696 | 244 | 10.119 | 3.850 | 2.479 |
| Zhurak — Dominator | Orco | 582,24 | 2.372,73 | 993,75 | 1.602,43 | 426 | 922 | 7.366 | 3.198 | 5.386 |
| Brunna — Maestro | Enana | 1.329,43 | 322,30 | 1.445,04 | 1.140,86 | 834 | 219 | 9.205 | 3.963 | 2.479 |

## Alcance y límites

- Las cifras salen de perfiles técnicos `ArenaArden`…`ArenaBrunna`; los nueve
  personajes ancla originales y su telemetría no se alteran.
- Se retiró la lanza de Arden y el Imperial Staff del mago orco: ahora usan
  espada y Arcana Mace +4. Los otros arquetipos usan arco Focus, daga, hacha,
  martillo o equipo de mago según corresponda.
- Los NPC siguen siendo `Monster` con la IA actual del Coliseo. Esta fase
  normaliza estadísticas, equipo, dyes y buffs; no añade uso estratégico de
  skills, potas, cubics, summons, UD, gestión de CP/HP/MP ni cambio de target.
- Los valores se recalculan al arrancar el GameServer y los buffs se reaplican.
  Si falla un perfil, el script lo registra y ese NPC mantiene su plantilla;
  revisar `NormalNpcRoster` en el log antes de iniciar la pelea.

Validación: compilación del script, preparación 9/9 y arranque sin errores del
roster. Daño y supervivencia quedan por comprobar en una pelea manual.
