# Dust2 V6: soportes inclinados para las demás escaleras — 14/10/2026

Kevin confirmó V5: «bien, ya se puede en esa, faltaria las demas». Esa confirmación valida la subida/bajada del soporte local V5, no todas las escaleras V6. Se extendió el mismo principio a32 tramos detectados. Critical de salida sigue separado, sin causa ni solución confirmadas.

## Detección y preparación

Se usaron las31.234 capas apoyadas por los pisos V4 y la geometría original de las37 mallas, con la misma escala1.0 y espejoY corregido. Se distinguieron superficies horizontales reales de las aproximaciones por celdas de rampas visibles. Se tomaron frentes de peldaños de4..18u (principalmente16u), ancho mínimo de detección32u, y se agruparon risers consecutivos del mismo ancho en ambas direcciones. Resultado41 frentes/32 vuelos, incluyendo tramos de2/3/4 peldaños. No se agregaron rampas a las caras de cajas/plataformas de32u: una primera auditoría más amplia mostró que esas caras generaban soportes perpendiculares que invadían escaleras reales.

Cada tramo usa una o más franjas físicamente comprobadas, dejando fuera partes junto a pared/techo o suelo de otro nivel. Se permiten franjas de16u en bordes estrechos; el soporte y las paredes originales continúan alrededor. Se prolonga la aproximación cuando el punto inicial nominal quedaría flotando sobre un peldaño previo. Los apoyos mantienen la pendiente de referencia≈26.565° de V5. El perfil visible de los escalones no cambia: un plano invisible puede separar algo los pies de peldaños durante la subida, como en la prueba validada por Kevin.

Actores nuevos **HGDust2V6Ramp000..031**, todos deco01.Box02 original, espesor normal4u, rotación Pitch paraX o Roll paraY y pequeños solapes. Se desactivó y retiró la referencia del soporte local HGDust2V5RampExample, sustituido por las pendientes generales equivalentes de esa escalera. La orden `.dust2 escalera` sigue disponible y conserva destino/orientación. No se cambiaron handlers, modelos visibles, UV, escala ni equipamiento.

## Geodata y verificación

-32 soportes;1.380 rayos sobre las mallas nativas transformadas verificaron las pendientes y sus extremos, tolerancia.02u.
-1.016 muestras adicionales del perfil conjunto (rampas + pisos previos) no encontraron bordes ascendentes discontinuos en las entradas, recorridos y salidas centrales de los tramos.
-271 alturas de geodata ajustadas dentro de las huellas de las rampas;0 bits NSWE añadidos. Se preservaron otras capas y regiones. Datos intermedios de candidatos rechazados quedan en excluded.json.
-`server-probe.txt`: **32 rampas,1.668 comprobaciones bidireccionales,0 segmentos fallidos**, incluidas entradas y salidas y3 líneas a lo ancho de cada rampa.
-`server-smoke.txt`: PASS40 inicios,192 subidas anteriores, pasos abiertos/cerrados, capas, paz/respawn, CT/T, regreso y pisos de muelle/nave/Coliseo.
-Ver121, CRC y roundtrip íntegros. Actores anteriores preservados byte por byte salvo myLevel y el soporte local V5 desactivado; verification.json tiene el recuento. Se verificaron32 refs activasV6 y ausencia de la refV5 en myLevel.
-Los6 manifiestos de instalación coinciden con los archivos vivos después de instalar.

La prueba geométrica y del servidor **no certifica la física completa del cliente** ni todos los movimientos posibles de todas las razas. El patrón de soporte sí tiene confirmación de Kevin en V5. V6 requiere recorrido ingame por otros sectores.

## Instalación y continuidad

Cliente E:/l2 estaba cerrado al reemplazar el mapa (comprobación de proceso), sin pedirle otro cierre al usuario. GameServer9536 siguió activo y recargó24_19 con API nativa; no se reinició ni se movió al personaje. Backup combinado **E:/l2-local/backups/dust2-ramps-v6-20261014-163546**, mapa + geodata y copias de manifiestos anteriores. Restaurar mapa y geodata juntos para volver a V5, con hashes comprobados, y recargar la región. No reejecutar prepare/install sobre el estado ya instalado ni usar instaladores históricos de muelle/nave/Dust2.

Galería y perfiles de combate bajo demanda siguen como estaban. No se tocaron DLLs/audio/shaders ni se aplicó una supuesta solución al critical. Sin commit/push.

Pendiente: Kevin debe recorrer las demás escaleras; si queda una, capturar posición viva ante el bloqueo y comprobar si es un tramo no detectado (diagonal/curvo), una entrada lateral o una colisión de otro nivel. No dar por confirmadas todas las escaleras solo por el PASS del servidor.
