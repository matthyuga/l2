# Bitácora: niebla del mapa, diagnóstico y optimización

Guardada el **28/10/2026**, con lo trabajado durante el 27/10 y esta conversación.

Proyecto: `E:\l2-local`. Cliente: `E:\l2\system-hud`.

## Estado para retomar

**V9 instalada. Pendientes la confirmación visual del usuario y una medición de rendimiento dentro de L2 con V9.** Las pruebas aisladas pasaron; no confundirlas con una validación completa dentro del juego.

El usuario pidió que la niebla se disipe al explorar, con claros circulares, bordes suaves e irregulares tipo nube, y menos tirones. Se implementó e instaló esa representación. Las visitas siguen almacenándose en las mismas celdas: no se borró ni migró progreso.

Archivo instalado: `E:\l2\system-hud\d3d9.dll`.

SHA256 de V9:

`a93edc738847000f5eed39ab44fcba0ca2ab49fd36392efbbac64540fd524b4d`

Fuente, pruebas y documentación actuales: [research/map-fog-cloud-v9-20261027/README.md](research/map-fog-cloud-v9-20261027/README.md).

## 1. El mapa recibía descubrimientos, pero no los mostraba

El usuario mostró zonas recorridas todavía cubiertas. El log de V7 confirmaba la recepción de snapshots completos de exploración personal/global, pero no registraba las actualizaciones esperadas al dibujar.

REA/Frida observó el cliente V7 abierto, PID3116. El dispositivo real tenía una tabla de funciones D3D cuyos slots17/65/81/82/83/84 apuntaban al D3D9 de Windows, sin los hooks del proxy. Se observaron llamadas reales de presentación y dibujo en esa tabla. Eso confirmó la ruta que faltaba; **no se determinó quién retiró los hooks ni si se sobrescribió o sustituyó la tabla**.

Evidencias:

- `ev_16fee0eb3f65684e7e637438a46f0047cd0e6860f370a57a98747480b498a03a`
- `ev_ddaf71455621815462b00470e640dec7b1e5f304da8b47edb93505b8bde80e10`

V8 añadió actualización desde el dibujado nativo del mapa y reparación de los hooks de la tabla activa. Una prueba HAL reprodujo el mapa congelado al retirar los hooks y pasó con la reparación. V8 se instaló después de que Kevin confirmara el cierre del cliente. El diagnóstico posterior observó actualizaciones reales de exploración dentro de L2.

Detalles: [research/map-fog-live-v8-20261027/README.md](research/map-fog-live-v8-20261027/README.md).

## 2. Tirones al descubrir: medición real con REA en V8

El usuario preguntó si las trabas se debían a cargar zonas. Se midió el cliente abierto PID16412 mediante instrumentación temporal, desmontada al terminar.

La identidad del código se verificó: se obtuvo un mapa de símbolos al reenlazar el objeto original en una carpeta de análisis y se comprobó igualdad exacta de la sección `.text` con la DLL instalada. No se reemplazó el cliente para medir.

Resultados observados:

| Medición | Resultado |
|---|---|
| Seis reconstrucciones de niebla, primera captura | 113–114 ms cada una |
| Intervalos entre cuadros coincidentes | 118–122 ms |
| Cinco reconstrucciones adicionales | 112–117 ms |
| Procesamiento de mensajes de pantalla | Máximo observado 1 ms |
| `LockRect` de la textura | 0 ms a la resolución de la medición |
| `UnlockRect` | 0–1 ms |

Las reconstrucciones se ejecutaban en el hilo de renderizado. El código recorría **1024 × 2048 = 2.097.152 píxeles**, calculando la máscara completa y escribiendo 8 MiB cada vez que cambiaba la revisión, incluso al descubrir una sola celda.

Conclusión respaldada: el coste dominante de esos tirones estaba en el cálculo CPU de la niebla. No había base para recomendar más RAM/GPU ni atribuir esas pausas principalmente a lectura de terreno. **También hubo dos pausas de 116/126 ms sin reconstrucción inmediata; su causa quedó sin identificar. No se descartó la carga de terreno como causa de otros tirones.**

Los tiempos incluyen instrumentación y tienen resolución aproximada de1ms. Las13.287 llamadas a `update` en19s incluían retornos rápidos; no equivalían a13.287 reconstrucciones.

Evidencias:

- `ev_3a469a2fbe420b7ad0f986554cc729076a5584d943680befdba1ef7bcb5c5131`
- `ev_c4f3c7d2f103fa8f4c147b98a2cc73d370e214aa9f22cf2cdd50e392ef08db5a`

Informe y evidencia conservados:

- [ANALISIS.md](research/map-fog-performance-20261027/ANALISIS.md)
- [rea-evidence.json](research/map-fog-performance-20261027/rea-evidence.json)
- `research/map-fog-performance-20261027/identity.json`
- `research/map-fog-performance-20261027/measure-frames.js`
- `research/map-fog-performance-20261027/measure-texture.js`

Ese informe refleja el diagnóstico anterior a V9; su sección «corrección recomendada, aún no implementada» es histórica. La implementación posterior se describe abajo.

## 3. V9: claros circulares, suaves y actualización optimizada

