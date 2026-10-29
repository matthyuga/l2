# Giran: Ares y Nyx patrullan y defienden

11/10/2026. Instalado y validado: **1909 comprobaciones nativas PASS**; GameServer listo para jugar.

La IA anterior era SiegeGuardAI: adquiría enemigos dentro del alcance físico del arma (40), no del aggro configurado. Sin un Spawn asociado tampoco podía caminar de regreso ni patrullar. Solo reaccionaba al daño.

- Ares recorre el patio, la entrada desde la puerta exterior y el acceso a la puerta interior. En combate corre al enemigo, usa War Cry y sus ataques físicos individuales nativos.
- Nyx recorre la sala, el pasillo y la escalera norte hasta el artefacto. Usa Arcane Power, Silence, Surrender to Wind, Wind Vortex, Demon Wind y Hurricane con MP/reuse y efectos nativos.
- Patrullan caminando también fuera del asedio. Cada uno lleva su propia ruta y pausas.
- Durante el siege detectan atacantes registrados a 1200; mantienen un blanco hasta 1600, con límite de sector a 2000 del puesto. Prioridad: conquistador casteando Seal, agresor de defensores/puertas, invasor cercano. Nyx da más peso al acceso final.
- Respetan propietario actual y defensores registrados, incluidos summons. No adquieren jugadores neutrales, NPC comunes ni blancos tras paredes o en campamentos. Al cambiar de propietario borran el combate anterior.
- Muertos conservan cadáver; se pueden revivir desde `.giran`. A los 60 segundos vuelven a la sala de resurrección y esperan 10 segundos. La geodata deja esa sala superior aislada (probe BFS 990 celdas, sin ruta a la sala inferior), por lo que usan un traslado interno a la sala y vuelven a su puesto caminando. Este traslado está limitado al ciclo de resurrección: no se usa durante patrulla ni persecución. Si las puertas interiores siguen cerradas, Ares patrulla el acceso y la sala desde dentro hasta que se abran o destruyan.

Se conservan V6, propietario, clanes, estadísticas originales de bosses y geodata. El ajuste es de conducta, no de daño o HP. `.giran` muestra las zonas de ambos guardianes.

Validación nativa PASS: ciclo completo de ambas rutas por movimiento nativo; daño real sin provocarlos; uso de skills; propietario cercano protegido; prioridad a Seal; enemigo summon y límite de persecución; regreso desde sala. Regresión completa V6 y snapshots privados de persistencia. Los fixtures de navegación aislan enemigos para comprobar las rutas; el balance del asedio completo se prueba jugando.

Stage: `research/giran-guardians-v7`. Respaldo: `backups/giran-guardians-v7-2026-10-11`. No reejecutar instaladores históricos.

Persistencia PASS: Hellkevin/inventario, clanes/skills/reputación, propietario/fecha de Giran y guardias conservados; 19 pilotos offline nivel80. Core, estadísticas de bosses y geodata V6 sin cambios. Runtime/source/cloud sincronizados, sin commit ni push.
