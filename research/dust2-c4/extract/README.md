# C4 Counter-Strike 1.6: extracción local

Origen de solo lectura: `D:\juegos\cs1.6\cstrike\models\w_c4.mdl` y `p_c4.mdl`. Las copias están junto a los OBJ; no se ejecutó Counter-Strike ni se modificó el origen.

`w_c4/w_c4.obj` es el recomendado para una bomba plantada: bloque verde con reloj rojo y cables, 64 vértices y 116 triángulos. `p_c4/p_c4.obj` tiene 72 vértices y 128 triángulos, una variante para mano. Ambos tienen tres materiales y tres PNG de paletas embebidas. Las imágenes `preview_*` se renderizaron con Blender 3.5.1 y fueron inspeccionadas visualmente; la textura y forma de la bomba son reconocibles.

Exportación en coordenadas GoldSrc originales, Z arriba, sin recentrar ni escalar. Se aplican transformaciones de todos los huesos padres a los vértices/normales locales usando sus valores de reposo. No se decodifican deltas de animación. Los OBJ invierten el winding horario de GoldSrc para producir caras antihorarias compatibles con OBJ y normales hacia afuera; cada triángulo no degenerado coincide con la orientación de sus normales. UV `(s/ancho, 1-t/alto)` para imágenes PNG con sus filas originales.

Validaciones: IDST versión 10 y longitud de cabecera igual al archivo; lecturas dentro del archivo; padres e índices de huesos, vértices y normales válidos; matrices ortonormales; cantidad de triángulos reconstruidos de strips/fans igual a cada cabecera de malla. `manifest.json` conserva SHA256 de entrada, estructura, transformaciones, dimensiones, materiales y contajes.

Reproducir: ejecutar `python extract_goldsrc_c4.py`. Para las ocho vistas ejecutar Blender 3.5.1 en background con `--factory-startup --python render_models.py`. Importación Blender: `bpy.ops.import_scene.obj(...,axis_forward='Y',axis_up='Z')`.

Referencia primaria del formato: https://github.com/ValveSoftware/halflife/blob/master/engine/studio.h . Se escribió un decodificador independiente a partir de la estructura documentada; no se copió código del SDK al proyecto. Esta extracción demuestra lectura y conversión del activo local, no licencia de redistribución ni carga en Lineage II. No se modificaron archivos de L2.
