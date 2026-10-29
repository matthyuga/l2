# Planificación de personajes en el catálogo

27/10/2026. Pedido de Kevin: añadir nombre elegido/sugerido y etiquetas provisionales (territorio, nivel y otras) para catalogar sus favoritos y asignar modelos a personajes de la reinterpretación.

Implementado en research/model-catalog/gallery.html, gallery.js y gallery.css:

- Nombre propuesto, territorio, bando, nivel e IP como texto libre.
- Etiquetas múltiples, con Enter/coma/punto y coma/botón, deduplicación sin distinguir acentos/mayúsculas y eliminación individual.
- Presentación en tarjetas, búsqueda por nuevos campos y nota, filtros propios de territorio y etiqueta.
- Guardado explícito junto a favoritos existentes; exportación JSON incluye planning y versión 2 manteniendo selections.
- Referencias originales, NPC seleccionado, niveles y hábitats se conservan como datos independientes.

Mismo localStorage l2-model-choices. Se preservan propiedades anteriores/desconocidas y referencias antiguas sin correspondencia actual. Una propuesta por modelo, como los favoritos anteriores. No se agregó persistencia de servidor ni importación: los datos siguen en el navegador y pueden exportarse.

La galería local ya está sirviendo la versión nueva en http://127.0.0.1:32280. HTML/JS/CSS con versión de caché actualizada; el usuario puede recargar después de guardar cualquier edición pendiente. No se refrescó su pestaña ni se accedió a su perfil.

Verificación reproducible: verify.cjs, Chromium con contexto nuevo y fixture de favoritos propios de prueba. Incluye persistencia tras recarga, exportación con referencias antiguas, campos desconocidos, notas intactas, búsquedas, filtros, etiquetas, texto parecido a HTML mostrado como texto, móvil sin desbordamiento, cambio de referencia nativa y recurso externo sin NPC. Resultado sin errores JavaScript. Capturas y verification.json en E:\l2-local\tmp\gallery-planning-20261027.

Respaldo de archivos previos: E:\l2-local\backups\gallery-planning-20261027. update-html.py documenta la migración de HTML aplicada una vez. No ejecutar generadores históricos sobre la versión actual para repetir esta mejora.

Sin cambios a gallery.json, NPC, cliente, estadísticas, apariciones o servidor de juego.
