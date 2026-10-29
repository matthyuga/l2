import pathlib,json,sqlite3
from build_database import ROOT,CAT,PRIMARY

d=json.loads((CAT/'rig-data'/ (PRIMARY+'.json')).read_text('utf-8'));db=sqlite3.connect(ROOT/'rig-catalog.sqlite')
counts={table:db.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in ['models','nodes','joints','clips','channels','source_bones','source_actions','segments','experiments']};db.close()
clip=d['clips'][0];source=d['fbx_observation'];correlation=d['fbx_correlation'];poses=d['sampled_pose_verification'];comparisons=json.loads((CAT/'rig-data/sett-comparisons.json').read_text('utf-8'))
by_node={b['node']:b for b in d['bones']};children={}
for b in d['bones']:children.setdefault(b['parent_node'],[]).append(b)
lines=[]
def tree(parent,depth=0):
    for b in children.get(parent,[]):
        lines.append('  '*depth+b['name']+' [nodo '+str(b['node'])+'; incidencias con peso '+str(b['weighted_vertices'])+']');tree(b['node'],depth+1)
tree(None);(ROOT/'sett-hierarchy.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
text=f'''# Base fiable de rigs y animaciones — Sett

Revisión del 28/10/2026. Objetivo: conservar mediciones verificables para comparar esqueletos y preparar experimentos, sin confundir coincidencias con compatibilidad demostrada.

[Abrir ficha técnica interactiva](http://127.0.0.1:32280/rig-inspector.html?model={PRIMARY})

## Resultado de Sett

| Dato | Medición y alcance |
|---|---|
| Huesos | {d['joint_count']} joints en el GLB; {correlation['source_joint_count']} bones tras importar el FBX |
| Con pesos | {sum(b['weighted_vertices']>0 for b in d['bones'])} joints con influencias positivas en las primitivas exportadas |
| Animaciones | {d['clip_count']} clip, sin segmentación semántica |
| Tiempo del GLB | {clip['start_seconds']:.9f} a {clip['end_seconds']:.9f} segundos |
| Duración del clip | {clip['duration_seconds']:.9f} segundos |
| Importación FBX | {source['scene_fps']/source['scene_fps_base']} FPS; acción entre frames {source['actions'][0]['frame_range'][0]} y {source['actions'][0]['frame_range'][1]} |
| Curvas FBX importadas | {source['actions'][0]['curve_count']} curvas escalares; {source['actions'][0]['keyframe_count']:,} puntos observados por Blender |
| Pistas GLB | {clip['channel_count']} canales vectoriales TRS; {clip['varying_channels']} con variación por encima de 1e-6 |
| Nombres y padres | Sin huesos perdidos/añadidos y sin discrepancias de parentesco entre ambos formatos |
| Poses muestreadas | {poses['compared_joint_positions']} posiciones de joints en {len(poses['samples'])} instantes; error máximo {poses['max_error_world_units']:.12f} unidades globales |

Las curvas escalares y los canales vectoriales no son la misma unidad: una rotación quaternion ocupa cuatro curvas escalares y una pista vectorial. Los 60 FPS corresponden a la escena importada; glTF almacena tiempos en segundos y no exige una frecuencia global fija.

## Base de datos

Archivo: [rig-catalog.sqlite](rig-catalog.sqlite). Versión de esquema 1.

'''
text+='\n'.join('- '+k+': '+str(v) for k,v in counts.items())
text+='''

La base contiene matrices locales/globales de referencia, matrices inversas de enlace, orden de joints por skin, parentesco, incidencias de pesos, canales, interpolación, tiempos y valores. Las muestras de los canales glTF se guardan completas como bytes compactos comprimidos con zlib, con tipo de componente, tamaño y SHA-256. No se almacenan solamente estadísticas o capturas de pantalla.

Las incidencias de pesos corresponden a vértices de primitivas exportadas: pueden incluir duplicados por UV/material e instancias. No equivalen a un recuento de vértices únicos del FBX.

El contraste directo FBX/GLB está realizado para Sett. Los otros 28 modelos tienen una medición del GLB, sin afirmar una validación equivalente de sus originales.

## Evidencia y versiones

- REA inspeccionó `sett.zip`: inventario de 22 entradas del directorio central, sin contradicciones de integridad reportadas.
- Evidencia de inspección: `ev_1a4509f2d15947a6818745a03365c1b51eb72b6691e7c446a631405625ffc18e`.
- Inventario: `ev_dcba1f8726194379f1b2050da224b8e088ace1200000b5c6846a94f988867a80`.
- [Bundle REA completo](rea-sett-evidence.json). REA no interpretó los huesos ni ejecutó el modelo; esa parte procede de Blender y de la decodificación de glTF.
- [Observación FBX](sett-fbx-observation.json), [correlación](sett-correlation.json) y [prueba de poses](sett-pose-verification.json).
- `snapshots/` conserva copias del ZIP, FBX y GLB de Sett bajo sus SHA-256. La copia FBX coincide con el miembro original del ZIP.
- La ficha verifica el SHA-256 del GLB antes de mostrarlo. Un cambio bloquea su presentación como la revisión anterior.
- `build_database.py` rechaza sustituir silenciosamente una malla de otro hash bajo la misma clave. Antes de una nueva pasada conserva una copia SQLite coherente en `database-revisions/`.

## Comparación preliminar

'''
for c in comparisons:
    title=next(m['title'] for m in json.loads((CAT/'rig-data/index.json').read_text('utf-8'))['models'] if m['key']==c['target'])
    text+=f'- Sett → {title}: {c["candidate_count"]} candidatos por nombre normalizado; {c["same_parent_candidate_count"]} con nombre de padre coincidente. Transferencia sin probar.\n'
text+='''
No hay un porcentaje de compatibilidad inventado. La comparación no prueba igualdad de proporciones, ejes locales, matrices de enlace, contactos de pies/manos, movimiento de raíz ni función de los apéndices.

## Qué queda sin establecer

- Los ataques, reposos, poses y muertes aún no tienen etiquetas ni cortes confirmados. La tabla `segments` está vacía.
- No se trasladó ninguna animación a otro modelo. La tabla `experiments` está vacía.
- Las etiquetas anatómicas son hipótesis basadas en nombres y están marcadas `unverified`.
- La prueba FBX/GLB cubre posiciones de joints en 11 instantes; no demuestra equivalencia en todos los frames, orientaciones o deformaciones de malla.
- No se validó ni instaló una adaptación UKX/UTX para Interlude.

## Uso para experimentar con control

1. Elegir un intervalo temporal y confirmar visualmente qué movimiento contiene. Guardar sus límites como segmento, conservando el clip completo.
2. Elegir esqueleto destinatario y revisar una correspondencia explícita de huesos, con especial atención a apéndices y padres diferentes.
3. Generar el resultado en un archivo nuevo. Conservar huellas de origen, parámetros, versión de herramientas y resultado de la prueba.
4. Comparar pose, proporciones y contactos antes de adaptar al cliente. Un resultado fallido también debe conservar su registro.

## Verificación

- [Prueba de SQLite y blobs](database-verification.json): integridad, claves foráneas, tamaño y hash de todos los canales descomprimidos, y hashes de las tres copias de Sett.
- [Prueba del navegador](browser-verification.json): jerarquía 3D, búsqueda y selección de huesos, pistas, comparación, reproducción/pausa, cambio de modelo y acceso desde la galería.
- [Jerarquía completa en texto](sett-hierarchy.txt).

Los originales y los favoritos del navegador real no se modificaron. Respaldo de la integración del catálogo en `E:\\l2-local\\backups\\rig-database-20261028`.
'''
(ROOT/'REVISION.md').write_text(text,encoding='utf-8');print('Rig report saved.')
