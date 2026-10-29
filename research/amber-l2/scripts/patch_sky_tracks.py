exec(open(__file__.replace('patch_sky_tracks.py','inspect_bow_pose.py')).read())
import struct,math
from mathutils import Quaternion
from io_scene_psk_psa.psa.importer import ImportBone,_calculate_fcurve_data
meta=json.loads((ROOT/'reports/archer-native-tracks.json').read_text())
native=bytearray((ROOT/'reports/archer-animation-native.bin').read_bytes())
seqs=json.loads((ROOT/'reports/fighter-sequences.json').read_text())
patched=0
for seq in opts.sequence_names:
    move=meta['moves'][seqs.index(seq)];rig.animation_data.action=bpy.data.actions[seq]
    for boneName in ('Bip01_L_Clavicle','Bip01_R_Clavicle'):
        boneIndex=next(i for i,b in enumerate(meta['bones']) if b[0]==boneName)
        track=move['tracks'][move['indices'].index(boneIndex)]
        rb=rig.data.bones[boneName]
        ib=ImportBone(None);ib.orig_quat=Quaternion(rb['orig_quat']);ib.post_quat=Quaternion(rb['post_quat']);ib.parent=True
        for key in range(track['quat_count']):
            time=struct.unpack_from('<f',native,track['time_offset']+4*min(key,max(0,track['time_count']-1)))[0] if track['time_count'] else 60
            bpy.context.scene.frame_set(1+int(time));bpy.context.view_layer.update();pb=rig.pose.bones[boneName]
            matrix=pb.matrix.copy();position=matrix.translation.copy()
            rotation=Quaternion((1,0,0),math.radians(-55))@matrix.to_quaternion()
            matrix=rotation.to_matrix().to_4x4();matrix.translation=position;pb.matrix=matrix;bpy.context.view_layer.update()
            wanted=pb.rotation_quaternion.copy()
            q=ib.orig_quat@ib.post_quat@wanted.conjugated()@ib.post_quat.conjugated();q.normalize()
            result=Quaternion(_calculate_fcurve_data(ib,(q.w,q.x,q.y,q.z,0,0,0))[:4]);assert abs(result.dot(wanted))>0.9999
            struct.pack_into('<4f',native,track['quat_offset']+16*key,q.x,q.y,q.z,q.w);patched+=1
(ROOT/'exports/archer-sky-native.bin').write_bytes(native)
(ROOT/'reports/archer-sky-patch.json').write_text(json.dumps(dict(keys=patched,angle=-55,sequences=opts.sequence_names,byte_size_preserved=True),indent=2))
print('SKY_PATCH',patched)
