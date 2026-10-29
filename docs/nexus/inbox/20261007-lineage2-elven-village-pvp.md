# Lineage II local: sala Elven Village PvP

El 7 de octubre de 2026 se preparo una primera sala PvP compartida y aislada que reutiliza las coordenadas y el escenario de Elven Village sin modificar la zona de paz del mundo principal.

- Plantilla dinamica PvP: `3051`.
- Entrada: `.elvenpvp` o `.elvenpvp entrar`.
- Salida: `.elvenpvp salir`.
- Estado: `.elvenpvp estado`.
- Reinicio GM: `.elvenpvp reiniciar`.
- La sala se crea al primer ingreso y permanece compartida.
- Contiene nueve FakePlayers de combate: Arden, Selene, Eryndor, Lethiel, Vaelkor, Myrentha, Gorvak, Zhurak y Brunna.
- Son copias de combate provisionales; no modifican los nueve personajes fisicos de telemetria.
- Buscan automaticamente el objetivo visible mas cercano, atacan FakePlayers y jugadores y reaparecen a los 20 segundos.
- Los magos usan Prominence, Hydro Blast o Hurricane; el resto prueba autoataque melee/rango.
- Los archivos viven tanto en `server/game/data` como en `source/L2J_Mobius_CT_0_Interlude/dist/game/data`.
- El reinicio de fase 5 de las 19:49 cargo 3 plantillas de instancia, 36 NPC custom y 128 scripts. `error0.log` quedo vacio.
- El servidor informa conflictos nominales porque las copias usan los mismos nombres que los personajes fisicos; es informativo y no impide cargar las plantillas.

Pendiente funcional: entrar con un cliente, ejecutar `.elvenpvp`, observar pathfinding/seleccion de objetivos y ajustar posiciones, dano y supervivencia con evidencia visual. No se aplicaron todavia las builds finales de fase 5.
