# HELLGAMES: salida/voto con interfaz grafica

Usuario rechazo barra textual y pidio panel estilo invitacion party/trade/clan. Despues confirmo explicitamente: Cancelar devuelve al punto interior anterior, aun desde fuera. Aceptar mantiene cuenta4s, no salida inmediata. Caminar dentro tambien cancela. Sin curacion/inmunidad añadida.

Trabajo E:/l2-local/research/pvp-room-ui. Seis fuentes/scripts instalados. PROXIMO ARRANQUE NORMAL de cuatro salas; no reinicio, movimientos de jugadores ni cambios cliente/core. Sesion animaciones preservada. Lobby anterior aun activo y muestra indicador anterior hasta reinicio.

Salida: ConfirmDlg native4s, requesterIdtoken, SystemMessage1983 S1_2 para evitar colision con S1_3 offline/admin. Voto: tres opciones HTML y barra grafica SquareWhite/Gray240px; elegir abre confirmacion nativa con plazo restante, Aceptar vota una vez por onCommand, rechazar no vota. No se modifico Interface.u ni se afirma ventana HTML externa nueva/pequeña.

Tests aislados PASS: paquete/tiempo/token, respuestas ajenas, Cancelar fuera mantieneestado, Aceptar noadelanta, stale/replay/late, barra llena/media/vacia, cleanup. Regresion bots/combate/votos PASS. Auditoria43archivosvigentes y cerobots/owners/membresia. Compilacion todos scripts proximoarranque PASS.

Pendientes cliente: render, posicion/tamaño y cierre visual al cancelar caminando; respuesta invalidada noactua aunque popuppermanezca hasta4s. Sin actualizacion ciega con dialogovacio para no cerrar invitaciones ajenas. Leer README con evidencia/limites.

Backup backups/pvp-room-ui-20261015-135414; rollback hashguard detenido. Orden: UI,bots,rondas,sync,autoflag. Verificador UI entiende manifiestosencadenados; verificadores anteriores detectan hostposterior como corresponde.
