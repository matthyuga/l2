import bpy,sys,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/psk_addon'))
import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psa.reader import PsaReader
from io_scene_psk_psa.psa.importer import import_psa,PsaImportOptions
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'exports/amber-l2-animated.blend'))
rig=bpy.data.objects['L2_FFemale_Rig'];reader=PsaReader(str(ROOT/'exports/l2-reference/Fighter/MeshAnimation/FFighter_anim.psa'))
opts=PsaImportOptions();opts.sequence_names=['SpAtk01_Bow_FFighter','SpAtk02_Bow_FFighter'];import_psa(bpy.context,reader,rig,opts)
out=[]
for name in opts.sequence_names:
    rig.animation_data.action=bpy.data.actions[name]
    for frame in (1,30,60,90):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        positions={n:list(rig.matrix_world@rig.pose.bones[n].head) for n in ('Bip01_L_Hand','Bip01_R_Hand','Bip01_head')}
        out.append(dict(sequence=name,frame=frame,positions=positions))
(ROOT/'reports/bow-poses.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
