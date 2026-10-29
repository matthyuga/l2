# Dust2: revisión de cámara V8 — 14/10/2026

Kevin confirmó que `.dust2 escalera2` sube completa en V7. Las capturas reales `E:/l2/system-hud/Shot00079.bmp`, `Shot00080.bmp`, `Shot00081.bmp` (16:59:50 a 17:02:09) muestran que la cámara V7 sigue escapando: vistas por encima y por debajo del escenario, terreno original y superficies exteriores incompletas. Copias PNG de inspección en `../dust2-camera-v7/qa`. No se considera resuelta la cámara.

Se comprobó que el perfil HUD conserva `bUseHitCheckCamera=true`, `HitCheckCameraMinDist=0` y `MaxZoomingDist=1800`. El problema no fue una pérdida de ese cambio al abrir el cliente.

Inspección estática del Engine.dll local, sin modificarlo: `CalcBehindView@ALineagePlayerController` resuelve a 0x1056ea50. Una llamada de comprobación a 0x1056f1dc utiliza un vector de extensión (0.1,0.1,5) y flags 0x86. `ActorNonZeroExtentLineCheck` comprueba el bit de bloqueo de barridos antes de evaluar la geometría. V7 había desactivado ese bloqueo en todos sus cerramientos de cámara. Esto justifica una prueba controlada; no demuestra todavía que sea la única causa. Hay también llamadas con extensión cero en otras ramas, por lo que no afirmar que la cámara use exclusivamente barridos. Código de inspección y desensamblados en V7, obtenidos del archivo local sin tocar el proceso.

V8 habilita `bBlockNonZeroExtentTraces` en techos y juntas V7 que no intersectan una envolvente conservadora de personaje: radio 9, desde suelo visual+2 hasta suelo+88, evaluada en todas las capas caminables contiguas de la geodata. Se excluyen las superficies de baja separación. Los límites laterales V7 y las paredes físicas V4 se conservan byte por byte. No se agregan actores ni se cambian sus dimensiones, el mapa visible, las rampas confirmadas, los comandos, el perfil de cámara o la geodata. Los techos excluidos pueden dejar zonas sin contención para este tipo de barrido: esta revisión es una prueba de la hipótesis, no una garantía de cerramiento completo.

`prepare.py` parte del mapa V7 instalado con guardia SHA. Compara todas las propiedades de cada actor modificado, permitiendo solamente el cambio de ese booleano; verifica todos los demás payloads byte por byte, el cifrado Ver121 y CRC, y relee el paquete cifrado. `verification.json` contiene los actores habilitados/excluidos. No reutilizar este script tras instalar V8 sobre el propio V8.

`install.py` exige cliente cerrado, compara hashes y los 7 manifiestos históricos, guarda copia previa y actualiza sus hashes. No reinicia el servidor. La confirmación pendiente es visual: alejar/girar la cámara en una zona abierta de `.dust2` y en `.dust2 escalera2`; comprobar además que el personaje conserva el paso. Solo después de comprobar que este tipo de colisión afecta a la cámara conviene resolver las discontinuidades restantes.

El critical al cerrar continúa sin causa confirmada. Esta revisión no pretende corregirlo.


Instalada tras cierre explícito de L2: backup E:/l2-local/backups/dust2-camera-v8-20261014-172322. Los 8 manifiestos coinciden con archivos vivos. Sin reinicio del servidor. Cámara V8 pendiente de prueba del cliente.
