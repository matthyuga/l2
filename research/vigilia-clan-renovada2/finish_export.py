"""Finish the landing edge under its final railing post and refresh the export."""
import bpy,json
from pathlib import Path
OUT=Path(__file__).resolve().parent;R=OUT.parents[1];EXP=R/'research/model-catalog/exports/vigilia-renovada2'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Vigilia-renovada2.blend'))
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith('Pasarela a azotea') and not o.get('landing_edge_finished'):
  for v in o.data.vertices:v.co.x=-13.25+(v.co.x+13.25)*(1.4/1.3)
  o['landing_edge_finished']=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Vigilia-renovada2.blend'))
for col in bpy.data.collections:
 if not col.name.startswith('VIG_'):continue
 meshes=[o for o in col.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.select_set(True)
 if len(meshes)>1:bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();bpy.context.object.name=col.name+'_Mobiliario'
bpy.ops.object.select_all(action='DESELECT')
for col in bpy.data.collections:
 if col.name.startswith('VIG_'):
  for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(EXP/'vigilia.gltf'),export_format='GLTF_SEPARATE',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
file=EXP/'vigilia.gltf';g=json.loads(file.read_text(encoding='utf-8'))
for m in g['materials']:
 if 'Parabrisas transparente' in m['name']:m['alphaMode']='BLEND';m['doubleSided']=True
 if 'Roble restaurado' in m['name']:m['pbrMetallicRoughness']['baseColorFactor']=[.42,.29,.19,1]
file.write_text(json.dumps(g,ensure_ascii=False),encoding='utf-8')
