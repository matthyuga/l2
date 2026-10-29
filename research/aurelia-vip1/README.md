# Aurelia VIP1

Encargo: renovar la aeronave Aurelia como espacio VIP del dueño del servidor, con fiestas, piscina animada, salas interiores y un mirador transparente que permita mirar hacia tierra y ver a los ocupantes desde abajo.

Entregas: `../../mapas editados/aureliavip1/README.md` describe espacios, enlaces, cámaras y límites. Modelo editable: `Aurelia-VIP1.blend`, con materiales y texturas empacadas. Catálogo optimizado: `../model-catalog/exports/aurelia-vip1/aurelia.gltf` y dependencias. Proyectos `aureliavip1`, `aureliavip1-social` y `aureliavip1-invitados`, bajo `../scene-editor/projects`.

## Reproducción

1. Blender 5.0.1: `build_vip.py` abre y copia el modelo original; produce distribución y mobiliario sin modificar el original.
2. Blender: `polish_vip.py` añade techos, paneles, arte, iluminación visual y ajusta muebles para despejar entradas.
3. Blender: `finish_vip.py` verifica pasos de las barandas, empaca imágenes en el master y exporta una copia agrupada por zona/material.
4. Node 24: `register-project.cjs --rebuild` registra catálogo/escena y escribe los tres proyectos. Omitir --rebuild si ya existen; no reconstruir después de ediciones del usuario sin conservarlas.
5. Python/Pillow: `optimize-textures.py` reduce únicamente las copias de texturas exportadas a un máximo de 1024 px, preservando las originales.
6. Reiniciar solamente el servidor local del taller si cambió data.json o el esquema de efectos.

`render_vip.py` produce dos imágenes de presentación desde el modelo. `verify-vip.cjs` prueba el editor real en Chrome aislado, diez cámaras, las dos vistas de interiores, el emisor animado, exportación, API y recarga. `audit_geometry.cjs` comprueba las entradas a distintas alturas y las líneas de visión del mirador desde arriba/abajo con la geometría exportada.

El agua animada corresponde al nuevo tipo `pool` en scene-effects.js y effect-schema.js del taller. El modelo Blender tiene una superficie de respaldo; los efectos se ejecutan en el taller a partir del JSON.

La integración histórica de Aurelia en L2 no fue modificada. Este paquete es el diseño VIP separado; no ejecutar instaladores históricos contra el mapa actual para instalarlo.
