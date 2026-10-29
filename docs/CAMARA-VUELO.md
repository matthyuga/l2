# Camara NexusCam

Modo de vuelo confirmado por Kevin el 16/10/2026: puede desplazarse con teclado y mouse, tambien desde AnyDesk. La version instalada conserva ese mecanismo nativo y elimina el limite de dos minutos del prototipo.

Abrir **L2 - Observador NexusCam** desde el escritorio. Cuenta `nexuscamera`; contrasena en `research/camera-observer/ACCESO-PRIVADO.txt`. Elegir **NexusCam**. Se configuro entrada automatica al vuelo unos segundos despues del login; esa entrada automatica de la version permanente todavia requiere observacion manual, aunque el constructor/listener se cargo correctamente en el servidor actual.

## Controles

- Teclado y mouse: los mismos que funcionaron en la prueba.
- `.camvuelo`: abrir controles mientras esta activo; activarlo si esta detenido.
- `.camvuelo subir` / `.camvuelo bajar`: cambiar 200 de altura.
- `.camvuelo giran`, `.camvuelo coliseo`, `.camvuelo elven`: cambiar de zona sin entrar al observador fijo.
- `.camvuelo off`: retirar montura/vista de vuelo y volver al punto de partida.

Sin limite de sesion. Al desconectarse se restaura el origen y se retira el estado de vuelo. `server/game/config/CameraFlight-return.properties` guarda el retorno durante el vuelo; si hay un corte, el modulo lo recupera al arrancar para la cuenta reservada. Es estado local, no copiarlo al repositorio.

## Alcance comprobado

Se aprovechan `Player.setMount(12621,55)`, el paquete `Ride` y `CameraMode(1)`: vuelo wyvern nativo con solicitud de primera persona. La vista esta ligada al piloto volador; no es una camara independiente del personaje. Cambiar el zoom puede mostrar la montura. Mantiene invisibilidad e invulnerabilidad durante la sesion, sin otorgar GM ni cambiar el nivel del personaje.

El modo fijo `.camara` se conserva para investigacion. No usar sus destinos durante el vuelo: para navegar usar `.camvuelo`. F9/F10 y `///camerawalking` no activaron vuelo online y ya no forman parte del acceso habitual.

## Instalacion y validacion

- Modulo persistente: `server/game/data/scripts/custom/CameraFlight/CameraFlight.java`, espejo source/dist y cloud-repo (solo codigo). CameraFlight agregado a CustomScriptFolders.
- `StartMode=flight` en la configuracion privada local CameraObserver.properties. El observador fijo omite su autoentrada en esta modalidad; CameraFlight registra el inicio automatico a los 4,5 segundos y espera el fin del teleport.
- Modulo cargado mediante ScriptEngine en el GameServer actual; no se reinicio el servidor ni modifico el core.
- Smoke nativo de la version permanente: identidad reservada/no GM, rechazo de caller nulo, vuelo/montura/protecciones, movimiento habilitado a velocidad250 y limpieza sin cambiar posicion: PASS. Registro: `research/camera-observer/flight-stable-install.txt`.
- Prueba visual de la base nativa: Kevin confirmo vuelo con teclado/mouse; `flight-trial.txt` registro desplazamiento desde cerca de Giran hasta Z4604 y limpieza al desconectar. La autoentrada permanente, botones de destinos y recuperacion tras corte no se presentan como pruebas visuales realizadas.
- Los comandos temporales `.camdiag` y `.cammovil` se retiraron del registro runtime. Copias previas en `backups/camera-flight-stable-20261016`.

Para desactivar el inicio automatico: `StartMode=observer` antes de arrancar el servidor. No restaurar bases ni borrar personajes para cambiar de modo.
