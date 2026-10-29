# Lineage II: regreso de W11 a W10 revisado

Fecha: 10/10/2026, Buenos Aires. Sesión de origen: Codex, revisión del regreso.
Ruta real: `E:\l2-local`; cliente: `E:\l2\system-hud`.

La memoria de K: conservaba el estado anterior al viaje. El cierre actualizado viaja en `E:\l2-local\CONTINUIDAD-W10\LEER-PRIMERO.md`.

- Inventario de salida verificado: 54/54 archivos SHA256 correctos; SQL de respaldo también coincide. Utilizar la base operativa del disco, posterior al guardado final, sin restaurar ese SQL.
- Amber terminó W11 con 61 checks PASS y animaciones de ataque confirmadas. Pendientes: nuevos efectos de arco/fuego/lluvia, duración y recarga dentro del cliente.
- W11 también amplió el arranque a 600s, reparó iconos Amber y convirtió el Coliseo a rivales por duelo (63 checks de spawns PASS). GroupAgite smoke PASS; ensayo manual y clanes pendientes.
- W10 confirmado. Servicios y cliente detenidos. No se arrancó ni se ejecutaron probes en esta revisión.
- Corregidas dos rutas MySqlBinLocation D: -> E: en configs privadas game/login, con respaldo en `backups/retorno-w10-rutas-2026-10-10`. Arranque principal usa rutas dinámicas y --no-defaults.
- Cambios locales sin commit/push. Core y recursos conservados.

Acción sugerida: integrar este cierre al resumen `sessions/lineage2-local.md` al actualizarlo; consultar antes la nota local `CONTINUIDAD-W10/13_REVISION_RETORNO_W10_2026-10-10.md`. Próximo arranque normal una sola vez, confirmar 19 perfiles preparados y continuar revisión visual.
