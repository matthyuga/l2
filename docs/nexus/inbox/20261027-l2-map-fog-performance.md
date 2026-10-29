# L2: tirones por reconstruccion de niebla

27/10/2026. Analisis REA solicitado. V8 instalada y revelando; en L2 PID16412 se midieron11 reconstrucciones del atlas de112-117ms en el hilo de render. Seis coinciden con gaps118-122ms. LockRect0ms/UnlockRect0-1ms: coste dominante fuera de bloqueo de textura, en calculo CPU completo1024x2048 por revision. Mensajes max1ms. Otros dos gaps sin reconstruccion no explicados; no descartar carga de terreno general.

E:/l2-local/research/map-fog-performance-20261027/ANALISIS.md y rea-evidence.json. No se instalaron cambios en esta investigacion. Recomendacion pendiente: actualizacion por regiones cambiadas y precalculo de datos fijos; reconstrucciones completas fuera del hilo de render con publicacion coherente.
