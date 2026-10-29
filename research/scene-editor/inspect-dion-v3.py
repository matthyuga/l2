from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parent
a=json.loads((R.parent/'scenario-batches/library_fe488fdfccee/actors.json').read_text())
names=[x['actor']+'_0' for x in a if (14500<x.get('Location',[0])[0]<22000 and 141000<x.get('Location',[0,0])[1]<148000 and any(w in x['StaticMesh'].lower() for w in ['manor','wall','fence']))]
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(R.parent/'scenario-batches/library_fe488fdfccee/scene-with-terrain.blend')) as (src,dst):dst.objects=names
out=[]
for o in dst.objects:
 if not o:continue
 bpy.context.scene.collection.objects.link(o)
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 out.append({'name':o.name,'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)],'materials':[m.name for m in o.data.materials]})
(R/'dion-v3-inspection.json').write_text(json.dumps(out,indent=2))
