# Doce rivales: builds mixtas con raza fija

Ampliación preparada el2026-10-09: `DIECINUEVE-DUELOS-INDIVIDUALES.md`.
Los siete añadidos se activaron el2026-10-09. Ver documento de diecinueve.
Correccion posterior: SK de Kaelis/Riven/Noctis era ID107 (Spectral Dancer),
ahora ID106 (Shillien Templar). Sus cifras historicas de abajo no sustituyen
las fichas actuales del panel, recalculadas tras la correccion.

2026-10-08. Receta `normal-pvp-s4-hybrid-v2`.

Los nueve perfiles del Coliseo reciben tres subs complementarias. Se añaden
Kaelis, Riven y Noctis con las tres combinaciones solicitadas por el usuario.
No se modifican las builds de los siete pilotos anteriores ni los anclajes
originales nivel 1. Cada rival tiene un Player técnico persistente `Arena...`.

| Rival | Raza / perfil | Principal activa | Sub 1 | Sub 2 | Sub 3 |
|---|---|---|---|---|---|
| Arden | Humano fighter | Dreadnought | Hell Knight | Doom Cryer | Grand Khavatari |
| Selene | Humana mystic | Cardinal | Phoenix Knight | Wind Rider | Dominator |
| Eryndor | Elfo fighter | Moonlight Sentinel | Hell Knight | Hierophant | Grand Khavatari |
| Lethiel | Elfa mystic | Mystic Muse | Phoenix Knight | Arcana Lord | Dominator |
| Vaelkor | Elfo oscuro fighter | Ghost Hunter | Shillien Templar | Soultaker | Doom Cryer |
| Myrentha | Elfa oscura mystic | Storm Screamer | Shillien Templar | Spectral Master | Cardinal |
| Gorvak | Orco fighter | Titan | Phoenix Knight | Grand Khavatari | Doom Cryer |
| Zhurak | Orco mystic | Dominator | Eva's Templar | Arcana Lord | Archmage |
| Brunna | Enana fighter | Maestro | Shillien Templar | Grand Khavatari | Doom Cryer |
| Kaelis | Humano fighter | Sagittarius | Grand Khavatari | Titan | Shillien Templar |
| Riven | Humano fighter | Adventurer | Grand Khavatari | Titan | Shillien Templar |
| Noctis | Orco mystic | Dominator | Cardinal | Shillien Templar | Spectral Master |

Equivalencias: Tyrant → Grand Khavatari; Destroyer → Titan;
Shillien Knight (SK) → Shillien Templar; Bishop → Cardinal;
Phantom Summoner → Spectral Master.

## Reglas y comparación

- Nivel 80 en los cuatro slots. Todas pueden tener tercera aprendida.
- Acumular skills hasta segunda; sólo la clase activa aporta tercera y sus
  niveles mejorados. Masteries repetidas no se suman.
- Raza y perfil inicial permanecen al cambiar de slot.
- Principal: equipo S y joyería +4, dyes legales y buffs físicos o mágicos.
  No se fuerzan toggles, Frenzy/Guts, Zealot, UD ni tótems en la captura.
- Las subs reciben dyes físicos o mágicos legales para su clase. El equipo
  no cambia al activar una sub: para combate manual requiere arma/armadura
  compatible. Las lecturas comparativas del roster usan la principal.
- Eryndor/Selene retoman conjuntos de finalistas históricos; otras recetas
  son adaptaciones y las tres nuevas son propuestas del usuario. No declarar
  resultados de fases antiguas válidos para esta regla nueva sin repetirlas.

## Integración

NPC 901100–901111, nombres en el mismo orden de la tabla. `.arena iniciar`
inicia doce duelos; diez segundos entre victorias; `.arena repetir` y
`.arena cancelar` se conservan. Los tres nuevos esperan en una segunda fila
del mismo sector interior. La entrada al duelo sigue usando el punto seguro
del arreglo previo de geodata; falta comprobar visualmente esta fila.

El panel «Rivales del Coliseo» muestra doce perfiles, sus subs y stats observados.
Telemetría de ataques extendida hasta 901111; no se borra historia anterior.

Límite: estos NPC siguen siendo Monster, no Player con IA completa. Se copian
los stats calculados por el Player técnico; no se implementan estrategias de
summon/TP, cubics, curación, potas o defensa por añadir subs. Selene usa ahora
Steal Essence heredado de Overlord, y Noctis el mismo ataque de su principal;
no se les concede Prominence ajeno a sus builds. El sistema de copiado de
stats por FuncSet conserva su limitación previa frente a cambios dinámicos.

Respaldo previo: `E:\l2-local\backups\twelve-hybrid-roster-2026-10-08`.
Validar cuatro slots y recarga de cada perfil, skills permitidos, raza y stats
antes/después. La preparación registra `HybridSlot PASS`, `RosterHybridReload PASS`
y un total de 12 perfiles. No iniciar el experimento si hay fallos de preparación.

## Validación completada

Arranque final 21:48:19; roster listo 21:49:31. Doce recargas verificadas,
96 checks de slots (cuatro antes y cuatro después de recarga por perfil).
`verify-twelve-roster.js`: SUCCESS 12/12 para recetas, raza, subs nivel 80,
regla vigente y nueve stats del NPC idénticos a su Player fuente. Compilación
Java, sintaxis del panel y XML correctos. `.arena iniciar` se bloquea hasta
que todos los perfiles pasen. No se ejecutó pelea manual ni se validó aún
visualmente la segunda fila de espera.

Capturas actuales de los tres adicionales, principal activa, buffs y +4:

| Rival | P.Atk | M.Atk | P.Def | M.Def | Vel. ataque | Casteo | HP | CP | MP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Kaelis | 3392,22 | 330,40 | 1145,76 | 1222,73 | 764 | 230 | 6553 | 2422 | 2711 |
| Riven | 1214,80 | 330,40 | 1145,76 | 1222,73 | 1129 | 230 | 6307 | 1826 | 2711 |
| Noctis | 593,34 | 2372,73 | 1007,75 | 1710,43 | 426 | 922 | 7366 | 3198 | 5386 |
