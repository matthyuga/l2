# Lineage II Interlude local — auditoría de continuidad

Fecha: 2026-10-06
Sesión: Codex en PC principal
Rutas reales revisadas: `E:\l2` y `E:\l2-local`

## Resumen

- `E:\l2` contiene el cliente Interlude y variantes `system-clean`, `system-hud`, `system-local` y `system-solo`.
- `E:\l2-local` contiene L2J Mobius, MariaDB portátil, fuente, backups y dos interfaces locales:
  - `lab-panel`: personajes, rivales, clases, skills y telemetría.
  - `idea-lab`: 18 ideas, 3 decisiones y seis conversaciones fuente en modo lectura.
- El `GameServer.jar` desplegado coincide por SHA-256 con el último build de la fuente.
- Los XML personalizados principales se cargan como XML válido y las interfaces pasan control de sintaxis Node/PowerShell.

## Hallazgos importantes

1. El disco está actualmente en `E:`, pero los accesos normales del servidor, cliente y panel todavía fijan `D:\l2-local` y `D:\l2`. Esos accesos no funcionan en esta PC. Los modos portátiles `9-ABRIR-LAB-IDEAS.cmd` y `11-ABRIR-LAB-L2-OFICINA.cmd` sí calculan la ruta desde el disco.
2. La fuente Git está basada en un único commit upstream y conserva 17 archivos modificados más 5 archivos nuevos sin commit. Debe hacerse un checkpoint antes de seguir desarrollando.
3. `server\game\config\Custom\FakePlayers.ini` está configurado para la arena, pero su copia en `source\...\dist\game` conserva valores upstream. Una reinstalación desde la fuente podría desactivar o cambiar el comportamiento de Ares/Nyx.
4. Hay un error histórico real de Build Lab: intento de subclase duplicada para Hellkevin (`Duplicate entry '268473899-38'`). Conviene reproducir y corregir la operación para que sea idempotente.
5. Los avisos Hikari de conexiones caducadas son de mantenimiento de pool; el servidor siguió funcionando. El error de puerto 9014 pertenece a un arranque duplicado anterior.
6. Todo está limitado a `127.0.0.1`; no hay exposición de red pública.

## Próxima acción sugerida

Hacer primero una fase de estabilización: volver portátiles todos los lanzadores, sincronizar `FakePlayers.ini`, crear un commit/checkpoint y luego probar en esta PC el arranque completo, Build Lab y una pelea con telemetría.

## Actualización — Windows 10

La fase de portabilidad fue aplicada el mismo 2026-10-06:

- accesos normales, servidor, panel y herramientas auxiliares ya no dependen de `D:`;
- `FakePlayers.ini` quedó sincronizado;
- la entrada de `hosts` fue instalada;
- MariaDB, Login Server, Game Server, panel y cliente HUD arrancaron correctamente desde `E:`;
- no fue necesario copiar el proyecto al disco interno;
- los originales están en `E:\l2-local\backups\portable-paths-2026-10-06`.

Pendientes posteriores: checkpoint Git, corrección defensiva de la subclase duplicada y prueba manual dentro del mundo con telemetría nueva.

Archivos de continuidad principales:

- `E:\l2-local\README-ES.txt`
- `E:\l2-local\ARENA-DE-PRUEBAS.txt`
- `E:\l2-local\BITACORA_LABS_PORTATILES_2026-10-06.md`
- `E:\l2-local\idea-lab\data\workspace.json`

## Actualización 2026-10-07 — respaldo en GitHub

- Repositorio público: `https://github.com/matthyuga/l2`.
- Commit publicado: `a5aae7b` (`Add L2 Interlude lab project snapshot`).
- Incluye paneles, documentación, scripts, notas, resultado final de Fase 4D y
  overlay de cambios sobre L2J Mobius.
- Excluye cliente, binarios, herramientas, base activa, credenciales, logs, perfiles
  de navegador y backups completos.
- La acción de GitHub `Validar snapshot` terminó con resultado correcto.
- El proyecto quedó registrado en `projects.md`, `sessions/lineage2-local.md` y
  `links/lineage2-local.path.txt`.

## Actualización 2026-10-07 — Fase 5A

- Línea base 4D etiquetada: `phase4d-baseline-2026-10-07`.
- Nuevo commit público: `eedb912` (`Start Phase 5 external comparison and Nyx calibration`).
- L2Nyx quedó registrado como primer servidor externo con fuentes y diferencias.
- Calibración interna: 360/360 pasadas, cero fallos; 90 por escala 100/75/60/50.
- Ninguna escala llegó al objetivo de 10–20 s; siguiente ronda sugerida 30/25/20%.
- Nyx original no se modificó; los 285 resultados de 4D quedaron intactos.
- Acción GitHub `Validar snapshot` #3: correcta.
