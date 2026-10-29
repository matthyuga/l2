# L2: recuperación del panel admin

Proyecto E:\l2-local. Usuario reportó botones admin sin acción. Registro mostró NoClassDefFoundError para HtmlUtil en AbstractHtmlPacket al preparar validación de botones.

El JAR actual contenía la clase y pasó CRC; una JVM nueva resolvió HtmlUtil y buildHtmlActionCache. GameServer anterior inició antes de una actualización del JAR. Tras confirmación de salida del personaje y comprobación sin conexiones, se reinició solo GameServer, conservando Login y MariaDB. Nuevo PID5460, puerto7777 abierto, registro Login correcto y arranque sin errores de clase. Confirmación de clics en juego queda a cargo de la siguiente interacción.

Detalle y log previo: E:\l2-local\research\admin-html-recovery-20261027\DIAGNOSTICO.md . No se modificaron HTML, permisos ni validación. Evitar actualizar GameServer.jar con el proceso activo: aplicar cambios detenido y reiniciar.
