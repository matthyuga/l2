# HELLGAMES — Sala Elven PvP V1

14/10/2026. Trabajo real en E:\l2-local. Usuario autorizó implementar primero Elven y dejar otros mapas para después.

Implementada sala con NPC Salas PvP / HELLGAMES en Giran y muelle aéreo de Gludio (902600, modelo nativo 30146), menú Elven compartido y controlador PvpRooms dentro del folder permitido ElvenPvpRoom. Perímetro rectangular X42000..49200 Y46600..54000 Z-3800..-2000. Salida vulnerable de 4 s con indicador segmentado superior independiente de casteo; volver dentro cancela y desplaza a última posición interior; vencimiento vuelve siempre a Giran. Entrada/salida no restaura HP/CP/MP ni efectos; eliminado el fullRestore/Noblesse del ingreso y observador de revive anteriores. Posición de reingreso conservada en memoria del servidor, no persistida tras reinicio.

Compilación y pruebas en handlers activos con dos Player temporales PASS: daño durante salida y después del retorno, conservación de recursos/buff, salida >=4s, Giran, reentrada, independencia, comandos, muerte y ausencia de curación. Geodata cruzable en cuatro lados. Pendiente prueba visual humana del menú, indicador y transición del retorno en cliente; no afirmar widget gráfico personalizado ni validación visual ingame. Nueve combatientes/telemetría actuales conservados.

Servidor reiniciado durante el trabajo por otra operación, cargó scripts a19:53; posteriores cambios solo redefinieron métodos de los dos scripts sin reinicio/duplicados. No core/cliente ni commit/push. Runtime/source/overlay sincronizados. No reejecutar install.py (guard de manifest); no volver a cargar el script creando otros timers/NPCs.

Documento: E:\l2-local\SALAS-PVP-ELVEN-V1.md (también cloud-repo). Evidencias y manifest research/elven-rooms. Backup backups/elven-rooms-20261014-195242; restore.py requiere GS cerrado y verifica hashes. Restaura solo archivos registrados y vuelve a reglas anteriores de Elven.

Dependencia corregida al activar la sala: tarea nativa PvpFlaggingStopTask incorporada aisladamente al folder ElvenPvpRoom, porque el perfil custom la exclu?a y el core la invocaba para los FakePlayers. No habilitar el folder FakePlayers completo. Registro de tarea/Quest lobby PASS; manifest actual registra quince archivos.
