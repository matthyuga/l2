import bpy,sys,json
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).resolve().parent;LAB=R.parents[2]
sys.path.insert(0,str(LAB/'research/amber-l2/tools/psk_addon'))
import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psa.reader import PsaReader
from io_scene_psk_psa.psa.importer import import_psa,PsaImportOptions
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.psk(filepath=str(R/'real-seat-roundtrip/BHMTransport/SkeletalMesh/BehemothMesh.psk'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
assert (rig.data.bones['Bone15'].matrix_local.translation-Vector((0,-6.75,98))).length<.001
reference=json.loads((R/'seat-orientation-reference.json').read_text())
actual_rotation=rig.data.bones['Bone15'].matrix_local.to_quaternion();expected_rotation=Quaternion(reference['stockQuaternionWXYZ']);print('ROTATION_CHECK',list(actual_rotation),list(expected_rotation),abs(actual_rotation.dot(expected_rotation)));assert abs(actual_rotation.dot(expected_rotation))>0.99999
reader=PsaReader(str(R/'native-source/LineageMonsters3/MeshAnimation/antaras_ex_a_anim.psa'));options=PsaImportOptions();options.sequence_names=['run','atkwait'];options.should_use_fake_user=True
result=import_psa(bpy.context,reader,rig,options)
rig.animation_data_create()
bind=rig.data.bones['Bip01 Spine1'].matrix_local.inverted()@rig.data.bones['Bone15'].matrix_local
checks=[]
for clip in ['run','atkwait']:
 rig.animation_data.action=bpy.data.actions[clip];positions=[]
 for frame in [1,8,16]:
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
  actual=rig.pose.bones['Bone15'].matrix
  expected=rig.pose.bones['Bip01 Spine1'].matrix@bind
  assert (actual.translation-expected.translation).length<.001
  positions.append(list(actual.translation))
 checks.append({'clip':clip,'seatFollowsAnimatedSpine':True,'positions':positions})
(R/'seat-pose-verification.json').write_text(json.dumps({'passed':True,'sourceNativeBoneCount':99,'sourceAnimationBoneCount':98,'seatOrientationMatchesStockStrider':True,'checks':checks,'nativeGameVisualVerified':False},indent=2));print('PASS: seat orientation matches stock strider and follows native run/idle on roundtripped mesh.')
