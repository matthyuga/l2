import bpy,json
from pathlib import Path
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'v4-textures/RifleNPCV4.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');s=bpy.context.scene
out={}
for f in [1,30,62,126]:
 s.frame_set(f);bpy.context.view_layer.update();out[f]={}
 for name in ['bip01_l_foot','Bip01_L_Toe0','bip01_r_foot','Bip01_R_Toe0','Bip01_head','Bip01_R_Hand']:
  p=rig.pose.bones[name];out[f][name]={'head':list(p.head),'tail':list(p.tail),'local_rotation':list(p.rotation_quaternion),'rest_head':list(p.bone.head_local),'rest_tail':list(p.bone.tail_local)}
(R/'pose-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out[1],indent=2))
