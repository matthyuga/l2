# HELLGAMES: cuatro modos y votacion por sala

Ruta real E:/l2-local. Usuario confirma mapas Elven, playa Primeval, Valley of Saints ("desierto" describe este ultimo). Cada modo tiene sala/voto independiente. Equipos sin daño amigo; Libre permite atacar clan y party. Arena es FFA con Top 10.

Implementacion y pruebas aisladas PASS: rondas provisionales 30m, voto abre faltando5m/dura60s/resultados4m, votos por personaje/ronda, rechazo duplicados/tardios/antiguos, azar sin votos/empates, puntuacion y equipo verde por titulo/color. Daño real amigo bloqueado/enemigo permitido, areas/party FFA, cambio mapas, muertos sin autorevive y salida4s. No se movio Hellkevin. Configuracion editable.

Se agregaron geodata 20_17 y22_15 con revision fija Orion, hashes/procedencia; limites candidatos y spawns validados por componentes transitables. Debe recorrerse visualmente en casa. Sin cambios al cliente.

IMPORTANTE: cuatro salas preparadas para PROXIMO ARRANQUE NORMAL, no activas aun. Usuario dijo que dejo el juego abierto; no reiniciar ni mover para esta etapa. Lobby anterior activo. Start-L2Local.ps1 aplica primero pending elven-position-sync y despues 20261015-pvp-rounds (7clases); nuevos scripts luego inician cuatro salas. PvpRooms.main anterior deshabilitado para evitar NPC duplicado.

Leer SALAS-PVP-RONDAS.md y research/pvp-rounds/README.md. Backup backups/pvp-rounds-20261015-115354; rollback con hashes. Orden rollback: rondas, sync, autoflag. UI, barra, verde y cold startup pendientes. Error "Files are corrupted" aportado por usuario: cree que pertenece a otra sesion de animaciones; esta sesion no reparo ni modifico cliente.
