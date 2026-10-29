# Dust2 V7: techo invisible para cámara y rampas por piezas — 14/10/2026

Kevin reportó en V6 dos problemas: puede sacar la cámara y ver aberturas/terreno de L2 debajo del mapa; una escalera se frena a mitad de subida. Aclaró que quiere «una especie de techo invisible que no permita alejar la camara y notar los detalles de las aberturas al aire del mapa». Dejó al personaje en otra zona para la cámara. Coordenada viva de esa zona: **141496,55320,8040**, heading56194. La coordenada offline anterior141401,54851,8136 NO se considera ubicación certificada del escalón de la captura.

## Cámara

Se leyó el user.ini real del perfil HUD (`E:/l2/system-hud`) con el codec local: bUseHitCheckCamera ya era true; HitCheckCameraMinDist300 impedía una aproximación corta al obstáculo; MaxZoomingDist1800. Se cambia **solo HitCheckCameraMinDist=0**, manteniendo el zoom máximo y las demás preferencias byte por byte en el texto descifrado. Afecta la aproximación de la cámara a paredes en todo ese perfil HUD, no impone un máximo de zoom global nuevo. Se comprobó encode/decode413 íntegro.

Se preparó un cerramiento local invisible en el mapa Dust2:

-1.921 rectángulos de techo, que cubren31.234 centros de capas caminables. El límite se obtiene del primer sólido/cielo del BSP por encima del personaje, limitado además a128u sobre el suelo de cada zona.0 centros sin límite detectado. Se conserva la separación de pisos superpuestos.
-2.744 cierres verticales entre alturas distintas del techo invisible, para evitar que una junta escalonada permita escapar.
-1.286 límites laterales derivados de las paredes nativas existentes, cerrados hasta el techo correspondiente.
-Total5.951 actores de cámara, todos ocultos con deco01.Box02 original. Tienen bBlockZeroExtentTraces=true y **bBlockNonZeroExtentTraces=false**, para bloquear trazas puntuales de cámara sin añadir obstáculos de barrido al personaje. La interpretación efectiva de la cámara debe verificarse en el cliente; el test geométrico no ejecuta su función nativa de cámara.
-Cada actor lleva CollisionRadius/CollisionHeight explícitos que cubren su caja transformada; propiedades, flags y límites verificados tras releer el paquete cifrado.

En la zona dejada por Kevin, el suelo visual8000 tiene techo de cámara8128. No se cambió la apariencia visible, el clima, el cielo renderizado ni el terreno base de L2. El cerramiento pretende impedir que la cámara llegue a ver el exterior incompleto, no rellena artísticamente ese exterior. El efecto real de ocultación y la comodidad de la cámara están pendientes de prueba de Kevin.

## Escaleras

Se sustituyeron las32 rampas largas V6 por **189 piezas cortas**, de32x32u como máximo en planta, manteniendo las mismas pendientes y sus alturas. Duplicados exactos deduplicados; pequeños solapes evitan juntas. Se fijaron los límites de colisión de cada pieza. Es una prueba para el fallo de mitad de recorrido; **no se confirmó que la causa fuera el tamaño de los apoyos o sus límites de colisión**. V5 local sí tenía confirmación de subida/bajada en cliente; V6 seguía fallando en al menos una escalera.

ActoresHGDust2V7RampTile0000...; las refs de HGDust2V6Ramp se desactivaron y retiraron de myLevel. Los32 tramos conservan su superficie.1.701 rayos nativos verifican las alturas de9 puntos de cada pieza, tolerancia.01u. GeodataV6 quedó byte por byte igual; no se abrieron más bits ni se cambió la escala para intentar corregir este fallo.

Se agregó **`.dust2 escalera2`** para probar una escalera larga de referencia de6 peldaños: llegada141320,55440,8045 mirando al norte. No se afirma que sea exactamente la escalera de la captura. `.dust2 escalera` conserva la prueba inicial; `.dust2 salir` regresa. Handler runtime/source/cloud sincronizado, compilado y actualizado en vivo por redefineClasses conservando campos/estado. server-probe.txt PASS364 movimientos de la prueba original, llegada real escalera2 con Player transitorio y regreso; no se fabricó personaje persistente.

## Instalación y límites

Kevin cerró L2 expresamente antes de reemplazar archivos. Backup **E:/l2-local/backups/dust2-camera-v7-20261014-165612**,5 archivos: mapa24_19.unr, system-hud/user.ini y3handlers. GameServer9536 se mantuvo activo. Muelle/aeronave/modelos visibles y demás payloads fuera de las32 rampas previas/myLevel conservados (16.003 payloads). Ver121, CRC, roundtrip del mapa, propiedades y refs verificadas.7 manifiestos actualizados y hashes cotejados; scripts de preparación/instalación no son idempotentes y no deben reejecutarse sobre V7. Para retirar esta prueba, restaurar sus5archivos juntos y recargar/reiniciar el handler según corresponda. No usar instaladores históricos sobre el mapa actual.

Coste pendiente de observar:5.951 actores de cámara ocultos, compartiendo la misma malla nativa, más189 apoyos cortos; no tienen AI ni representación visible, pero el coste de carga/trazas de cámara del cliente no está medido. No atribuir el critical de salida a este cambio ni declararlo resuelto; sigue sin causa confirmada. Galería y bots bajo demanda intactos. Sin commit/push.

Preguntas async enviadas: (1) cámara en la zona que dejó Kevin: ¿ya queda dentro o se acerca demasiado? (2) `.dust2 escalera2`: subir, bajar y repetir; ¿completa o se frena? Esperar esos resultados antes de declarar ambos problemas resueltos. Si la cámara ignora los actores de traza puntual, revisar el tipo de traza que usa el cliente antes de seguir agregando cerramientos. Si la escalera sigue fallando, capturar coordenadas mientras está frenado en esa escalera concreta; la ubicación de la prueba de cámara no la identifica.


Actualización de prueba: Kevin confirmó que .dust2 escalera2 sube completa. Las capturas Shot00079..81 muestran que la cámara sigue escapando; cerramiento V7 no validado. Diagnóstico y siguiente prueba en ../dust2-camera-v8/README.md.
