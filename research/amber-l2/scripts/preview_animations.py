import bpy
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/psk_addon'))
import io_scene_psk_psa
io_scene_psk_psa.register()
from io_scene_psk_psa.psa.reader import PsaReader
from io_scene_psk_psa.psa.importer import import_psa, PsaImportOptions
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'exports/amber-l2-rigged.blend'))
rig=bpy.data.objects['L2_FFemale_Rig']
reader=PsaReader(str(ROOT/'exports/l2-reference/Fighter/MeshAnimation/FFighter_anim.psa'))
names=list(reader.sequences)
(ROOT/'reports/fighter-sequences.json').write_text(json.dumps(names,indent=2),encoding='utf8')
options=PsaImportOptions()
options.should_use_fake_user=True
options.sequence_names=[n for n in names if n in ('Wait_Hand_FFighter','Walk_Hand_FFighter','Run_Hand_FFighter','AtkWait_Bow_FFighter','Atk01_Bow_FFighter')]
if not options.sequence_names:
    options.sequence_names=[n for n in names if any(s in n.lower() for s in ('wait','walk'))][:4]
result=import_psa(bpy.context,reader,rig,options)
rig.animation_data_create()
rig.animation_data.action=bpy.data.actions.get('Wait_Hand_FFighter') or bpy.data.actions[options.sequence_names[0]]
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'exports/amber-l2-animated.blend'))
(ROOT/'reports/animation-preview.json').write_text(json.dumps({'sequences':options.sequence_names,'warnings':result.warnings},indent=2),encoding='utf8')
print('IMPORTED ORIGINAL ANIMATIONS',options.sequence_names,result.warnings)
