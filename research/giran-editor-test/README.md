# Prueba del editor con la estatua de Giran — 2026-10-14

## Resultado

Prueba parcial satisfactoria del motor/editor UE2 instalado. No se verificó la interfaz gráfica ni se instaló la variante en el cliente. El mapa vivo `E:/l2/maps/22_22.unr` conserva el mismo SHA-256 que la copia original.

- Estatua alada: actor `StaticMeshActor0`, recurso `Statues_S.statue_wingGirl_A`, posición 87301.734375 / 148628.1875 / -3070.673828125.
- UCC del paquete L2Editor carga Statues_S y sus dependencias y exporta sus cinco mallas, sin errores ni advertencias.
- Variante de prueba: ancho X aumentado 25 %, altura y profundidad originales. Se convirtió el T3D exportado a LWO2 porque este importador rechaza T3D directamente.
- Se compiló `compiler/HGStatueProbe.u` mediante UCC make y se volvió a cargar/exportar mediante UCC batchexport.
- Conserva 2270 triángulos y los cuatro materiales por nombre. Ancho de 169.540604 a 211.925750 unidades; error máximo entre posiciones esperadas y reconstruidas: 0.0000045 unidades.
- **NO está lista para producción**: el importador LWO altera UV (6810 esquinas con UV no nulos en origen frente a 522 tras reimportar). Emitió mensajes `BuildStripifyInfo: > 2 triangles on an edge... uncertain consequences`; el resumen de compilación indica 0 errores y 0 warnings. Hay que resolver importación UV y revisar normales/suavizado/colisión antes de usar este flujo para un recurso final.
- Carga del mapa completo: se preparó copia descifrada y se resolvieron dependencias en carpeta aislada; la prueba se detuvo tras 48 intentos, aún pidiendo Gl_CV_T. También hubo avisos de propiedades/funciones Engine.LocalMessage faltantes. **No demuestra que UnrealEd pueda guardar el mapa completo sin pérdidas**.
- Control de ventanas: `@oai/sky` falló con `Computer Use native pipe is unavailable`, dos intentos y otro después de reset. No se abrió/controló la interfaz del editor.

## Archivos

- `22_22.original.unr`: copia cifrada original, nunca instalar variantes automáticamente.
- `export-Statues_S/statue_wingGirl_A.t3d`: geometría exportada por el motor instalado.
- `statue_wingGirl_A_wider.t3d` y `.lwo`: variante de prueba.
- `compiler/HGStatueProbe.u`: paquete generado experimental, sin instalar.
- `roundtrip/WingGirlWider.t3d`: comprobación de recarga del paquete generado.
- `statue-verification.json`, `editor-probe.json`, `statue-import.txt`, `statue-roundtrip.txt`: evidencia y límites.
- `probe_editor.py`, `edit_statue.py`: scripts reproducibles de laboratorio. No escriben en el cliente vivo. Los logs históricos de intentos incluyen fallos intermedios que se resolvieron posteriormente.

Siguiente paso: reparar el control de aplicaciones o abrir manualmente UnrealEd para verificar la interfaz; resolver el paso de UV antes de preparar una variante instalable. Para cambiar colocación/rotación/escala de piezas existentes conviene un editor de actores compatible con L2, conservando las mallas originales.
