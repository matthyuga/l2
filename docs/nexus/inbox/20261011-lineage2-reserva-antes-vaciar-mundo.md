# Lineage2 — reserva antes de vaciar el mundo

Usuario eligió vaciar el servidor clásico y pidió primero una copia para restaurar o consultar ubicaciones/stats/drops. Se creó y validó la reserva; el servidor activo todavía no se vació ni se reinició.

Reserva: `E:\l2-local\backups\mundo-completo-antes-vaciado-2026-10-11_232156`.

Contiene ZIP de servidor/datapack/código/panel/launchers/herramientas portables, SQL consistente completo InnoDB, usuario de servicio y grants, manifiesto SHA-256, carpeta legible `referencia-clasica` (spawns/stats/zones/mapregion/teleporters/buylists/multisell), LEEME/RESTAURAR. SQL incluye datos clásicos y las personalizaciones actuales; ZIP incluye nuestros scripts.

CRC y SHA-256 de cada miembro ZIP verificados. SQL importado en instancia MariaDB aislada puerto33307:126 tablas comprobadas,39 perfiles y arma Darius6607+4 correctos. Usuario de servicio reconstruido y autenticación validada. Instancia temporal apagada; GameServer25748/7777 continúa. Evidencia `restore-verification.json`, `service-user-verification.json`, `metadata.json`, `RESPALDO-VALIDADO.json`.

No incluye cliente externo E:\l2 ni copia física caliente database/data; datos se recuperan por SQL. Logs/procesos excluidos. Reserva en mismo disco: para protección frente a falla física copiar carpeta a otro dispositivo. No trasladar archivos grandes al Nexus.

Helper `tools-src/backup-world.py`; verificador `lab-panel/scripts/verify-world-backup.js` usa instancia aislada33307. Primer intento232033 fue incompleto por permisos al consultar usuarios globales: tiene aviso RESPALDO-INCOMPLETO.md; usar232156, que guarda usuario/grants del servicio y está validado.

Pendiente: implementar mundo vacío conservando herramientas y contenido elegido. No basta NoSpawns (raids/random/script spawns independientes). NoQuests corta executeScriptList completo, incluidos custom: separar carga clásica/custom. Mantener escenario/geodata/estructura nativa necesaria para siege. Todos nacen Giran según experiencia propuesta. No se cambió configuración de carga todavía.
