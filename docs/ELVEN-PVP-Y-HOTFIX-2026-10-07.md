# Sala Elven PvP y ajustes operativos

Estado verificado el 7 de octubre de 2026.

## Sala PvP aislada

- Instancia dinámica: `3051`.
- Entrada: `.elvenpvp` o `.elvenpvp entrar`.
- Salida: `.elvenpvp salir`.
- Estado: `.elvenpvp estado`.
- Reinicio GM: `.elvenpvp reiniciar`.
- Reutiliza el escenario de Elven Village sin retirar la zona de paz del mundo
  principal.
- Contiene nueve FakePlayers de combate. Son copias provisionales y no modifican
  los nueve personajes físicos usados como anclas telemétricas.
- Los participantes reciben Noblesse Blessing, HP/MP/CP completos al entrar y al
  reaparecer, y los FakePlayers adquieren blancos en modo FFA.

## Ajustes acompañantes

- Duración del Scheme Buffer: 7.200 segundos para buffs, songs, dances y
  especiales.
- Noblesse Blessing (`1323`) disponible en el Scheme Buffer.
- Mana Potion (`728`) disponible en la multisell `50039928` por 2.000 Adena.
- Límite de cubics: tres cuando no existe una Cubic Mastery activa que lo amplíe.

## Archivos del overlay

- `dist/game/data/scripts/custom/ElvenPvpRoom/ElvenPvpRoom.java`
- `dist/game/data/instances/custom/elven_village_pvp.xml`
- `dist/game/data/stats/npcs/custom/elven_village_pvp.xml`
- `dist/game/config/Custom/SchemeBuffer.ini`
- `dist/game/data/SchemeBufferSkills.xml`
- `dist/game/data/multisell/custom/50039928.xml`
- `dist/game/data/scripts/handlers/skill/effects/SummonCubic.java`
- `java/org/l2jmobius/gameserver/config/custom/SchemeBufferConfig.java`
- `java/org/l2jmobius/gameserver/entity/actor/instance/SchemeBuffer.java`

El núcleo completo compiló y el Game Server cargó 128 scripts y 86 buffs del
buffer. La validación visual y de jugabilidad sigue siendo una prueba manual:
entrar con un cliente, revisar selección de blancos, pathfinding, daño y tiempos
de supervivencia antes de convertir las copias en builds finales.

## Telemetría NPC contra NPC

El capturador de `LabTelemetry` reconoce los IDs `901100–901108` dentro de la
instancia Elven PvP y registra ataques entre ellos mientras exista al menos un
jugador real conectado dentro de la sala. Al quedar sin observadores deja de
guardar estos eventos, evitando que el FFA automático haga crecer la base de
datos indefinidamente.

Cada evento conserva ID de instancia, cantidad de observadores, atacante,
defensor, skill, daño, crítico, fallo, recursos y muerte. Las estadísticas de los
nueve NPC también se guardan en `lab_creature_stats`, incluyendo HP, P.Atk,
M.Atk, P.Def, M.Def y velocidades.

El panel incorpora `/api/telemetry/elven-pvp` y el bloque **Elven PvP · combate
vivo**, con daño infligido y recibido, impactos, críticos, fallos, bajas, muertes,
daño absorbido por muerte, equivalentes de barra de HP y skill de mayor daño.
Los datos anteriores al cambio siguen intactos, pero no poseen `instance_id` ni
`observer_count`; la comparación NPC contra NPC comienza con la siguiente entrada
a `.elvenpvp`.
