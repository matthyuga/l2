# Correcci?n de texturas de Tanda 2 ? 13/10/2026

Causa confirmada en el NPC de la captura: el importador recortaba las rutas de UModel con espacios (Client Side/...) y trataba Client como nombre de paquete. No era evidencia de descarga da?ada. Corregida la lectura en build_gallery.py y regenerados materiales y miniaturas de la tanda. Tambi?n corregida la sustituci?n de argumentos cuando paquete y objeto tienen el mismo nombre (Takao).

Antes: 161 de 1379 vistas ten?an al menos una textura; 112 ten?an todos sus materiales texturados. Despu?s: 1090 tienen al menos una textura; 1075 tienen todos sus materiales texturados. Recuperaci?n: 929 vistas adicionales con textura y 1950 asignaciones de textura adicionales. No equivalen a especies ?nicas.

El NPC LineageNPCs_Effects_01.viRUS_NPC02_m00 de la captura tiene ahora sus 3/3 materiales texturados. Miniatura revisada visualmente, al igual que Balok. Se comprobaron 3604 enlaces a buffers e im?genes, las 1379 miniaturas actualizadas y las 843 entradas originales conservadas sin cambios. Servidor devuelve cat?logo y miniatura con HTTP 200.

Persisten 289 vistas sin textura resuelta y 15 parcialmente texturadas. Hay mallas auxiliares sin material, dependencias ausentes y shaders no resueltos. Ejemplo confirmado: Wog_building solicita Wog_buildingtex, ausente en su paquete extra?do; el archivo contiene otro paquete de texturas con nombre distinto. No asumir que cada pendiente est? da?ado ni que funcionar? completo en el juego. Los efectos, part?culas y materiales de Unreal no se reproducen ?ntegramente en glTF. Contin?an 130 fichas sin vista disponibles por geometr?a vac?a u otros errores previos.

Abrir la galer?a y actualizar con Ctrl+F5. Los originales descargados, el cliente y el servidor del juego no se modificaron.

Evidencia: material-fix-summary.json, material-fix-verification.json y logs por paquete. Backup de metadatos: gallery-before-material-fix.json; importador previo: build_gallery-before-texture-fix.py. refresh_materials.py conserva la tanda original; no ejecutar el main hist?rico de build_gallery.py para reconstruir la galer?a completa.
