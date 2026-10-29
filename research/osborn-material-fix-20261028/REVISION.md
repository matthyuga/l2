# Osborn: cuerpo recortado — 28/10/2026

Corregido en [el catálogo](http://127.0.0.1:32280/?model=m0527&view=3d).

La ficha m0527, `LineageNPCs.e_patriarch_MOrc_m00`, agrupa 12 NPC, entre ellos Osborn, Drikus y Kakai. La geometría no estaba incompleta: la transparencia del material del cuerpo estaba mal reconstruida.

## Evidencia del cliente original

- `e_patriarch_MOrc_m00_t00_b01` es un FinalBlend: AlphaTest=true, AlphaRef=160, Material=`e_patriarch_MOrc_sh`.
- El Shader usa Diffuse=`e_patriarch_MOrcc_t00_b01_sp` y Opacity=`e_patriarch_MOrc_m00_t00_b01_or`.
- La alfa del diffuse también sirve de máscara de brillo; sus valores 0–170 no representan la transparencia del cuerpo.
- La textura de Opacity sí contiene una alfa 0–255 para recortar los bordes de la ropa.

Se conservaron los colores RGB del Diffuse y se reemplazó únicamente su alfa por la de Opacity. El glTF usa MASK con el umbral original 160/255. Cabello y demás materiales conservan sus propias reglas. La miniatura se regeneró desde el glTF corregido.

## Conservación y persistencia

No se modificaron la malla, los nodos, el esqueleto, los buffers, las animaciones ni los paquetes del juego. El resto de las fichas del catálogo permanece idéntico. `evidence.json` contiene las propiedades serializadas, hashes y comprobaciones. Copias previas en `before/`.

La caché de materiales guarda el color compuesto, su origen y el umbral correcto. `build_gallery.py` respeta el umbral específico de la caché para conservar la corrección al reconstruir esta ficha.

`browser-verification.json` comprueba que el visor carga la textura y usa el umbral correcto. Captura: [osborn-browser.png](osborn-browser.png).
