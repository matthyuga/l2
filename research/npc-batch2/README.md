# Galeria L2: Tanda original y Tanda 2

13/10/2026. Incorporados los165paquetes de NPCs descargados enK. El visor portable conserva843entradas previas como Tanda original y agrega1509entradasTanda2:1379mallas conglTF yminiatura;130fichas sinvista disponible. Las fichas incluyen mallas, variantes y piezas deefectos/objetos: no representan1509NPCs distintos.

Abrir GALERIA-MODELOS-L2.cmd y elegir el filtro Tanda. Acceso directo: http://127.0.0.1:32280/?batch=Tanda%202 . Tambien se puede buscar Tanda2 por su etiqueta en busqueda. Activar Mostrar recursos sin imagen para revisar130fichas pendientes.

843claves/metadataoriginales conservadas salvo el campo batch. Favoritos priorizan claveexacta para evitar confundir misma malla deotra tanda. Tarjetas ydialogos muestran etiqueta. CategoriaBosses agregada. RecursosTanda2 aislados porarchivoDrive enresearch/npc-batch2/packages; no se copiaron acliente. nativeAssetRoot resuelto dentro delproyecto para UModel, conextensionesukx/usx/u.

Verificados todos losbuffers,texturas yminiaturas de1379vistas. APIcatalog2352entradas y dosfiltros de tanda. APIaperturaBalok200 y UModelresponding. No se pudo inspeccionar navegador nativo porque ComputerUsepipe estaba indisponible; no afirmar validacionvisual completa deWebGL/UI. Hoja de6miniaturas revisada visualmente encontact-sheet.jpg: mallas presentes, materiales aproximados y algunos colores pendientes deafinacion.

130no disponibles incluyen100exportaciones congeometriavacia yotroserrores/recursos sinmalla. Freya cuerpo/trono original deeste pack exporta geometriavacia conUModel; sus accesorios legibles siguenvisibles. Paquetes originales yerrores conservados. No ejecutar DLL/codigo de lospacks. Stats/IA/servidor nointegrados. Particulas/sonidos/animaciones nativas no equivalen aWebGL. Algunasvariantes comparten unarepresentacion de material.

Backup: backups/npc-tanda2-20261013-153746. Scripts/manifest/logs enresearch/npc-batch2. No reejecutar build_gallery/finalizadores historicos para regenerar todo sinpreservar Tanda2. Elimportador guarda resultadosporpaquete; repeticiones requieren revisar gallery.json yvariantes.


# Correcci?n de texturas de Tanda 2 ? 13/10/2026

Causa confirmada en el NPC de la captura: el importador recortaba las rutas de UModel con espacios (Client Side/...) y trataba Client como nombre de paquete. No era evidencia de descarga da?ada. Corregida la lectura en build_gallery.py y regenerados materiales y miniaturas de la tanda. Tambi?n corregida la sustituci?n de argumentos cuando paquete y objeto tienen el mismo nombre (Takao).

Antes: 161 de 1379 vistas ten?an al menos una textura; 112 ten?an todos sus materiales texturados. Despu?s: 1090 tienen al menos una textura; 1075 tienen todos sus materiales texturados. Recuperaci?n: 929 vistas adicionales con textura y 1950 asignaciones de textura adicionales. No equivalen a especies ?nicas.

El NPC LineageNPCs_Effects_01.viRUS_NPC02_m00 de la captura tiene ahora sus 3/3 materiales texturados. Miniatura revisada visualmente, al igual que Balok. Se comprobaron 3604 enlaces a buffers e im?genes, las 1379 miniaturas actualizadas y las 843 entradas originales conservadas sin cambios. Servidor devuelve cat?logo y miniatura con HTTP 200.

Persisten 289 vistas sin textura resuelta y 15 parcialmente texturadas. Hay mallas auxiliares sin material, dependencias ausentes y shaders no resueltos. Ejemplo confirmado: Wog_building solicita Wog_buildingtex, ausente en su paquete extra?do; el archivo contiene otro paquete de texturas con nombre distinto. No asumir que cada pendiente est? da?ado ni que funcionar? completo en el juego. Los efectos, part?culas y materiales de Unreal no se reproducen ?ntegramente en glTF. Contin?an 130 fichas sin vista disponibles por geometr?a vac?a u otros errores previos.

Abrir la galer?a y actualizar con Ctrl+F5. Los originales descargados, el cliente y el servidor del juego no se modificaron.

Evidencia: material-fix-summary.json, material-fix-verification.json y logs por paquete. Backup de metadatos: gallery-before-material-fix.json; importador previo: build_gallery-before-texture-fix.py. refresh_materials.py conserva la tanda original; no ejecutar el main hist?rico de build_gallery.py para reconstruir la galer?a completa.
