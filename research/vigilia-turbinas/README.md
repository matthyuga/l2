# Turbinas navales de Vigilia

Fuente: research/vigilia-mascaron/Vigilia-mascaron.blend.
Salida: Vigilia-turbinas.blend y research/model-catalog/exports/vigilia-turbinas/turbinas.gltf.
Proyecto: vigiliaturbinas1 (19 objetos), con variante -escala.

build_turbines.py elimina solo los motores originales por prefijos de nombre, comprueba las firmas de las demás mallas y construye dos conjuntos independientes. Guarda el máster sin unir para editar las piezas, luego exporta tres raíces compactas: casco, turbina babor y turbina estribor. El mascarón usa su recurso anterior sin cambios.

register-project.cjs registra los recursos persistentes y genera proyectos nuevos. --rebuild solo para iteraciones de taller antes de entregar; no usar sobre cambios del usuario. verify-turbines.cjs comprueba igualdad de las otras 16 zonas, carga, exportación, guardado, recarga, variante de escala y errores del navegador; genera las vistas de revisión.

Referencia visual y créditos: ver mapas editados/vigiliaturbinas1/README.md. El zip original y sus metadatos se conservaron en source y source-metadata.json. No se usó geometría ni texturas descargadas en el resultado. No hay instalación nativa ni cambios de colisión/geodata.
