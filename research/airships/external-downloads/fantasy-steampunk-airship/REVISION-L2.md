# Revisión de integridad y adaptación a L2 — 14/10/2026

## Dictamen

El BLEND está completo como modelo visual y es una base viable para adaptación. No es una aeronave funcional lista para instalar: no trae sistema de pasajeros, rutas, animaciones de transporte ni colisión de cubierta verificada. No se cambió el cliente vivo ni el servidor.

Se abrió el original con Blender 5.0.1 portátil oficial, checksum SHA-256 cotejado con el índice oficial (`tools/blender-portable/download-proof.json`). La instalación Blender 3.5 se conservó. Scripts automáticos del archivo deshabilitados.

## Integridad visual

- Siete imágenes de archivo con datos válidos, todas empaquetadas dentro del BLEND. Se extrajeron a `packed-textures/`. Incluyen la cuerda que parecía faltar al inspeccionar solo el OBJ. Las rutas al equipo del autor no impiden leer estas imágenes empaquetadas.
- Se renderizó el original: casco, cubierta abierta, barandas, globo, cuerdas y aletas visibles. Imágenes: `source-perspective.png`, `source-deck.png`.
- Escena original: 21 objetos mesh (82412 triángulos evaluados) y seis objetos curve. Tras convertir las curvas a mesh: 83468 triángulos. El OBJ entregado por el autor tiene 33 objetos y 84524 triángulos; no corresponde exactamente al mismo inventario que el BLEND. No afirmar igualdad entre los cuatro formatos.
- Las ocho cuerdas mesh consumen 68544 triángulos, más del 80 % del modelo. No hay acciones de animación en el BLEND.
- Auditoría de mesh: 1410 aristas de borde y 44 aristas compartidas por más de dos caras; cero caras de área nula según Blender en esos 21 meshes. Los bordes abiertos pueden ser intencionales en tela; no suponen automáticamente un archivo roto. Para colisión debe usarse geometría independiente y simple.

## Copia de optimización y prueba nativa

Se conservó el original y se preparó `airship-probe-optimized.blend` y OBJ: solo las cuerdas mesh reciben Decimate ratio .08; curvas convertidas a mesh para exportar. Resultado: **27 piezas, 20398 triángulos**. Reducción ~75.6 % respecto de la escena original evaluada completa. Render de comparación `optimized-perspective.png` inspeccionado: conserva silueta y detalles principales a esa distancia; requiere revisar cuerdas de cerca antes de tratarla como versión final.

`l2-probe-optimized/` contiene conversión experimental LWO2 y paquete `system/HGAirshipProbe.u`:

- Conversión de unidades metros -> unidades de cliente con factor 100; ajuste de ejes OBJ/LWO/UE2.
- UCC make: salida 0, 0 errores y 1 advertencia del resumen (cuatro triángulos degenerados en Part24). Además aparecen siete mensajes de falta de xDxTex.exe para texturas provisionales; no declarar importación de materiales finales limpia.
- UCC recarga/exportación: las 27 piezas conservan los 20398 triángulos.
- UModel en modo L2 carga las 27 piezas del paquete generado. Evidencia `umodel-load-proof.json` y logs.
- VMAD añadido al LWO resuelve el colapso general de UV observado en la prueba anterior de estatua. Hay 61188 esquinas con UV no nulo de 61194; valores cero pueden ser válidos. Comparación multiconjunto redondeada a 4 decimales: coincide en 26/27 piezas; una pieza requiere revisión de tolerancias/UV. No declarar igualdad bit a bit.
- **Los materiales del paquete nativo son provisionales de color plano**, no los materiales originales de Blender. Las imágenes del original están completas, pero su conversión/bake a materiales de Interlude no está terminada.
- Primera prueba con OBJ original a escala sin factor100 guardó/recargó 33 piezas; produjo muchos avisos de geometría pequeña. La repetición a escala100 agotó 120 segundos. No usar esa prueba como paquete final. La prueba optimizada a escala100 sí completó.

## Trabajo pendiente antes de instalar como aeronave

1. Limpiar las cuatro caras degeneradas y revisar UV/materiales finales; hornear shaders de Blender cuando sea necesario y adaptar resoluciones/formatos a Interlude.
2. Revisar escala respecto de un personaje L2 y accesos reales a cubierta. El render no define capacidad de pasajeros.
3. Construir colisión simple para casco/cubierta y verificar suelo y barandas en cliente. Geodata fija no resuelve una cubierta móvil.
4. Integrar como vehículo con coordenadas relativas de pasajeros/NPCs; probar ascenso, giros, atracado y reconexión. Las pruebas actuales son del recurso, **no del transporte dentro del juego**.

Kevin autoriza, después de esta revisión, rediseñar/agregar detalles o usar el modelo como base para futuros diseños. No se tomó decisión todavía sobre el diseño final.
