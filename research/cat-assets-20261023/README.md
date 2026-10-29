# Revisión de gatos descargados — 23/10/2026

Se encontraron seis ZIP de gatos en `E:/l2-local/descarga de assets`. Se extrajeron copias de revisión en esta carpeta y se generaron GLB autocontenidos y miniaturas para el catálogo. Los ZIP originales no se modificaron. No se han transferido estas armaduras a Lucien ni integrado modelos al cliente de L2.

| Archivo | Triángulos | Contenido y utilidad |
|---|---:|---|
| a-cartoon-drawing-of-a-cat-wearing-gold-armor.zip | 50.000 | Gato dorado de cuerpo entero, con textura; anatomía más alargada que la referencia. |
| a-white-cat-dressed-as-a-knight-the-cat-is-weari (1).zip | 50.000 | Gato guerrero turquesa, de cuerpo entero; aspecto de aventurero estilizado. |
| a-white-cat-dressed-as-a-knight-the-cat-is-weari.zip | 50.000 | Gato con casco, capucha y traje azul; base visual de explorador. |
| armor-cat.zip | 804.744 | STL de un gato redondo con casco, penacho, armadura, espada y escudo. Es el más cercano a la silueta tierna del dibujo. Sin UV ni texturas en el STL. Requiere retopología, texturizado y rig. |
| armored-cat-with-horned-god-face.zip | 2.042 | FBX de cuerpo entero con textura; gato oscuro con cuernos, adecuado a una variante de fantasía oscura. El bajo número de triángulos no demuestra por sí solo calidad de deformación. |
| knight-cat.zip | 1.144.368 | Cabeza de gato con casco; no es un personaje de cuerpo entero. No sirve como conjunto completo de armadura para Lucien. |

Ninguno de los seis archivos importados contiene armature. Los cuatro GLB originales tampoco contienen skins ni clips de animación. El rig de Lucien puede estudiarse como referencia para adaptar una versión reconstruida; la compatibilidad no está demostrada.

## Acceso

Galería local: `http://127.0.0.1:32280/?q=Gatos%20descargados`. Categoría Personalizados, paquete GatosDescargados. Claves `web_cat_review_01` a `web_cat_review_06`. No se asignaron IDs, niveles ni zonas ficticias. Los botones de animaciones nativas están desactivados.

Inventario detallado: `inventory.json`. Extractor: `inspect_assets.py`; render/importación: `render_assets.py` con Blender 3.5.1. Copia previa del catálogo: `backups/cat-assets-review-20261023`.

## Correspondencia con enlaces

Solo se estableció correspondencia por nombre con el gato dorado y Knight Cat, además del Armor Cat mencionado anteriormente. No se encontraron archivos identificables como Paladin Cat, los dos Samurai Cat ni Steampunk Robot Cat; podrían llegar después o tener otros nombres. No se deben atribuir automáticamente las descargas adicionales a esos enlaces.

La ficha web de [Samurai Cat de Tom Johnson](https://sketchfab.com/3d-models/samurai-cat-based-on-art-by-hiziripro-89106361d8e947e58bd2709e6a289a6e) declara una escultura de unas 590.300 caras triangulares, sin retopología ni texturas, basada en una ilustración de Satoshi Matsuura. Es información de la publicación; no se inspeccionó una descarga local de ese modelo.

Las licencias de todas las descargas no están confirmadas. Las copias de revisión preservan la procedencia del ZIP; no representan permiso para redistribuirlas en un cliente público.
