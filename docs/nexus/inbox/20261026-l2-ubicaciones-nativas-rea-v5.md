# L2 — ubicaciones nativas REA V5

Proyecto E:\l2-local, cliente E:\l2\system-hud. Usuario pidió buscar todas las
ubicaciones con REA y reconocerlas. REA/Ghidra confirmó Engine.dll lookup nativo
por máscaras L2ZoneName.%d_%d, índice P8, sector, color y altura estricta. Se extrajo
ZoneName-e.dat362registros/242nombres y l2zonename.utx204máscaras128x128.354registros/
240nombres visitables validados; Talking Island genérico sin píxeles y Lyonn
inactivo no tienen ubicación válida. No afirmar242ubicaciones activas ni inventar
límites. Huntingzone220registros también extraídos para referencia.

Instalado V5 sólo servidor/fuente, sin DLL nueva, conservando niebla y variables
FOG4. Prioridad TownZone, máscara nativa, fallbackV4.2.731checks+comparación P8 con
UModel; GameServer reiniciado sin conexiones.00:16:16 log ready362registros204máscaras,
7777 PID2384. Falta prueba visual real V5. Ketra llegadaGK es Goddard Territory
según máscara; Ketra Outpost y Village al norte son diferentes. TOI distinguepisos.

Documentación/evidencia y scripts: research\exploration-locations-v5\README.md,
coverage.json, rea-*.json, installation.json. Backup
backups\exploration-native-v5-20261026-001555. ManifiestoV4 actualizado para restore.
