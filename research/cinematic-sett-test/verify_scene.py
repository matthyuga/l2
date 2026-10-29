import bpy,json,pathlib
from mathutils import Vector
p=pathlib.Path(r'E:\l2-local\research\cinematic-sett-test');s=bpy.context.scene;r=next(o for o in s.objects if o.type=='ARMATURE');a=bpy.data.objects['Sett_Walk_Controller']
res={'packed_images':[(i.name,bool(i.packed_file),i.filepath) for i in bpy.data.images if i.type=='IMAGE'],'frames':[]}
for f in [1,13,25,49,97,145,192]:
 s.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();er=r.evaluated_get(deps)
 row={'frame':f,'actor':list(a.location),'feet':{side:list(er.matrix_world@er.pose.bones['bip001_'+side+'_foot'].head) for side in ['l','r']}};res['frames'].append(row)
(p/'verification-scene.json').write_text(json.dumps(res,indent=2));print('SCENE_VERIFIED')
