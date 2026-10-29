# Texturas CC0 para L2 Lab

Colección de ambientCG en 2K-JPG: todas las disponibles de las categorías listadas en `plan.json`. Incluye pasto, musgo, tierra/arena, grava, piedra/roca, adoquines, ladrillo, madera/pisos/tablones y metal/pintado/óxido. Este lote no equivale a los tres catálogos completos de Poly Haven, ambientCG y ShareTextures.

`download.py` usa el catálogo público de ambientCG, conserva los ZIP originales en `archives/`, verifica tamaño y CRC, extrae los mapas, comprueba las imágenes y genera miniaturas. Reanudar los tres proveedores con `20-DESCARGAR-TEXTURAS-L2.cmd` en E:/l2-local o `python -u research/texture-library/run_all.py`. Una exclusi?n mutua evita dos gestores simult?neos. El gestor reintenta hasta tres pasadas por proveedor y registra si quedan pendientes; no garantiza que enlaces retirados o restringidos sean descargables. Para ambientCG solo: `python -u research/texture-library/download.py --all`. Omite materiales terminados. Los fallos quedan registrados y una nueva ejecución vuelve a intentar los pendientes.

- `ambientcg-catalog.json`: metadatos originales de la API pública.
- `plan.json`: alcance y tamaño previsto.
- `progress.json`: cantidad terminada, total, errores y estado.
- `catalog.json`: únicamente materiales terminados, con fuente, licencia, resolución, mapas y SHA-256 del ZIP.
- Mapas extraídos: `E:/l2-local/research/model-catalog/exports/cc0-textures/ambientcg/`.

Licencia: **CC0 1.0**. Fuentes y detalles por material en `source.json` y `catalog.json`. Documentación oficial: https://docs.ambientcg.com/license/ . Permite uso, modificación y redistribución, incluso comercial. Materiales originales de ambientCG; no son archivos extraídos de L2.

En el editor local: Escena → seleccionar pieza → desbloquear → Superficies → Explorar texturas. Galería con búsqueda bilingüe por ID/tags y categoría en español. Recargar el navegador para incorporar materiales que terminen durante la descarga. Por ahora se utiliza el mapa de color; normal, rugosidad, altura y otros mapas quedan conservados para futuras funciones. No se instala nada en el cliente de juego.

## Trabajo en segundo plano

`run_all.py` administra tres procesos independientes (4/2/2 descargas simult?neas respectivamente), con registro run.json, logs por proveedor y progreso persistente. Contin?a sin mantener esta conversaci?n abierta mientras Windows y la conexi?n sigan activos. No configura tareas de inicio ni se reanuda tras reiniciar Windows salvo ejecutar el lanzador.

Poly Haven se descarga mediante su API p?blica: mapas de color, normales OpenGL/DirectX, rugosidad, oclusi?n, desplazamiento y otros mapas principales disponibles en 2K, con comprobaci?n MD5 publicada. ShareTextures usa su sitemap y metadatos de las p?ginas p?blicas, respetando la exclusi?n de su API en robots.txt; conserva los ZIP 2K enlazados p?blicamente. Fuentes, licencias y mapas por material en source.json. Las p?ginas sin ZIP p?blico 2K o que requieren otro proveedor/cuenta se registran como pendientes; no se eluden restricciones.

El selector integra los cat?logos terminados de los tres proveedores. Explorar texturas muestra el avance global. Recargar el editor incorpora materiales nuevos. Mapas y miniaturas en research/model-catalog/exports/cc0-textures/{ambientcg,polyhaven,sharetextures}; ZIP originales de ambientCG y ShareTextures en esta biblioteca. Los dem?s mapas a?n no se usan en el render del editor.
