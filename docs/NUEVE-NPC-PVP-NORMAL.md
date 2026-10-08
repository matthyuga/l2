# Coliseo: nueve rivales con perfiles normales

Actualizado: 2026-10-08. Implementación `normal-pvp-level80-s4-v1`.

Los NPC 901100–901108 conservan sus nombres, raza, tercera profesión, posición y
orden del gauntlet. Ya no dependen de sus cifras de combate artificiales al
arrancar el servidor: `NormalNpcRoster` prepara un `Player` de referencia por
rival, calcula sus stats con el motor normal, y aplica esos valores al NPC.
Los nueve perfiles son nivel 80, sin subclases, con equipo de grado S +4,
joyería +4, dyes y buffs de clase. La raza queda fija a la del personaje ancla.

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

- Los atributos y derivados listados se capturan de personajes `Player` reales
  creados sólo como perfiles técnicos (`ArenaArden`…`ArenaBrunna`). Los nueve
  personajes ancla originales y su telemetría de fases anteriores no se alteran.
- Las armas de los perfiles son espada (Arden), maza mágica Acumen y escudo
  (magos), arco Focus (Eryndor), daga (Vaelkor), hacha (Gorvak) y martillo
  (Brunna); el antiguo aspecto de lanza y el bastón Imperial del mago orco se
  retiraron.
- Los NPC siguen siendo `Monster` con la IA actual del Coliseo: no son jugadores
  controlados por IA. Esta fase normaliza la hoja de stats/equipo/buffs; no añade
  todavía uso estratégico de skills, potas, CP/HP/MP, cubics, summons, UD,
  target cancel ni cambio de objetivo.
- Los valores se recalculan al arrancar el GameServer y los buffs se reaplican.
  Al cambiar recetas, revisar también la versión en `NormalNpcRoster`.
- Si falta un perfil, el script lo informa y ese rival conserva la plantilla
  anterior; comprobar el log `Roster Coliseo` antes de iniciar una pelea.

Validación realizada: compilación del script Java, preparación de 9/9 perfiles,
captura de stats en `lab_player_stats` y arranque del servidor sin errores del
roster. La validación de daño/supervivencia requiere una nueva pelea manual.
