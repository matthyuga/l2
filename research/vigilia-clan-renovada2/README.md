# Vigilia revisión 2

Fuente preservada: `../vigilia-clan-renovada1/Vigilia-renovada1.blend`. Revisión solicitada: abrir los paneles traseros de ambos laterales del puente, escalera posterior al techo con alero recortado y unión visual de globo/casco.

Master: `Vigilia-renovada2.blend`. `build_revision.py` parte siempre de la revisión 1, genera piezas editables y exporta una copia agrupada por zona/material. `register-project.cjs` registra el modelo/escena independiente y los proyectos principal/escala. No usar --rebuild tras ediciones del usuario sin conservarlas. Reducir únicamente las copias de las dos texturas exportadas a 1024 px conservando proporciones.

`audit_geometry.py` comprueba apoyos, altura libre y recorridos con referencia 46u alto/24u ancho y anclajes sobre el globo. `verify-revision.cjs` carga el proyecto en Chrome aislado y comprueba cámaras, exportación, API y recarga. `render_revision.py` produce las tres vistas de presentación. Documentación de uso y enlaces en `../../mapas editados/vigiliarenovada2/README.md`.

La sala del timón utiliza los dos accesos laterales nuevos; la escalera ocupa la parte posterior. En integración L2 se necesitan apoyos/colisión/geodata para la azotea y nueva escalera. La nave actualmente instalada queda conservada.
