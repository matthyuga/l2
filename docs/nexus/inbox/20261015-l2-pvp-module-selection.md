# Módulos PvP para HELLGAMES

15/10/2026. Usuario aclara: L2Damage rotaba automática/aleatoriamente SIN votos; para HELLGAMES quiere votación del próximo mapa al terminar el tiempo. Prioridad ahora obtener módulos/pack de PvP flag y relacionados, antes de nuevas integraciones.

Se inventarió el core local: FlagPvPZone, ArenaZone, ZoneNPoly y PvpFlagTaskManager ya presentes. PvpFlaggingStopTask de Elven es para NPC FakePlayers, no auto-flag de jugadores. Preparado dossier E:\l2-local\research\pvp-module-pack\README.md y ZIP research\HELLGAMES-PVP-modulos-referencia-20261015.zip (integridad PASS). Incluye copias locales y seis fuentes/configs/docs de Orion fijadas al árbol 0daf83956edc9402dda235cd69f97d1d13cb82a7, con URLs/hashes.

Orion RandomZone trae timer, auto-flag, rotación aleatoria, instancias/vallas opcionales, siete zonas ejemplo; NO voto en controladores revisados ni Elven/playa Primeval en RandomZone.xml. No es pack autónomo compatible con Mobius. Parche foro Mobius11872 localizado por índice, directo403; no auditado completo y fragmento añade Noblesse/limpia flag, incompatible con intención sin adaptar.

Sin cambios runtime/core/cliente/DB, sin ejecutar fuentes descargadas. Pendiente adaptar auto-flag a sala/franja sin borrar flag previo, reloj, votación y mapas. No afirmar que se consiguió el pack privado exacto de Damage o un módulo de voto probado.
