# Panel admin sin respuesta - 27/10/2026

Estado: causa identificada; usuario confirmó salida del personaje y se inició reinicio solo de GameServer.

- El HTML del menú contiene comandos admin válidos.
- logs/game-stderr.log registra NoClassDefFoundError / ClassNotFoundException para org.l2jmobius.gameserver.util.HtmlUtil al preparar AbstractHtmlPacket.runImpl. Afecta tanto AdminAdmin como AdminBuildLab.
- El proceso GameServer PID25292 inició el 26/10 a las 14:39; GameServer.jar fue modificado después, el 26/10 a las 23:09. Es consistente con un JAR actualizado mientras el proceso conservaba su cargador anterior.
- El JAR actual contiene HtmlUtil.class y AbstractHtmlPacket.class; lectura y CRC correctos.
- ProbeHtmlUtil.java ejecutado en JVM nueva con server/libs/*: carga HtmlUtil y resuelve buildHtmlActionCache correctamente. No requiere reparar el HTML ni desactivar validación de acciones.
- Sigue habiendo conexión de cliente al puerto7777. Se pidió salir del personaje antes de reiniciar para conservar el guardado.

No se modificó código del juego, permisos GM, validación HTML ni servidor vivo durante el diagnóstico. Próximo paso: verificar ausencia de cliente, conservar logs, reiniciar solo GameServer y comprobar arranque/error logs; confirmar botones después de reconectar.

## Reinicio autorizado

Kevin confirmó que salió del personaje. Se comprobó ausencia de conexiones establecidas al puerto7777, identidad del PID y propiedad del puerto. Se conservó game-stderr-before-restart.log y se detuvo únicamente GameServer PID25292. La ejecución directa del lanzador encontró la política PowerShell deshabilitada; se ejecutó mediante powershell.exe -NoProfile -ExecutionPolicy Bypass -File Start-L2Local.ps1. No se modificó la política permanente del sistema.

Nuevo GameServer PID5460 en arranque. Login PID17152 y MariaDB PID18012 se conservaron. Todos los parches pendientes del lanzador ya tenían marca .applied; no se aplicaron nuevas modificaciones al JAR.

Resultado: GameServer inició el 27/10 a las16:01:17, abrió puerto7777 y se registró en Login como Server2: Sieghardt. Arranque completado en78 segundos. El nuevo log no contiene NoClassDefFoundError, ClassNotFoundException, Exception in thread ni SEVERE en la revisión posterior. Falta confirmación visual del usuario al reconectar y pulsar Char/Game; no se afirma una prueba de clics que no se realizó.

Prevención: no sustituir ni actualizar GameServer.jar mientras un GameServer lo esté usando; preparar cambios y aplicarlos con el proceso detenido. Un JAR correcto en disco no garantiza que el cargador del proceso anterior pueda resolver clases tras el reemplazo.
