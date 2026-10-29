# Amber: modelos descargados y comparacion — 2026-10-23

Se descargaron dos distribuciones MMD/PMX de Amber y se compararon con el VRM de Koikatsu y la adaptacion Blender para L2. No se modifico ningun archivo instalado del cliente o servidor.

## Procedencia y archivos

Indice: https://mmdfr.fr/genshin-mmd/
Respuesta publica utilizada: https://api.mmdfr.fr/api/character/Amber

- `amber-mmd-v10.rar`: indice1.0, 4.700.645 bytes. URL https://static.biligame.com/caster_custom_assets/ys/gczj/anbo.rar
- `amber-mmd-v14.zip`: indice1.4, 3.959.338 bytes; carpeta interna `安柏2.0`. URL https://activity.hdslb.com/blackboard/static/20210316/4d40bc4f98f94fbc71c235832ce3efd4/ApoSncaZI8.zip
- Descomprimidos en `v10` y `v14`. Cada uno contiene PMX, seis texturas y reglas. SHA256 y URLs guardados en `provenance.json`.

El indice los presenta como modelos oficiales. Los archivos atribuyen copyright a miHoYo y edicion a 神帝宇. Son distribuciones para MMD: no se ha establecido que sean los mismos archivos internos utilizados por el juego. La version del indice1.4 y el nombre de carpeta2.0 son etiquetas diferentes, no dos descargas adicionales.

Los textos incluidos permiten ajustes descritos de esqueleto, cuerpos rigidos y UV; prohiben redistribucion y uso comercial, entre otras condiciones. Se conservan los originales. No se copian modelos ni texturas a GitHub/Nexus. Este informe no interpreta la licencia como permiso general para publicar una conversion a otro juego.

## Datos medidos

| Dato | MMD indice1.0 | MMD indice1.4 / Amber2.0 | Adaptacion actual L2 |
| --- | ---: | ---: | ---: |
| Vertices | 31.405 | 12.598 | 33.470 |
| Triangulos | 47.378 | 15.794 | 52.153 |
| Materiales | 8 | 8 | 2 |
| Texturas referenciadas | 6 | 6 | 2 atlas2048x2048 |
| Huesos totales | 160 | 160 | 76 del esqueleto destino |
| Huesos con pesos positivos | 101 | 85 | No medido en esta comparacion |
| Morphs PMX | 49 | 47 | No es una medida equivalente del PSK |
| Cuerpos rigidos | 52 | 52 | No implementados por este analisis |
| Articulaciones fisicas | 36 | 36 | No implementadas por este analisis |

MMD: parser leyo los archivos completos (1.996.966 y913.705 bytes), verifico indices de vertices, suma de caras por material y existencia de todas las texturas. Informes `v10-analysis.json`, `v14-analysis.json`; geometria separada en JSON para reproducir vistas. No se ejecuta codigo del modelo.

L2: inventario de `exports/amber-l2-rigged.blend`: cuerpo8.559 vertices/12.980 triangulos; traje24.911 vertices/39.173 triangulos. Conteos por objeto, sin soldar vertices de objetos diferentes. Referencias de huesos segun `reports/amber-build.json`.

Origen Koikatsu: `amber-imported.blend` contiene cuerpo24.678 triangulos y outfit46.088 (70.766 entre los dos objetos principales), mas objetos auxiliares/variantes no incluidos en las vistas. VRM original40 materiales/40 texturas y847 huesos; ese numero incluye estructuras que no deben interpretarse como847 huesos necesarios de deformacion. Las diferencias de triangulos y huesos no bastan para medir rendimiento.

## Hallazgos entre las dos descargas

Las seis texturas son identicas por SHA256. Cara, cabello y ropa usan mapas2048x2048; sphere map512x512, toon800x800 y expresiones1181x1181.

Entre1.0 y1.4 los conteos de triangulos de blanco de ojos1026, cara1648, ojos196, cabello1694, accesorio260 y expresiones442 no cambian. Piel3532->883 y ropa38580->9645. Eso explica la mayor parte de la reduccion; no se ha demostrado identidad de todos los vertices/pesos de las partes con igual conteo.

Los materiales separan blanco de ojos, cara, ojos, piel, pelo, ropa, accesorio y expresiones. Algunos usan sphere mode2 y toon externo. Existe informacion de sombreado aparte del color base. Esto no equivale al shader completo de Genshin ni a una garantia de apariencia identica al juego.

## Comparacion visual reproducible

- `comparison-face.jpg`: referencia MMD1.4 frente a nuestra adaptacionL2.
- `comparison-full.jpg`: cuerpo completo de ambos.
- `comparison-three-stages.jpg`: MMD, Koikatsu/VRM importado y adaptacionL2.
- `reference-texture-sheet.jpg`: seis texturas del MMD.
- `amber-mmd-reference-basecolor.blend`: escena de inspeccion de geometria, UV y color con texturas empaquetadas. NO es una importacion completa: no reconstruye esqueleto, morphs, fisicas, toon ni sphere shader. Los PMX originales conservan esos datos.

Vistas ortograficas frontales, encuadre normalizado a la altura total, color base mediante emission, transformacion Standard y sin iluminacion direccional. Se usan UV originales y alpha de textura. No reproducen el shader original de ninguno de los modelos, sus contornos ni el render de L2. La vista del origen es del VRM importado, no captura directa de Koikatsu.

La diferencia observable incluye proporciones de ojos/cara y cuerpo, silueta y limpieza de detalles del traje. Los colores base del MMD y del origen Koikatsu tambien difieren. No atribuir automaticamente los artefactos del render de color base a corrupcion del modelo: materiales superpuestos y mezclas originales no estan reconstruidos en esta prueba.

Blender advirtio dos shape keys auxiliares con referencia invalida al abrir el blendL2 (`Gag Eyes.baked` y `Tears.baked`). Solo se leyo en memoria y no se guardo sobre el original. Esa advertencia no demuestra fallo de la malla que esta instalada en L2.

## Puente recomendado

1. Usar MMD1.4/Amber2.0 como referencia inicial: tiene unas3,3 veces menos triangulos que nuestra adaptacion, pero ese dato solo no determina calidad o velocidad.
2. Importacion MMD completa en copia de trabajo: reconstruir8 materiales,47 morphs, jerarquia, pesos, IK y fisicas; verificar contra los PMX y no contra esta escena de color base simplificada.
3. Aprobar un modelo maestro Blender con rostro, colores y material toon, separado por cara/ojos/pelo/ropa cuando necesiten comportamiento diferente.
4. Crear derivado para L2: mapear al esqueleto76, validar deformacion de hombros/codos/manos y arco; adaptar materiales a UE2. No sustituir este paso por aplanar indiscriminadamente todo a dos atlas.
5. Comparar maestro y derivado con camaras/poses equivalentes en Blender y despues capturas reales de L2. El shader de Blender/MToon no se exporta como comportamiento ejecutable a UE2.

La actual Amber queda conservada como base funcional. Este trabajo completa descarga, inspeccion estructural y primera comparacion visual; no instala ni declara lista una nueva Amber para combate.

Reproduccion: `scripts/compare_amber_pmx.py`, `inventory_amber_reference.py` y `render_amber_model_comparison.py` (Blender5.0.1). El analisis de formatos y escenas se realizo con herramientas especificas; no se atribuye a REA una ejecucion que no se hizo.
