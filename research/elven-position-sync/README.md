# Elven: sincronizacion con cliente conectado

15/10/2026. Correccion activa sin reiniciar el servidor ni desconectar a Hellkevin.

## Problema comprobado

La primera entrada mostraba Elven y el nombre violeta brevemente. Un ValidatePosition pendiente con coordenadas de Giran sobrescribia la posicion del servidor; el controlador detectaba al personaje fuera del perimetro y completaba la salida. La traza temporal de WorldObject identifica ValidatePosition.runImpl como origen. WorldObject se restauro al terminar la instrumentacion; no se modifico su entrada del JAR.

## Cambio

RoomTeleportSync mantiene durante seis segundos una referencia a la instancia de destino. ValidatePosition y MoveToLocation rechazan coordenadas de origen incompatibles con la posicion actual autoritativa (mas de 600 unidades horizontales o 1000 verticales) y solicitan resincronizacion. Se admiten posiciones actuales y movimiento normal. La sala arma la guarda antes de viajar o devolver al ultimo punto interior y actualiza las coordenadas de cliente.

La guarda no cura, cambia efectos/cooldowns ni concede invulnerabilidad o proteccion de teleport. El plazo de sincronizacion no es el plazo de salida: la salida sigue durando cuatro segundos.

## Verificacion

- Usuario confirma que ahora permanece en Elven con nombre violeta.
- `client-verification-v2.txt`: paquetes sinteticos con origen conocido de Giran rechazados; posicion actual aceptada; cliente conectado estable durante diez segundos.
- `client-walk-verification.txt`: movimiento del AI del servidor con cliente conectado, cruzando un paso validado por geodata; cuenta iniciada al salir y cancelada al entrar, conservando instancia y flag. Salida por comando a Giran en 4097 ms, estabilidad durante siete segundos y reentrada final en Elven.
- Regresion de los handlers activos: `../elven-autoflag/verification.txt` PASS, incluido daño durante salida/cancelacion y conservacion de recursos, buff, debuff y cooldown. Auditoria final: cero personajes transitorios remanentes, cero propietarios offline y dos NPC de acceso.
- Pendiente: confirmacion visual del indicador. La automatizacion nativa no esta disponible en esta sesion; no se certifica el renderizado ni se simularon pulsaciones reales de teclado/mouse.

Se conserva `client-boundary-verification.txt`, fallo de una prueba anterior que reposicionaba abruptamente al personaje y exigia un punto interior anterior. No se usa como evidencia aprobada ni se determino su causa exacta. Se sustituyo por el cruce mediante movimiento sobre terreno validado. El primer ensayo sintetico de paquetes tampoco garantizaba una distancia suficiente entre origen y destino; V2 comprueba esa precondicion explicitamente.

## Instalacion y restauracion

Fuentes y scripts sincronizados en runtime, source y overlay. `deployment.txt` registra la redefinicion activa de los dos handlers de paquetes y el controlador; `support.jar` proporciona RoomTeleportSync a la JVM actual.

El JAR en disco sigue siendo el anterior porque esta en uso. Las cuatro clases estan en `server/pending-core-patches/20261015-elven-position-sync`. El arranque habitual `Start-L2Local.ps1` las incorpora antes de iniciar GameServer y crea `.applied`. No usar un arranque manual directo del JAR hasta aplicar esa etapa. No se reinicio al usuario para comprobar este siguiente arranque.

`baseline.json` e `installation.json` registran respaldo y hashes. Respaldo: `E:/l2-local/backups/elven-position-sync-20261015-110358`.

Para deshacer solo esta etapa con GameServer detenido: `python E:/l2-local/research/elven-position-sync/restore.py`. Primero valida que no haya cambios posteriores, los respaldos y el JAR (antes o despues de aplicar las cuatro clases); despues restaura fuentes/scripts/core y desactiva la carpeta pendiente. Para deshacer tambien auto-flag, restaurar esta etapa primero y luego la de auto-flag.
