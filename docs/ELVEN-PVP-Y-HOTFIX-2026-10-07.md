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
