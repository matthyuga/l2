import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
r=Path('E:/l2-local/research/mounts/behemoth-v2');bpy.ops.wm.open_mainfile(filepath=str(r/'Behemoth-Two-Riders.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and len(o.data.bones)==98)
# Reference pose frame: root is irrelevant, convert the pelvis target into bind bone coordinates.
bone=rig.data.bones['Bip01 Spine1'];matrix=bone.matrix_local
origin=matrix.inverted()@Vector((0,-6.75,98.0))
q=matrix.to_quaternion().inverted();e=q.to_euler('XYZ')
result={'bone':'Bip01 Spine1','tag':'Bone15','position':list(origin),'rotationBytes':{'ROLL':round(e.x*128/math.pi),'PITCH':round(e.y*128/math.pi),'YAW':round(e.z*128/math.pi)}}
(r/'native-seat-socket.json').write_text(json.dumps(result,indent=2));print('NATIVE_SOCKET',result)
