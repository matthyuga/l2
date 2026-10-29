"""Generate an actual attachment bone using the native PSK exporter conventions."""
import bpy,sys,json,struct
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils import Quaternion
R=Path(__file__).resolve().parent;LAB=R.parents[2]
sys.path.insert(0,str(LAB/'research/amber-l2/tools/psk_addon'))
import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psk.builder import build_psk,PskBuildOptions
from io_scene_psk_psa.psk.writer import write_psk
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.psk(filepath=str(R/'native-strider/LineageMonsters/SkeletalMesh/strider_m00.psk'))
stock=next(o for o in bpy.data.objects if o.type=='ARMATURE');stock_seat=stock.data.bones['Bone15'].matrix_local.copy()
stock_rotation=stock_seat.to_quaternion();stock_position=list(stock_seat.translation)
sys.path.insert(0,str(LAB/'research/dust2-animation-study/native'))
from write_l2_animation import chunks
size,count,data=chunks(R/'BehemothTwoRiders.psk')['REFSKELT'];world_rot=[];world_pos=[];bone_names=[]
for i in range(count):
 name,flags,children,parent=struct.unpack_from('<64s3i',data,i*size);bone_names.append(name.rstrip(b'\0').decode())
 x,y,z,w,px,py,pz=struct.unpack_from('<7f',data,i*size+76);q=Quaternion((w,x,y,z));loc=Vector((px,py,pz))
 if i==0:world_rot.append(q);world_pos.append(loc)
 else:world_rot.append(world_rot[parent]@q.conjugated());world_pos.append(world_pos[parent]+world_rot[parent]@loc)
parent=bone_names.index('Bip01 Spine1');local_position=world_rot[parent].inverted()@(Vector((0,-6.75,98))-world_pos[parent]);local_rotation=stock_rotation.conjugated()@world_rot[parent];local_rotation.normalize()
record=struct.pack('<64s3i4f3f4f',b'Bone15',0,0,parent,local_rotation.x,local_rotation.y,local_rotation.z,local_rotation.w,*local_position,0,0,0,0)
assert len(record)==120;(R/'SeatBoneNativeRecord.bin').write_bytes(record)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.psk(filepath=str(R/'native-source/LineageMonsters3/SkeletalMesh/antaras_ex_a_m00.psk'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
bone=rig.data.edit_bones.new('Bone15');bone.parent=rig.data.edit_bones['Bip01 Spine1'];m=stock_rotation.to_matrix().to_4x4();m.translation=Vector((0,-6.75,98));bone.matrix=m;bone.length=1
bpy.ops.object.mode_set(mode='OBJECT');bpy.ops.object.select_all(action='DESELECT')
meshes=[o for o in bpy.data.objects if o.type=='MESH'];materials=[]
for o in meshes:
 o.select_set(True)
 for material in o.data.materials:
  if material.name not in materials:materials.append(material.name)
bpy.context.view_layer.objects.active=meshes[0];options=PskBuildOptions();options.material_names=materials
write_psk(build_psk(bpy.context,options),str(R/'SeatBoneExport.psk'))
(R/'seat-orientation-reference.json').write_text(json.dumps({'reference':'original LineageMonsters.strider_m00 Bone15','stockQuaternionWXYZ':list(stock_rotation),'stockPosition':stock_position,'behemothSeatPosition':[0,-6.75,98]},indent=2))
print('REAL_SEAT_BONE_EXPORTED',len(rig.data.bones))
