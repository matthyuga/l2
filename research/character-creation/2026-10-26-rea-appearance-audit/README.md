# Diagnóstico con REA de los tres fallos de apariencia

Análisis del 26/10/2026 sobre una copia del engine.dll instalado. No se modificaron archivos activos del cliente, servidor ni personajes durante este análisis. Se descargó el paquete Orc.ukx del mismo distribuidor de los recursos originales para comparar el modelo de cabeza con las texturas de caras ya instaladas.

| Caso | Resultado | Grado de certeza |
|---|---|---|
| Elfo oscuro masculino, Hairstyle G | Pertenece a Tanda 1. El material original pide AlphaRef=160, pero el instalado usa 5. Ambos usan mezcla alfa, prueba alfa y escritura de profundidad. | Diferencia de configuración confirmada; su papel en el defecto visual requiere prueba en el cliente. |
| Orca Fighter, Hairstyle J | Pertenece a Tanda 2 v11. Atlas, material y selección correctos; el usuario confirma que ve el paisaje a través de la zona. El material acepta píxeles de alfa muy bajo y escribe profundidad. | Hueco visual confirmado por el usuario. Transparencia/oclusión es una hipótesis fundada; todavía no se distingue de falta de cobertura geométrica en esa zona. |
| Orco Fighter masculino, Face F | Se aplica una textura de cara completa al modelo con distribución UV antigua. La cabeza donante coloca correctamente las mismas texturas en una reconstrucción visual. El mismo problema afecta D y E. | Incompatibilidad de UV reproducida y confirmada. |

REA abrió y decompiló el binario instalado, no sólo los scripts de construcción. Evidencia: `ev_0c1763053529d873abd641f7f9344fd9fce05fea898920f5b90513d1a640cb0c`. SHA-256: `fd14ed00ededcb893826e88813eb3c3785b800192c73b0855c82b54e68a8287e`. Archivo completo: `rea-live-hooks.txt`.

Las funciones analizadas son `0x12071e00` (nombre de malla), `0x12072400` (material) y `0x12073600` (cantidad de materiales). Confirman que G del elfo oscuro carga `NexusAppearanceV1.MDarkElf_Hair2`, mientras J de la orca carga `NexusHairT2V11.FOrc_T2_1`. No se intercambian estos dos recursos ni sus letras. La cantidad de materiales de la orca J es uno. El arreglo de cabeza para caras nuevas está limitado al elfo oscuro; el orco sigue usando la cabeza nativa para D/E/F mientras recibe las texturas nuevas.

Para leer los paquetes Unreal se utilizó UModel, complementando el análisis nativo de REA. Los volcados `dark-hair-donor.txt`, `dark-hair-installed.txt`, `orca-hair-donor.txt` y `orca-hair-installed.txt` documentan las propiedades reales de los recursos. Los materiales instalados tienen TwoSided=true: no corresponde atribuir estos defectos simplemente a que falte activar el dibujo por ambas caras.

En G del elfo oscuro, el umbral instalado acepta 3.079 píxeles de alfa entre 5 y 159 que el material donante rechaza. En el atlas J de la orca hay 5.401 píxeles en ese intervalo. Son conteos de las imágenes completas, incluidos espacios y márgenes: no equivalen a una cantidad de píxeles visibles en pantalla ni demuestran por sí solos la causa de un hueco. La combinación de mezcla alfa y escritura de profundidad puede ocultar superficies posteriores, por lo que debe probarse con el renderer nativo.

La fuente de la orca usa texturas DXT3 con `bMasked=true`, `bAlphaTexture=true` y `bTwoSided=true`. La adaptación las combina en un atlas y las presenta mediante FinalBlend con AlphaRef=5. Su canal alfa no está ausente ni vacío. El umbral adecuado y la eventual necesidad de una superficie de apoyo deben decidirse mediante una prueba localizada, conservando geometría, UV y colores para aislar el efecto del material.

La comparación `alpha-vs-geometry.jpg` muestra reconstrucciones con transparencia y con alfa desactivado, de perfil y espalda. Es una prueba fuera del juego: no reproduce el orden de dibujo ni el búfer de profundidad del cliente. No permite declarar resueltos los dos defectos de cabello. La captura del usuario y su confirmación descartan interpretar el hueco de la orca simplemente como piel verde expuesta.

El rostro nativo del orco usa una textura de 256×256 con media cara; las texturas nuevas D/E/F son atlas de 512×512 de cara completa. `MOrc_m000_f` y el donante `MOrc_m001_f` tienen 206 puntos y 386 triángulos, pero sus UV no coinciden y sus geometrías tampoco son idénticas: la máxima distancia entre puntos más cercanos es aproximadamente 0,145 unidades. No corresponde sustituir solamente las coordenadas suponiendo igualdad exacta de vértices sin verificar la correspondencia. La solución propuesta es adaptar la cabeza m001 al esqueleto nativo y utilizarla únicamente para las caras D/E/F, manteniendo A/B/C.

`orc-faces-uv-comparison.jpg` reproduce las tres caras nuevas con la cabeza antigua y con la donante. En la cabeza antigua aparecen ojos, orejas y mandíbula duplicados/desplazados; la cabeza con UV correspondientes coloca esos rasgos correctamente. Esto verifica la causa del rostro, pero todavía no constituye una instalación ni una validación de animación dentro del cliente.

Siguiente corrección dirigida: restaurar el umbral del material donante para G del elfo oscuro; probar el tratamiento de recorte/profundidad sólo en J de la orca; adaptar la cabeza del orco para D/E/F. No cambiar todos los materiales o las cabezas originales de forma global.

Otros archivos: `sources.json` (hashes de recursos activos), `alpha-statistics.json`, `orc-face-uv-proof.json`, `donor/manifest.json`, exportaciones de mallas/texturas y generadores reproducibles de las imágenes de diagnóstico.
