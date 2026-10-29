# Tirones al descubrir zonas: REA en el cliente V8

27/10/2026. Analisis solicitado, sin instalar cambios ni modificar progreso.

## Resultado

La reconstruccion completa del atlas de niebla bloquea el hilo de renderizado aproximadamente 0,11 segundos por descubrimiento observado. Es una carga de calculo del parche; no hay evidencia de que estos tirones concretos se deban principalmente a cargar terreno del disco.

## Identidad y metodo

L2 PID16412, proxy V8 E:/l2/system-hud/d3d9.dll, SHA256 e7a845ebf8e7b7f223fee839398a14c7142b1be238470144171f85c020dd4750. Se relinko el objeto original solo en una carpeta de analisis para obtener simbolos; se comprobo igualdad exacta de la seccion .text con la DLL instalada. identity.json conserva hashes y RVA. No se reemplazo ningun archivo del cliente.

Dos observaciones temporales REA/Frida, desmontadas al terminar: measure-frames.js y measure-texture.js. Evidencia completa: rea-evidence.json. Los tiempos incluyen instrumentacion y tienen resolucion de aproximadamente1ms; no son un benchmark sin instrumentar.

## Observaciones

- ev_3a469a2fbe420b7ad0f986554cc729076a5584d943680befdba1ef7bcb5c5131: en19s, seis reconstrucciones reales duraron113-114ms; cada una coincide con un intervalo entre cuadros de118-122ms. Las seis corren en hilo26828, dentro de hookedPresent. Hubo4429 llamadas de presentacion y4429 de mapa. El procesamiento de362 mensajes de pantalla tuvo maximo observado1ms. El mapa sin reconstruccion tuvo maximo1ms.
- ev_c4f3c7d2f103fa8f4c147b98a2cc73d370e214aa9f22cf2cdd50e392ef08db5a: cinco reconstrucciones adicionales duraron112-117ms. LockRect tomo0ms a esta resolucion y UnlockRect0-1ms. Entre112 y117ms quedaron fuera de esas llamadas: el calculo/recorrido del atlas y demas trabajo dentro de update. Esto localiza el coste dominante en el trabajo CPU de update, no en el bloqueo de esa textura.
- Dos intervalos largos de116/126ms en la primera captura no coinciden inmediatamente con una reconstruccion; su origen no se identifico. No atribuir todos los tirones del cliente a la niebla ni afirmar descartada la carga de terreno en general.

## Explicacion del codigo

research/map-fog-live-v8-20261027/dynamic_fog.h, walking::update: si cambia revision, recorre1024x2048=2097152pixeles y escribe8MiB. En cada pixel calcula coordenadas, irregularidad, suavizado personal/global y la mascara de Giran. Lo hace sin repartir trabajo y en el mismo hilo que dibuja. Se reconstruye el continente completo aunque solo cambie una celda local. Las llamadas sin cambio de revision retornan pronto;13287 llamadas de update en19s no significan13287 reconstrucciones.

V8 corrigio la ruta de actualizacion que faltaba, pero dejo visible el coste de reconstruccion completa. La implementacion anterior ya contenia este recorrido. No hay base para culpar a insuficiencia general de RAM/GPU ni recomendar hardware por esta medicion.

## Correccion recomendada, aun no implementada

Comparar bits de snapshots y actualizar solo rectangulos afectados por las celdas cambiadas, incluyendo margen del suavizado y del jitter. Precalcular coordenadas, color y mascara fija; conservar el atlas. Para cambio de personaje/reconstruccion completa, calcular en segundo plano con publicacion coherente del resultado y mantener las operaciones D3D en el hilo permitido. Verificar equivalencia visual con el atlas actual y repetir esta medicion dentro de L2. No basta con bajar resolucion o retrasar snapshots sin medir y conservar el comportamiento.
