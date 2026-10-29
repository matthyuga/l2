import bpy,sys,json,math
from pathlib import Path
R=Path(__file__).parent;sys.path.insert(0,str(R));import nexus_animation_lab as lab
lab.register();sys.path.insert(0,str(lab.ADDON));import io_scene_psk_psa;io_scene_psk_psa.register()
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'research/dust2-animation-study/retarget/Dust2_BombWork_FFighter-QA.blend'))
# Remove QA floor/lights/camera and keep body materials for interactive solid view.
for o in list(bpy.data.objects):
 if o.type in ['LIGHT','CAMERA'] or o.name=='Plane':bpy.data.objects.remove(o,do_unlink=True)
r=next(o for o in bpy.data.objects if o.type=='ARMATURE')
from io_scene_psk_psa.psa.reader import PsaReader
from io_scene_psk_psa.psa.importer import import_psa,PsaImportOptions
reader=PsaReader(str(R.parent/'research/amber-l2/exports/l2-reference/Fighter/MeshAnimation/FFighter_anim.psa'))
wanted=[n for n in reader.sequences if any(t in n.lower() for t in ['wyvern','strider','cast','bow','social','walk_hand','run_hand'])]
opt=PsaImportOptions();opt.should_use_fake_user=True;opt.sequence_names=wanted;result=import_psa(bpy.context,reader,r,opt)
# Preserve separate pure Studio crouch as another blendable action.
with bpy.data.libraries.load(str(R.parent/'research/dust2-animation-study/retarget/StudioSquat_FFighter.blend'),link=False) as (src,dst):dst.actions=[n for n in src.actions if n=='StudioSquat_FFighter']
for a in bpy.data.actions:a.use_fake_user=True
s=bpy.context.scene.nl2;s.rig=r;s.base=next(n for n in wanted if 'Wyvern' in n);s.overlay=next(n for n in wanted if 'Cast' in n);s.output_name='Wyvern_Conjuro_Prueba';s.length=120
bpy.context.scene.render.fps=30
bpy.ops.object.select_all(action='DESELECT');r.select_set(True);bpy.context.view_layer.objects.active=r
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.show_region_ui=True;area.spaces.active.region_3d.view_distance=80;area.spaces.active.region_3d.view_location=(0,0,22)
   area.spaces.active.shading.type='MATERIAL'
# Meaningful evaluation tests: masked legs/root reproduce base; arm overlay weight1 reproduces overlay quaternion.
a=bpy.data.actions[s.base];b=bpy.data.actions[s.overlay];pa=lab.sample(a,r,lab.frame_at(a,15,1,0,True));pb=lab.sample(b,r,lab.frame_at(b,15,1,0,True));first=lab.sample(a,r,float(a.frame_range[0]))
mix=lab.mix(bpy.context);actual=lab.sample(mix,r,16)
errors={}
for n in ['Bip01_Pelvis','Bip01_L_Thigh','Bip01_R_Thigh','Bip01_L_Calf']:
 errors[n]=max(abs(actual[n][i][j]-pa[n][i][j]) for i in range(4) for j in range(4));assert errors[n]<1e-4
for n in ['Bip01_L_UpperArm','Bip01_R_UpperArm']:
 q=actual[n].to_quaternion();p=pb[n].to_quaternion();assert abs(abs(q.dot(p))-1)<1e-5
assert (actual['Bip01'].translation-first['Bip01'].translation).length<1e-4
r.animation_data.action=mix;bpy.context.scene.frame_set(1)
(R/'validation.json').write_text(json.dumps({'library_native_actions':wanted,'warnings':result.warnings,'leg_root_mask_max_error':errors,'arms_weight1_quaternion_matches_overlay':True,'root_fixed':True,'game_installation':False},indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Nexus-L2-Animation-Lab.blend'))
# Export through actual UI operator as a smoke proof.
out=bpy.ops.nl2.export();assert out=={'FINISHED'},out
print('ANIMATION_LAB_READY',len(wanted),'native actions; mixer masks and export PASS')
