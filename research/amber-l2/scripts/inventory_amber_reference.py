import bpy,json
from pathlib import Path
r=Path('E:/l2-local/research/amber-l2')
report={}
for name in ['amber-imported.blend','amber-l2-rigged.blend']:
 try:bpy.ops.wm.open_mainfile(filepath=str(r/'exports'/name))
 except RuntimeError as e:print('READ_WARNING',str(e))
 rows=[]
 for o in bpy.data.objects:
  if o.type=='MESH': rows.append(dict(name=o.name,hide=o.hide_render,vertices=len(o.data.vertices),triangles=sum(len(p.vertices)-2 for p in o.data.polygons),dims=list(o.dimensions),location=list(o.location),rotation=list(o.rotation_euler),materials=[dict(name=m.name,images=[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]) for m in o.data.materials if m]))
 report[name]=rows
(r/'reference-models/amber-web-2026-10-23/local-blender-inventory.json').write_text(json.dumps(report,indent=2))
print('Inventory saved')
