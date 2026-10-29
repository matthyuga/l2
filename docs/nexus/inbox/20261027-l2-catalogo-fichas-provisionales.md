# L2: nombres y etiquetas provisionales en galería

Kevin solicitó campos para asignar modelos favoritos a personajes, con nombre sugerido y etiquetas de territorio/nivel. Implementado en E:\l2-local\research\model-catalog, galería http://127.0.0.1:32280.

Campos: nombre propuesto, territorio, bando, nivel, IP y etiquetas libres. Presentación en tarjetas, búsqueda ampliada y filtros de territorio/etiqueta propuestos. Guardado explícito en favoritos y exportación JSON schema_version2 con selections conservado. Datos nuevos dentro de planning, separados de NPC/nivel/hábitat original.

Se conserva l2-model-choices y la información anterior; también propiedades desconocidas y favoritos sin correspondencia actual. No se tocó el perfil del navegador del usuario. Para cargar controles nuevos basta guardar cualquier edición pendiente y recargar. Datos aún locales al navegador, con exportación; no se agregó backend ni importación.

Detalle y pruebas: E:\l2-local\research\gallery-planning-20261027\README.md. Chromium aislado: persistencia, exportación, notas anteriores, búsqueda, etiquetas, móvil y referencias verificados; sin errores JS. Backup en E:\l2-local\backups\gallery-planning-20261027. Sin cambios al juego ni a los datos del catálogo.
