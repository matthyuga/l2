# Niebla V9: circulos suaves y calculo incremental en segundo plano

27/10/2026. INSTALADA con cliente cerrado y hashes verificados. Pendiente validacion visual y medicion dentro de L2.

El usuario autorizo suavizar la disipacion tipo nube y optimizar los tirones. Se parte de V8. El diagnostico REA anterior registro reconstrucciones CPU de112-117ms en el hilo de render (research/map-fog-performance-20261027/ANALISIS.md).

## Cambios

Cada celda visitada aporta un claro circular, con nucleo totalmente despejado y caida smoothstep. Radio interior0.76celda, exterior1.25 con irregularidad espacial acotada+-0.09; mantiene totalmente visible la celda visitada, une recorridos y evita contornos cuadrados. El borde es suave espacialmente, no una animacion temporal. Conserva Giran, capas personal/global, resolucion1024x2048, transporte y progreso. La DB sigue almacenando las mismas celdas; solo cambia su representacion.

cloud_atlas.h aplica solo sellos circulares de las celdas modificadas. Conserva mascaras acumuladas, colores y Giran precalculados. Un trabajador CPU genera publicaciones inmutables fuera del hilo de render y agrupa snapshots pendientes. Eliminaciones y cambio de personaje reconstruyen la mascara completa en ese trabajador. No llama a D3D desde el trabajador. El proxy/worker permanecen cargados hasta el cierre del proceso, como los hooks existentes; no se admite descargar la DLL manualmente durante el juego.

dynamic_fog.h publica sin mantener el mutex durante el calculo; el render usa try_lock, nunca espera al trabajador. Compara versiones de512tiles y copia solo el rectangulo afectado a la textura MANAGED, exclusivamente en el hilo de render. Las versiones incluyen publicaciones que el render haya omitido. Cambiar de personaje utiliza una mascara cubierta hasta disponer de su publicacion. La construccion inicial de los recursos fijos sucede al cargar el proxy, antes del juego.

## Verificacion

30415 comprobaciones heredadas de transporte/clipping/hooks,486 comprobaciones de nubes (incremental frente a reconstruccion completa, oraculo independiente de puntos, remociones, otro personaje, extremos, publicaciones inmutables, generaciones omitidas y no-op). HAL MANAGED y SYSTEMMEM->DEFAULT: framebuffer, opacidad, estado restaurado y16Present.

Regresion grafica asincrona:3 descubrimientos actualizan framebuffer sin volver a enlazar textura/Present, recupera hooks ausentes y otro personaje queda cubierto. Publicador ocupado no bloquea (1.261ms con copia completa de cobertura de seguridad). Maximo medido de las actualizaciones de mapa en la prueba:3.388ms. Una celda nueva:1102 evaluaciones radiales y16384pixeles de transferencia frente a2097152 previos; reconstruccion completa incluyendo reset12.569ms en trabajador. Son mediciones HAL controladas, no mediciones nuevas dentro de L2. No prometer esos tiempos exactos dentro del cliente.

cloud-preview.png muestra la mascara real de produccion sobre fondo ilustrativo; se inspecciono visualmente. No es captura del juego.

## Instalacion y continuidad

install.py exige cliente cerrado, hash de V8 y NWindow/D3DDrv conocidos, y candidato igual al verificado. Solo reemplaza system-hud/d3d9.dll; guarda respaldo y log. restore.py vuelve a V8 con controles de identidad y cliente cerrado. No reinicia servidor ni modifica datos.

Validar al reabrir: log START map fog V9, revelado redondeado al recorrer, mapa chico/grande, personaje distinto y persistencia. Para medir con REA hay que generar un mapa nuevo de simbolos desde el objetoV9 y verificar .text; los RVA de V8 ya no son validos. Confirmacion visual y rendimiento real dentro del juego pendientes.

Respaldo V8: E:\l2-local\backups\map-fog-cloud-v9-20261027-212319\d3d9.dll
