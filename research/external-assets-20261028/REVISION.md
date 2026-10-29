# Assets externos · Tanda 3

Revisión del 28/10/2026. Carpeta de entrada: `E:\l2-local\descarga de assets`.

## Resultado

- 85 modelos distintos con GLB portátil y miniatura renderizada.
- 1 recurso pendiente de conversión: Scary Guy, fuente Collada/DAE no admitida por Blender 5.
- 2 descargas de Sketchfab duplicadas agrupadas en la misma ficha.
- Un dirigible Airship02 incorporado desde FBX; sus variantes BLEND/OBJ/STL se conservan como formatos alternativos.
- 29 modelos con huesos en la fuente; 13 modelos con clips de animación exportados, reproducibles en el visor.
- 2971 fichas anteriores conservadas sin cambios. Los originales y favoritos del navegador del usuario no se modificaron.

[Abrir esta tanda en el catálogo](http://127.0.0.1:32280/?batch=Assets%20externos%20%C2%B7%20Tanda%203)

## Categorías

- Personalizados: 15
- Monstruos: 19
- NPC: 27
- Objetos: 8
- Escenarios: 16

## Texturas y límites

- 72 vistas con imágenes de textura y sin referencias ausentes detectadas. Esto no garantiza equivalencia de todos los shaders con el programa de origen.
- 12 vistas con referencias de textura pendientes; están señaladas en la ficha.
- 1 vistas sin texturas de imagen.
- Demogorgon: vista estática con esqueleto. Exportar sus clips excedió 300 segundos; el original se conserva y la limitación está indicada en la ficha.
- El visor permite explorar estos recursos. Todavía no son paquetes UKX/UTX adaptados a Interlude, ni tienen estadísticas, ID o IA de NPC.
- Algunas fuentes incluyen licencias NC o ND. Cada ficha muestra la licencia declarada por el publicador y su enlace original; la descarga no se presenta como autorización general para cualquier uso.
- Los 9 paquetes nativos restantes de L2 y los recursos auxiliares de cabello/interfaz quedan inventariados aparte, sin mezclarlos con esta tanda externa.

## Archivos de revisión

- [Inventario CSV](INVENTARIO.csv): nombres, formatos, triángulos, huesos, clips, texturas, autor y licencia.
- [Inventario de paquetes](inventory.json): todos los paquetes encontrados y formatos alternativos.
- [Procedencia de Sketchfab](sources.json): metadatos públicos de 87 descargas, sin URLs de descarga firmadas.
- [Fichas incorporadas](catalog-entries.json).
- [Verificación del navegador](browser-verification.json).

## Recursos con texturas pendientes

- Abomination - DOOM : The Dark Ages - Rigged — abomination_1005_n.png, abomination_1007_n.png, abomination_1002_n.png, abomination_1004_n.png, abomination_eye.png, human_eye_n.png…
- Airship02Fbx — rope_texture2093.jpg
- ANGEL OF DEATH from Hellboy 2 statue scan — 
- Bloody Rose Sword | FREE — 
- CATTO — 
- Despair - Darksiders 2 - Rigged — material_3
- FREE| Wild Sword — leafRouhgness, LeafSet024_4K-JPG_Color.jpg.001, LeafSet024_4K-JPG_NormalGL.jpg.002, LeafSet024_4K-JPG_Opacity.jpg, LeafSet024_4K-JPG_Roughness.jpg.002, Metal044B_4K-JPG_Color.jpg…
- Hologram Police Robots — Усилитель_Roughness.tga, Усилитель_Metallic.tga, Гусеничная лента_Metallic.tga, Внутрянка ленты_Roughness.tga, Пружины_Metallic.tga, Зашита от грязи_Roughness.tga…
- medieval town (no textures) — 212_DefaultMaterial_BaseColor.png, 212_DefaultMaterial_Emissive.png, 212_DefaultMaterial_Metallic.png, 212_DefaultMaterial_Normal.png, 212_DefaultMaterial_Roughness.png, 2x_DefaultMaterial_BaseColor.png…
- Old house — brick_001.png, Deep_Metal.png, lod_3.png, wind_1.png
- Robot — 8k_stars_milky_way.jpg, bark texture.jpg.005, leaf texture.jpg.005, mossy stone.jpg.005, portland_landing_pad_16k.exr, seamless rock2.png.005…
- The BodyHighJacker — Skin_ZSphere_2.bmp

## Contactos visuales

- [Hoja 1](contacto-1.jpg)
- [Hoja 2](contacto-2.jpg)
- [Hoja 3](contacto-3.jpg)
- [Hoja 4](contacto-4.jpg)

## Reproducción y respaldo

Scripts locales: inventory.py, unpack_rars.py, metadata.py, convert_blender.py, run_batch.py, publish.py, document.py y verify.cjs. No ejecutar el lote completo para reparar una sola ficha; usar --keys. Respaldo anterior a la publicación: `E:\l2-local\backups\external-assets-20261028`.

## Observaciones de revisi?n visual

- Abomination - DOOM : The Dark Ages - Rigged: La pose base necesita revisión antes de reutilizar el rig.
- ANGEL OF DEATH from Hellboy 2 statue scan: La malla importada es un busto; comprobar su correspondencia con el título de la publicación.
- Witch - DOOM : The Dark Ages - Rigged: La pose base aparece plegada; revisar el rig y su pose de enlace.
- World's End Inn: La vista importada parece plana; no se validó como edificio tridimensional completo.
