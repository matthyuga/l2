# L2: prueba de una, dos y tres salas de 32 bots

- Fecha: 22/10/2026. Sesión Codex, ruta real `E:\l2-local`.
- Pedido: probar varias salas llenas de 32 participantes. Se probaron 32 por sala en 16 vs 16, con copias de la misma composición de 32 builds, instancias Elven distintas y coordinador serial. Sin clientes humanos; telemetría y pool de 10 conexiones sin cambios.
- Un GameServer limpio por caso: 1 sala/32 bots completó 120 s, barrido IA p95 58,3 ms; 2 salas/64 bots completaron 120 s, p95 80,8 ms; 3 salas/96 bots completaron 180 s, p95 120,1 ms. Objetivo 100 ms; no afirmar que siempre se cumple con tres salas.
- Tres salas: hasta 54 summons adicionales; CPU media del GameServer 4,83% de la capacidad de 16 hilos, heap máximo 2754 MiB, RSS máximo del proceso 3039,6 MiB. Cadencia media de visitas 9,55/s por sala; intervalos p95 121,3 / 134,6 / 159,6 ms.
- Cero timeouts SQL registrados y cero eventos de daño cruzado observados en los tres casos. Hubo solicitudes esperando conexiones (pico 39 con tres salas): esto no prueba que el pool esté corregido ni que no pueda saturarse en otras condiciones.
- Es una prueba corta, con recursos/cooldowns nativos y sin membresía de clan de las copias. No valida red/FPS de clientes, horas de estabilidad, cuatro salas, 32 vs 32 por sala ni un asedio.
- El ensayo anterior de 100 en una sala no usa composición/instrumentación idéntica: no es un control para atribuir un factor de mejora únicamente a las instancias.
- Limpieza independiente PASS en los tres casos; cero actores/filas temporales verificadas; 39 perfiles originales, inventarios, skills, clanes y castillos preservados. Arranque normal final verificado, GameServer único y puerto7777 disponible. Sin commits/push ni cambios de producción.
- Informe: `E:\l2-local\reports\multiroom-32-2026-10-22\INFORME.md`. CSV, resúmenes, layout y verificación por caso en `1-rooms`, `2-rooms`, `3-rooms`; estado final en `final-state.json`.
