import bpy,json,pathlib
from mathutils import Vector
D=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath='E:/l2-local/research/airships/external-downloads/fantasy-steampunk-airship/airship-probe-optimized.blend',load_ui=False,use_scripts=False)
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 points=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
 rows.append(dict(name=o.name,vertices=len(o.data.vertices),bounds=[lo,hi],materials=[m.name for m in o.data.materials if m]))
(D/'base-objects.json').write_text(json.dumps(rows,indent=2))
for r in rows:print(r['name'],r['vertices'],[[round(x,2) for x in p] for p in r['bounds']])