Kevin pidió reemplazar el aspecto cuadrado por una disipación circular tipo nube y autorizó hacerla más suave y optimizada.

Implementación:

- Cada celda visitada aporta un claro circular. Los claros se unen a lo largo del recorrido.
- Núcleo despejado y caída `smoothstep` en el borde, con irregularidad suave anclada al mundo. Radio interior0,76celda; exterior1,25, con variación máxima±0,09.
- El suavizado es espacial. No se agregó una animación temporal de desvanecimiento.
- Se mantienen Giran despejada, capas personal/global, resolución del atlas y transporte de descubrimientos.
- Se precalculan colores y máscara fija. El cálculo se limita a las celdas que cambian.
- Un trabajador CPU construye publicaciones inmutables fuera del hilo de renderizado y agrupa snapshots pendientes.
- D3D sigue ejecutándose en el hilo de renderizado. Se copian únicamente los rectángulos afectados, identificados mediante versiones de512tiles.
- El render usa `try_lock`: no espera a que termine el cálculo de fondo.
- Eliminaciones y cambios de personaje reconstruyen la máscara en el trabajador. Mientras se prepara otro personaje, se usa cobertura para no mostrar exploración ajena.
- Las publicaciones omitidas se recuperan correctamente mediante las versiones de tiles.

Archivos principales:

- `research/map-fog-cloud-v9-20261027/cloud_atlas.h`
- `research/map-fog-cloud-v9-20261027/dynamic_fog.h`
- `research/map-fog-cloud-v9-20261027/map_fog.cpp`

## 4. Pruebas de V9 y límites de lo comprobado

Pasaron30.415 comprobaciones heredadas y486 específicas de la máscara circular: reconstrucción incremental frente a completa, oráculo independiente de puntos, bordes del mundo, eliminaciones, cambio de personaje, publicaciones inmutables, generaciones omitidas y snapshots sin cambios.

Pruebas HAL con texturas MANAGED y subida SYSTEMMEM→DEFAULT: framebuffer final, opacidad, restauración de estado y16Present. Regresión gráfica asincrónica: tres descubrimientos actualizan la imagen sin volver a enlazar la textura ni depender de Present; se recuperan hooks ausentes y otro personaje permanece cubierto.

Mediciones controladas:

| Caso | Resultado |
|---|---|
| Una celda nueva | 1.102 evaluaciones radiales |
| Transferencia de esa celda | 16.384 píxeles, frente a2.097.152 del atlas completo |
| Máxima actualización de mapa medida en la prueba HAL | 3,388 ms |
| Publicador ocupado, incluyendo cobertura de seguridad | 1,261 ms |
| Peor construcción de fondo de la prueba, incluyendo reinicios completos | 12,569 ms |

**Los tiempos HAL no son directamente comparables con la medición REA dentro de L2 y no garantizan esos valores exactos en el juego.** Falta repetir el perfil dentro del cliente V9.

Se generó e inspeccionó [cloud-preview.png](research/map-fog-cloud-v9-20261027/cloud-preview.png), usando la máscara de producción sobre un fondo ilustrativo. No es una captura del juego.

Registro estructurado: [verification.json](research/map-fog-cloud-v9-20261027/verification.json).

## 5. Instalación, conservación y restauración

V9 se instaló el27/10 después de verificar que L2 estaba cerrado. Se comprobó la identidad del candidato y de los archivos base. **Solo se reemplazó `d3d9.dll`.** Servidor, progreso, HSL, NWindow y D3DDrv se conservaron.

Respaldo de V8 anterior a V9:

`E:\l2-local\backups\map-fog-cloud-v9-20261027-212319\d3d9.dll`

Manifiesto: [installation.json](research/map-fog-cloud-v9-20261027/installation.json).

Para volver a V8, con el cliente cerrado y solamente si se decide revertir:

```powershell
python research/map-fog-cloud-v9-20261027/restore.py
```

El restaurador valida los hashes del archivo instalado y del respaldo antes de copiar. No ejecutar para «probar» ni reinstalar versiones históricas sobre modificaciones posteriores.

Otros respaldos de esta secuencia:

- Antes de V8, respaldo V7: `backups/map-fog-live-v8-20261027-205003/d3d9.dll`.
- Antes de V7: `backups/map-fog-refresh-v7-20261027-165127/d3d9.dll`.

## 6. Pendientes para la próxima sesión

1. Confirmar con Kevin el aspecto circular y el borde suave durante un recorrido real por terreno nuevo.
2. Verificar mapa pequeño/ampliado, persistencia al reconectar y cambio de personaje.
3. Medir V9 con REA durante descubrimientos y comprobar cuánto bajaron los tirones reales.
4. Generar símbolos nuevos desde el objeto de V9 y verificar identidad antes de instrumentar: **los RVA de V8 no sirven para V9**.
5. Si siguen existiendo pausas, separar las que coincidan con actualización de niebla de carga de terreno u otras funciones.

El crítico previo de `UpdateAnimation` sigue siendo una investigación separada; estas correcciones no se presentaron como solución de ese cierre.

No afirmar confirmación visual o rendimiento dentro de L2 con V9 hasta obtener esa evidencia. Esta bitácora no añade modificaciones al juego.
