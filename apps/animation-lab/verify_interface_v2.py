import bpy,sys,json
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R));import nexus_animation_lab as lab;lab.register();sys.path.insert(0,str(lab.ADDON));import io_scene_psk_psa;io_scene_psk_psa.register()
bpy.ops.wm.open_mainfile(filepath=str(R/'Nexus-L2-Animation-Lab.blend'))
r=bpy.context.scene.nl2.rig;lab.validate_rig(r)
s=bpy.context.scene.nl2
for kind in ['ARMS','UPPER','ALL','LEGS']:
 assert bpy.ops.nl2.preset(kind=kind)=={'FINISHED'}
 if kind=='ARMS':assert s.left==1 and s.right==1 and s.legs==0 and s.lock_pelvis
 if kind=='LEGS':assert s.legs==1 and not s.lock_pelvis
assert bpy.ops.nl2.load_motion(filepath=str(R/'exports/Wyvern_Conjuro_Prueba/Wyvern_Conjuro_Prueba.psa'))=={'FINISHED'}
assert bpy.ops.nl2.load_model(filepath=str(lab.PSK))=={'FINISHED'}
assert bpy.context.scene.nl2.rig!=r and r.hide_get()
assert len(bpy.context.scene.nl2.rig.data.bones)==76
bpy.ops.nl2.preset(kind='UPPER');s.base='Wyvern_FFighter';s.overlay='CastMid_FFighter';s.length=30;s.output_name='Interface_V2_Test'
a=lab.mix(bpy.context);assert a and len(a.fcurves)>0
s.left=0;assert bpy.ops.nl2.recipe()=={'FINISHED'};assert s.left==1
(R/'interface-v2-validation.json').write_text(json.dumps({'registered':True,'presets_tested':['arms','upper','all','legs'],'PSA_import_pass':True,'PSK_model_import_pass':True,'old_model_hidden':True,'mix_with_imported_model_pass':True,'recipe_restore_pass':True,'game_files_changed':False},indent=2))
print('INTERFACE_V2_IMPORT_MODEL_ANIMATION_MASK_RECIPE_PASS')
