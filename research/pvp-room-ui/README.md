# Interfaz PvP: confirmacion nativa y barra grafica

**Activada el 15/10/2026:** apagado ordenado sin clientes conectados y arranque normal solicitado por el usuario. Se aplicaron los dos parches pendientes. Auditoria del lobby real PASS: cuatro instancias PvP distintas (300000/300001/300002/300003), plantilla3060, dos NPC902600, tres mapas, modulo UI y bots OFF. Puertos7777/2106 disponibles. Ver `activation-audit.json` y `activation-core-audit.json`. El arranque en frio ya fue comprobado; falta observacion visual. Las descripciones de activacion pendiente abajo conservan el estado previo de preparacion.

15/10/2026. Cambio instalado en las fuentes/scripts de las cuatro salas y comprobado en instancias aisladas. **Se carga en el proximo arranque normal de las salas nuevas.** El lobby activo anterior conserva su indicador anterior mientras dure esta sesion. No se reinicio el servidor, no se movieron personajes reales y no se editaron archivos del cliente o de animaciones.

## Comportamiento aprobado por el usuario

La salida usa `ConfirmDlg`, el dialogo nativo temporizado del cliente, con cuatro segundos. Se envia una vez al iniciar la salida; el cliente anima su contador sin reenviar segmentos de texto cada tick.

- Aceptar mantiene la salida y el plazo original. No adelanta el viaje a Giran.
- Cancelar devuelve inmediatamente al ultimo punto interior de la arena, incluso desde fuera, tal como solicito expresamente el usuario.
- Volver caminando al interior sigue cancelando la salida.
- El personaje conserva HP/MP/CP, efectos, cooldowns y vulnerabilidad. El retorno interrumpe movimiento, ataque y casteo como el retorno existente.
- Una respuesta vencida, repetida o de otro dialogo no mueve al personaje.

La votacion muestra tres botones de mapa y una **barra grafica de imagenes** de 240 pixeles, con segundos restantes. No usa guiones, puntos ni segmentos de texto. Utiliza las texturas existentes `L2UI.SquareWhite` y `L2UI.SquareGray`, ya referidas por HTML del datapack.

Elegir un mapa abre la confirmacion nativa «Votar por ...?» con el tiempo restante de la votacion. Aceptar registra el voto por el comando normal de sala; Cancelar vuelve a las opciones sin votar. La confirmacion no amplia los 60 segundos ni permite cambiar un voto ya emitido. Los resultados y votos de otros siguen disponibles aunque no se vote.

El marco de las tres opciones es la ventana HTML del cliente, no una nueva ventana nativa personalizada con tres botones. La confirmacion si es el panel nativo. No se prometen dimensiones externas o posicion exactas del marco HTML: requieren revision en el cliente; no se parcheo Interface.u.

## Aislamiento de respuestas

La confirmacion emplea SystemMessageId.S1_2 (1983, texto "$s1") y requesterId propio por dialogo. Se evita S1_3 (1987), usado por acciones nativas de offline, administracion y otros scripts. Cada jugador tiene un listener durante la visita que solo consume el mensaje y token actuales; el resto se deja seguir por su handler habitual. Al salir se quitan listener y estado.

Cuando la salida o ronda se cancela por otra causa, se invalida la respuesta pendiente. No se intenta cerrar a ciegas una ventana enviando otra confirmacion vacia, porque podria interferir con una invitacion real. Hay que comprobar visualmente si el cliente cierra el aviso al cancelar caminando o lo mantiene hasta su corto vencimiento. Un aviso invalidado no puede realizar un viaje ni emitir un voto.

## Pruebas

`ui-verification.txt`: PASS sobre campos de paquete nativo (id, 4000ms, requesterId), respuestas ajenas/tokens incorrectos, Cancelar desde exterior con recursos intactos, Aceptar sin salida anticipada, vencimiento, seleccion sin voto anticipado, confirmacion/rechazo/repeticion/respuesta tardia, barra llena/media/vacia y liberacion de listeners.

`verification.txt`: regresion completa de los bots y votacion, incluyendo combate real de IA, cuatro instancias, empate3/3, duplicados6 y tardios4 rechazados, abstenciones, mayoria, mapas, siguiente ronda, respawn de bots y limpieza. Se cargaron las clases nuevas en un classloader privado del banco, sin reemplazar los scripts activos ni sus relojes.

`final-runtime-audit.json`: cero bots, propietarios de flag y miembros de reglas de prueba; lobby anterior `custom.ElvenPvpRoom.PvpRooms` activo.

`final-installation-audit.json`: 43 archivos vigentes de rondas/bots/UI comprobados por hash reconociendo los reemplazos posteriores; compilacion de todos los scripts instalados contra el core del proximo arranque aprobada. No hubo cambios al core en esta etapa.

**Pendientes:** arranque en frio y visualizacion del dialogo/barra en system-hud. Las pruebas de servidor no certifican estilo, posicion, cierre visual del aviso ni compatibilidad de renderizado de una variante de interfaz. No se enviaron estos paneles de prueba al cliente de animaciones.

## Respaldo y restauracion

Manifiesto: `installation.json`. Respaldo: `E:/l2-local/backups/pvp-room-ui-20261015-135414`. Seis archivos modificados/agregados en runtime, source y overlay.

Con GameServer detenido: `python E:/l2-local/research/pvp-room-ui/restore.py`. Rechaza cambios posteriores y devuelve la interfaz anterior conservando bots y salas. Orden de rollback completo: UI, bots, rondas, sincronizacion de posicion y auto-flag.
