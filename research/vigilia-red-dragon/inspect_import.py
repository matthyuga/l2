import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('E:/l2-local');out=root/'research/vigilia-red-dragon'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(out/'source/source/RedDragon.fbx'))
report={'objects':[],'bones':[],'actions':[],'materials':[]}
for o in bpy.data.objects:
 item={'name':o.name,'type':o.type,'dimensions':list(o.dimensions),'rotation':list(o.rotation_euler),'scale':list(o.scale),'location':list(o.location)}
 if o.type=='MESH':item.update({'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'groups':[g.name for g in o.vertex_groups],'materials':[m.name if m else None for m in o.data.materials],'bounds':[list(o.matrix_world@Vector(c)) for c in o.bound_box]})
 if o.type=='ARMATURE':
  for b in o.data.bones:report['bones'].append({'name':b.name,'head':list(o.matrix_world@b.head_local),'tail':list(o.matrix_world@b.tail_local),'parent':b.parent.name if b.parent else None})
 report['objects'].append(item)
for a in bpy.data.actions:report['actions'].append({'name':a.name,'frames':list(a.frame_range)})
for m in bpy.data.materials:report['materials'].append({'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None} for n in m.node_tree.nodes] if m.use_nodes else []})
(out/'import-inventory.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'RedDragon-source-import.blend'))
print('INVENTORY',[(o['name'],o['type'],o.get('vertices')) for o in report['objects']],flush=True)
print('BONES', [b['name'] for b in report['bones']],flush=True)
