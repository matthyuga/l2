> Modo habitual actualizado: ver [CAMARA-VUELO.md](CAMARA-VUELO.md). El vuelo nativo fue confirmado por Kevin; la parte de observador fijo de este documento queda como investigacion.

# Observador de cámara V1

16/10/2026. Cuenta dedicada para observar nuestro mundo sin usar a Hellkevin. No se modificó el core ni las cuentas/personajes existentes.

## Entrar

1. Abrir `14-ABRIR-OBSERVADOR.cmd`. Usa las herramientas y rutas del disco portátil; inicia el servidor si hace falta y abre una configuración online separada de la prueba offline.
2. Usuario `nexuscamera`, contraseña en `research/camera-observer/ACCESO-PRIVADO.txt` (local y privado).
3. Elegir `NexusCam`. El listener programa la entrada a observación en Giran dos segundos después del evento de login, si la sesión sigue conectada.
4. `.camara` abre el panel. Kevin confirmó login y vista online el 16/10; puede orientar la cámara, pero aún no avanzar/retroceder. Se agregaron F9/F10 a la copia online para probar camerawalking; requiere reiniciar el cliente.

## Comandos de la cuenta dedicada

- `.camara giran`, `.camara coliseo`, `.camara elven`: puntos de observación del mundo principal.
- `.camara ver Nombre`: ir una vez a la posición actual de un jugador conectado. No es seguimiento continuo. Las instancias privadas no están incluidas en V1.
- `.camara ir X Y Z`: cambiar el punto de observación dentro de un rango acotado.
- `.camara estado`: abrir panel y estado.
- `.camara salir`: salir del modo observador y volver al origen nativo. La cuenta sigue siendo un personaje normal sin privilegios GM cuando está fuera del modo.
- `.camara on`: activar observación desde la ubicación actual.

El modo observador nativo activa invisibilidad, invulnerabilidad y parálisis física. La cámara no recibe permisos GM. El comando exige ID de personaje, nombre y cuenta dedicados, y rechaza cualquier otro caller. No es una función pública ni VIP.

## Cliente y alcance

Cliente: `../l2/system-camera-online/L2.exe L2Protocol`, copia independiente de system-hud con su l2.ini original online y dirección local. La prueba offline sigue en system-camera-lab. Se descartó el arranque con -INI=camera-live.ini: el cliente no leyó ese archivo cifrado alternativo y lo reemplazó por una configuración mínima, causando el critical de Engine.Engine.GameEngine. La copia online conserva el nombre estándar l2.ini; ambos modos usan recursos del cliente existente. No se abrió acceso externo, configuró Sunshine/Moonlight ni modificó la red.

La prueba anterior F9 de camerawalking solo verificó el cliente offline. La cámara nativa en vivo usa ObservationEnter y necesita prueba manual de controles/alcance. No asumir que F9 esté habilitado con la configuración online. El observador recibe el entorno de su ancla; volar visualmente muy lejos no garantiza recibir jugadores/efectos de otra zona. Para mover el ancla usar .camara o sus destinos.

## Implementación y persistencia

- `server/game/data/scripts/custom/CameraObserver/CameraObserver.java`, con espejo en source/dist y cloud-repo (solo código).
- `server/game/config/CameraObserver.properties`: cuenta, personaje y hash de contraseña. Mantener local; no subir este archivo ni ACCESO-PRIVADO.txt.
- Se agregó únicamente CameraObserver a CustomScriptFolders en WorldContent.ini. Respaldo previo en `backups/camera-observer-20261016/WorldContent.ini.before`; registro de hashes en research/camera-observer/world-content-change.json.
- Al arrancar, crea la cuenta solo si no existe. Si existe con hash o privilegios distintos, falla sin sobrescribirla. Crea el personaje mediante Player.create, guarda y recarga. Si encuentra el personaje con otra identidad o privilegios, falla; nunca reemplaza otro personaje. No asigna equipo, nivel80, skills, clan o GM.
- No reinvoca enterObserverMode sobre un observador activo: reposiciona y envía ObservationEnter conservando el punto de retorno inicial.

## Verificación realizada

Compilación contra las librerías runtime correcta. Arranque GameServer completo. Cuenta y personaje creados: NexusCam, ID268436061, nivel1, accessLevel0 en ambos registros, offline al terminar el ensayo.

Probe nativo: 16 comprobaciones PASS sobre el personaje reservado offline. Revisa identidad, rechazo de caller nulo, entrada nativa, invisibilidad/invulnerabilidad/parálisis, cambio de ancla, preservación del origen, rechazo de coordenadas extremas, salida/retorno y ausencia de permisos GM. Simula fin de teletransporte con onTeleported; no equivale a un cliente real recibiendo paquetes. Limpia el personaje y lo deja offline. Agent de prueba solo invoca APIs; no redefine clases del core.

GameServer.jar mantiene el hash registrado antes: ver `research/camera-observer/verification.json`. Resultados en native-verification.txt y database-verification.txt. En el arranque se observó una advertencia previa de esquema XML de giran_lab_guardians.xml, ajena a esta instalación.

Pendientes: desplazamiento libre online y confirmación de controles F9/F10 tras reiniciar el cliente. Después: seguimiento, rutas, panel remoto y pantallas en mundo como tareas independientes.

## Desactivar

Con la sesión de cámara cerrada, retirar CameraObserver de CustomScriptFolders y reiniciar normalmente; el personaje/cuenta se conservan. El respaldo de WorldContent.ini solo debe restaurarse completo si no hubo cambios posteriores. No borrar cuentas, personajes o restaurar bases para desactivar la función.

## Resultado de controles online
Kevin confirmo que Return termina la observacion y vuelve al personaje. F9/F10 no activaron/desactivaron camera walking online tras reabrir. El binding no constituye una funcion online validada. ObserverReturn.java llama leaveObserverMode; ambos mecanismos son distintos. Se solicita prueba directa del comando de chat ///camerawalking mode=on, documentado por su autor en https://maxcheaters.com/topic/175982-solved-dev-console-commands/ (sin asegurar disponibilidad en este cliente conectado). No cambiar flags de login ni otorgar GM para esta prueba.
