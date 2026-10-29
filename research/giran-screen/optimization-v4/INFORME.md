# Nexus TV v4: optimización de 1080p — 17/10/2026

Instalado en `E:\l2-local\nexus-tv`. Se reinició únicamente el controlador, sin abrir ni cerrar clientes L2. No se cambiaron DLLs del cliente, paquetes, modelo, ubicación, resolución ni calidad JPEG (90). Canal Program_v3 y receptores anteriores conservados. Sin commit/push.

## Comparación controlada

Mismo banco, perfil fullhd (1920×1440, video 1920×1080 con bandas), navegador dedicado, salidas antiguas HD/512 y vista previa activas. Controlador normal detenido para aislar el banco. Muestras de 20 segundos por fuente después de calentamiento. Son FPS del emisor; no son FPS del motor L2 ni una prueba dentro de Giran.

| Medida | Código anterior | v4 instalada |
|---|---:|---:|
| Archivo local 1080p30: salida | 23,13 FPS | 28,59 FPS |
| Archivo local: contenido | 23,13 FPS | 28,39 FPS |
| Archivo local: tiempo medio de proceso | 37,48 ms | 20,56 ms |
| Archivo local: intervalo p95 | 82,33 ms | 56,59 ms |
| Archivo local: mayor intervalo | 136,71 ms | 84,50 ms |
| YouTube: salida | 16,8 FPS | 22,2 FPS |
| YouTube: contenido | 11,7 FPS | 20,0 FPS |
| YouTube: tiempo medio de proceso | 48,81 ms | 38,45 ms |

Fuentes: `baseline-isolated.json` y `final.json`. YouTube usó el mismo video oficial de prueba M7lc1UVf-VE y eligió hd720 en ambas pasadas. Los valores anteriores difieren de los 25–27 FPS históricos porque cambian las condiciones de ejecución. Esta comparación usa el código anterior y el nuevo en el mismo banco actual.

Mejora aproximada: +24% de salida local, −45% de procesamiento local, +32% de salida y +71% de contenido YouTube. **Todavía no se acreditan 30 FPS estables**: el promedio está por debajo y persisten intervalos de más de 33,3 ms. Tampoco se acredita reproducción 1080p nativa de YouTube mientras este elija hd720. Prueba en Giran con los clientes reales pendiente de Kevin.

## Cambios

- `decoder.py`: conversión BGR→BGRA nativa sobre un lienzo reutilizable, en lugar de asignación NumPy de tres canales con saltos de memoria. Decodificador FFmpeg limitado a dos hilos, medido frente a 1/4/8/16.
- `server.py`: cadencia basada en plazos absolutos; al exceder el presupuesto se descarta la deuda de tiempo para evitar ráfagas. Tarjetas estáticas almacenadas por tamaño.
- HD antiguo, salida 512 y JPEG de vista previa se preparan fuera del envío principal, con un único cuadro pendiente y caché para imágenes estáticas.
- Consulta periódica del reproductor separada del envío, con descarte de respuestas anteriores a una orden o cambio de fuente.
- Decodificación de JPEG del navegador fuera del bucle de eventos.
- `renderer.py`: confirmación de cuadros al consumirlos para limitar trabajo adelantado de Chrome. Se conserva el reproductor oficial y su imagen completa.
- Estado HTTP reporta `version: 4`; el ABI del canal sigue en v3.

Una variante con buffers ctypes sin copia dio 28,07 FPS y 22,85 ms medios, frente a 28,59 FPS/20,56 ms. Se descartó; no está instalada. Evidencia en `zero-copy.json`. Los resultados intermedios no representan el código final.

## Verificaciones

- Imágenes del decodificador idénticas byte por byte frente al original en tres fuentes/tamaños, incluyendo 4K, alpha opaco y saltos hacia atrás: `decoder-checks.json`.
- Pausa, seek, reanudación, cambio cámara/apagado, cambios eco/HD/4K/fullhd, canales HD/512, JPEG de vista previa y lista anterior/siguiente: `final.json`.
- Receptor D3D9 real con patrón 1080p propio pausado: **180/180 cuadros coincidentes**, Present HRESULT 0: `installed-native.json` y `installed-check.json`. La primera prueba con video animado falló por comparar muestras distintas durante el movimiento/escalado; se repitió con un patrón uniforme para eliminar esa ambigüedad. No se modificó el receptor para hacer pasar la prueba.
- Sintaxis Python compilada. Patrón temporal de verificación eliminado de biblioteca y lista.
- Estado final: controlador v4 listo, fuente cámara, perfil fullhd, volumen30, sin error. Preferencias y lista de usuario conservadas.

## Respaldo y continuación

Respaldo de los tres archivos originales: `E:\l2-local\backups\nexus-tv-opt-20261017`. Para volver: cerrar el reproductor mediante el control, restaurar `decoder.py`, `server.py`, `renderer.py` y abrir el control nuevamente. No sustituir archivos con el servicio ejecutándose.

Ejecutar el banco solo cuando no haya otra prueba en puerto8798 y evitar otras cargas durante las muestras. `benchmark.py ... --baseline --youtube` usa las tres fuentes respaldadas; `benchmark.py ... --youtube --checks` usa la versión instalada. Nunca publica sobre el canal de producción: utiliza canales de prueba separados. `verify_installed.py` sí verifica el controlador normal, con un clip temporal propio, y restaura cámara/volumen/lista al finalizar.

Siguiente evaluación: jugar en Giran con ambos clientes y medir la entrega real bajo esa carga. El transporte JPEG de Chrome sigue siendo el límite principal observado para YouTube. Audio integrado y 4K fluido continúan fuera de esta optimización.
