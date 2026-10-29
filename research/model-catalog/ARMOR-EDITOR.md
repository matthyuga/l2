# Taller de armaduras de Lucien

Abrir `EDITOR-ARMADURAS-L2.cmd` desde la raíz del proyecto, usar el enlace de la galería o visitar `http://127.0.0.1:32280/armor-editor.html` con el servicio activo.

## Uso

1. Lucien aparece como base de ajuste con un torso neutro. El selector también ofrece la versión original con su ropa.
2. Elegir categoría y origen en la biblioteca. Cada pieza tiene miniatura y botón Añadir. El conjunto Carmesí V2 se puede cargar completo.
3. Seleccionar una pieza en la escena o la lista de montaje. Mover con W, girar con E y cambiar tamaño con R usando los ejes del visor. Los campos de la derecha permiten valores exactos en centímetros, grados y porcentaje.
4. Se pueden reflejar, duplicar, ocultar, colorear o quitar piezas y restablecer su ajuste. Hay deshacer/rehacer. El reflejo invierte X y aplica una escala negativa; es una operación geométrica, sin reconstruir detalles asimétricos.
5. El borrador se guarda automáticamente en `localStorage` de este navegador (`l2-armor-draft-v1`). Guardar JSON conserva todas las referencias y ajustes; Abrir JSON permite continuar otro proyecto. Exportar GLB genera un modelo estático con las piezas visibles y el modelo base.

El control Base transparente ayuda a comprobar encajes. Frente, Perfil, Espalda y ¾ permiten revisar la silueta; Encuadrar adapta la cámara a todas las piezas visibles.

## Biblioteca inicial

- 12 grupos de la armadura V2: casco, dos hombreras, dos brazales, pechera, cinturón, faldón, gorjal, lazo, penacho y escudo. Se mantienen los materiales y el ajuste de la pose base.
- 10 cortes espaciales de Armor Cat: casco, pechera, cintura, faldón, dos hombreras, dos guantes y dos botas. Estos cortes provienen del STL fusionado y están marcados como iniciales. Pueden incluir rostro, cuerpo, accesorios o huecos en los bordes; no equivalen a prendas terminadas.

No se alteraron las descargas, el modelo original de Lucien ni el cliente de L2. Las copias para encaje están en `exports/armor-editor`. `build_armor_parts.py` reconstruye biblioteca, miniaturas y `armor-parts.json` usando Blender 3.5.1.

## Límites

Esta primera versión es un taller de ensamblaje en pose fija. No corta ni esculpe interactivamente la malla, no reconstruye superficies ocultas y no transfiere automáticamente pesos. Antes de usar un montaje en L2 se necesitan limpieza, ajuste de deformaciones, optimización, materiales compatibles y exportación al formato del cliente. El JSON es el proyecto editable; el GLB exportado carece de rig y animaciones.

Los recursos web retienen su procedencia. La existencia de una copia descargada no confirma su licencia para redistribuir un cliente público. Las piezas de Armor Cat provienen del ZIP local identificado en `research/cat-assets-20261023/README.md`.

## Implementación y comprobación

Three.js r160 con TransformControls y GLTFExporter de la misma versión; se conserva el OrbitControls corregido para zoom gradual. Se añadieron módulos oficiales en `vendor/addons/controls/TransformControls.js`, `vendor/addons/exporters/GLTFExporter.js` y `vendor/addons/utils/TextureUtils.js`.

El editor usa archivos estáticos servidos por el servicio existente, sin endpoints de escritura en el servidor. Los proyectos JSON solo aceptan piezas de la biblioteca, números finitos y tamaños acotados. La carga valida y prepara los recursos antes de sustituir el montaje activo.

Validación de navegador: `tmp/verify_armor_editor.py`, con resultados y capturas en `tmp/armor-editor-20261023`. Se comprueban carga, biblioteca, transformaciones, reflejo, deshacer/rehacer, duplicado, borrado, recuperación tras recarga, rechazo de proyectos inválidos y exportación/importación GLB estática.
