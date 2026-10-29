import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;LAB=R.parents[2]
sys.path.insert(0,str(LAB/'research/amber-l2/tools/psk_addon'))
import io_scene_psk_psa;io_scene_psk_psa.register()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.psk(filepath=str(R/'native-source/LineageMonsters3/SkeletalMesh/antaras_ex_a_m00.psk'))
native=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(LAB/'research/model-catalog/exports/l2lab-behemoth-two-riders/behemoth-two-riders.gltf'))
def info(o):
 d={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None}
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];d['bounds']=[[min(p[k] for p in pts) for k in range(3)],[max(p[k] for p in pts) for k in range(3)]]
 if o.type=='ARMATURE':d['bones']=[b.name for b in o.data.bones]
 return d
out={'native':[info(o) for o in native],'kit':[info(o) for o in bpy.data.objects if o not in native]}
blend=LAB/'research/dust2-animation-study/retarget/Dust2_BombWork_FFighter.blend'
with bpy.data.libraries.load(str(blend),link=False) as (a,b):out['characterSourceObjects']=a.objects;out['characterActions']=a.actions
(R/'blender-inventory.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('BEHEMOTH_INVENTORY_READY')
