import bpy,sys,json
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
ROOT=Path(__file__).parent
source=Path(sys.argv[sys.argv.index('--')+1])
d=json.loads(source.read_text(encoding='utf-8-sig'))
bones=d['bones'];frames=d['frames']; names={b['name']:i for i,b in enumerate(bones)}
C=Matrix(((-1,0,0),(0,0,-1),(0,1,0)))
C4=C.to_4x4()
def mat(t):
 q=t['rotation'];return Matrix.LocRotScale(Vector(t['position']),Quaternion((q[3],q[0],q[1],q[2])),Vector(t.get('scale',[1,1,1])))
def hierarchy(ts):
 worlds=[None]*len(bones)
 def calc(i):
  if worlds[i] is None:
   p=bones[i]['parent']; local=mat(ts[i]); worlds[i]=calc(p)@local if p>=0 else local
  return worlds[i]
 for i in range(len(bones)):calc(i)
 return [C4@m@C4.inverted() for m in worlds]
rest=hierarchy([b['rest'] for b in bones])
hands_path=source.parent/'f_suwari_00_10_M.motion.json'
hands=json.loads(hands_path.read_text()) if '--hands' in sys.argv else None
outname=source.stem.replace('.motion','')+'_FFighter'
if hands:
 assert [b['name'] for b in hands['bones']]==[b['name'] for b in bones]
 frames=[{'time':h['time'],'transforms':frames[i%(len(frames)-1)]['transforms'],'hands':h['transforms']} for i,h in enumerate(hands['frames'])]

sys.path.insert(0,r'E:\l2-local\research\amber-l2\tools\psk_addon')
import io_scene_psk_psa
io_scene_psk_psa.register()
bpy.ops.wm.open_mainfile(filepath=r'E:\l2-local\research\amber-l2\exports\fighter-reference.blend')
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
# Assemble original native outfit pieces onto the exact reference skeleton.
for path in (Path(r'E:\l2-local\research\dust2-animation-study\retarget\native-meshes\Fighter\SkeletalMesh')).glob('*.psk'):
 before=set(bpy.data.objects);bpy.ops.import_scene.psk(filepath=str(path));added=set(bpy.data.objects)-before
 for obj in added:
  if obj.type=='MESH':
   for mod in obj.modifiers:
    if mod.type=='ARMATURE':mod.object=rig
   obj.parent=rig
 for obj in added:
  if obj.type=='ARMATURE':bpy.data.objects.remove(obj,do_unlink=True)
# Exact anatomical pairs; corrective/cloth bones inherit parent motion.
mapping={'cf_j_hips':'Bip01_Pelvis','cf_j_spine01':'bip01_spine','cf_j_spine02':'Bip01_Spine1','cf_j_spine03':'bip01_spine2','cf_j_neck':'Bip01_Neck','cf_j_head':'Bip01_head','cf_j_shoulder_L':'Bip01_L_Clavicle','cf_j_arm00_L':'Bip01_L_UpperArm','cf_j_forearm01_L':'Bip01_L_Forearm','cf_j_hand_L':'Bip01_L_Hand','cf_j_shoulder_R':'Bip01_R_Clavicle','cf_j_arm00_R':'Bip01_R_UpperArm','cf_j_forearm01_R':'Bip01_R_Forearm','cf_j_hand_R':'Bip01_R_Hand','cf_j_thigh00_L':'Bip01_L_Thigh','cf_j_leg01_L':'Bip01_L_Calf','cf_j_foot_L':'bip01_l_foot','cf_j_toes_L':'Bip01_L_Toe0','cf_j_thigh00_R':'Bip01_R_Thigh','cf_j_leg01_R':'Bip01_R_Calf','cf_j_foot_R':'bip01_r_foot','cf_j_toes_R':'Bip01_R_Toe0'}
mapping={s:t for s,t in mapping.items() if s in names and t in rig.data.bones}
assert len(mapping)>=18,('Insufficient anatomy mapping',mapping,list(names))
reverse={t:s for s,t in mapping.items()}
next_joint={'cf_j_hips':'cf_j_spine01','cf_j_spine01':'cf_j_spine02','cf_j_spine02':'cf_j_spine03','cf_j_spine03':'cf_j_neck','cf_j_neck':'cf_j_head','cf_j_shoulder_L':'cf_j_arm00_L','cf_j_arm00_L':'cf_j_forearm01_L','cf_j_forearm01_L':'cf_j_hand_L','cf_j_shoulder_R':'cf_j_arm00_R','cf_j_arm00_R':'cf_j_forearm01_R','cf_j_forearm01_R':'cf_j_hand_R','cf_j_thigh00_L':'cf_j_leg01_L','cf_j_leg01_L':'cf_j_foot_L','cf_j_foot_L':'cf_j_toes_L','cf_j_thigh00_R':'cf_j_leg01_R','cf_j_leg01_R':'cf_j_foot_R','cf_j_foot_R':'cf_j_toes_R'}
hip=names['cf_j_hips'];foot=names['cf_j_foot_L']
scale=(rig.data.bones['Bip01_Pelvis'].head_local.z-rig.data.bones['bip01_l_foot'].head_local.z)/(rest[hip].translation.z-rest[foot].translation.z)
rig.animation_data_create();action=bpy.data.actions.new(outname);rig.animation_data.action=action
bpy.context.scene.render.fps=round(d['fps']);bpy.context.scene.frame_end=len(frames)
audit=[]
for frame_no,frame in enumerate(frames,1):
 pose=hierarchy(frame['transforms']);handpose=hierarchy(frame['hands']) if hands else None;bpy.context.scene.frame_set(frame_no)
 for pb in rig.pose.bones:
  pb.rotation_mode='QUATERNION'
  if pb.name in reverse:
   i=names[reverse[pb.name]]
   active_pose=handpose if handpose and any(k in reverse[pb.name] for k in ['shoulder','arm00','forearm','hand']) else pose
   delta=active_pose[i].to_quaternion()@rest[i].to_quaternion().inverted()
   srcname=reverse[pb.name]
   if srcname in next_joint and next_joint[srcname] in names and next_joint[srcname] in mapping:
    dstchild=rig.data.bones[mapping[next_joint[srcname]]]
    a=dstchild.head_local-pb.bone.head_local
    b=active_pose[names[next_joint[srcname]]].translation-active_pose[i].translation
    if a.length>1e-7 and b.length>1e-7:delta=a.normalized().rotation_difference(b.normalized())
   target=(delta@pb.bone.matrix_local.to_quaternion()).to_matrix().to_4x4()
   if pb.name=='Bip01_Pelvis':
    target.translation=pb.bone.head_local+(pose[hip].translation-rest[hip].translation)*scale
   else:
    # Preserve L2 segment lengths; position follows animated parent.
    local_rest=pb.parent.bone.matrix_local.inverted()@pb.bone.matrix_local if pb.parent else pb.bone.matrix_local
    target.translation=(pb.parent.matrix@local_rest).translation if pb.parent else pb.bone.head_local
   pb.matrix=target
  else:pb.matrix_basis=Matrix.Identity(4)
  bpy.context.view_layer.update()
  pb.keyframe_insert(data_path='rotation_quaternion',frame=frame_no)
  pb.keyframe_insert(data_path='location',frame=frame_no)
 # Ground the evaluated boot meshes rather than the ankle joint center.
 bpy.context.view_layer.update()
 boots=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('FFighter_m001_b')]
 dg=bpy.context.evaluated_depsgraph_get()
 min_z=min((o.matrix_world@v.co).z for o in boots for v in o.evaluated_get(dg).data.vertices)
 rootpb=rig.pose.bones['Bip01'];rootmatrix=rootpb.matrix.copy();rootmatrix.translation.z-=min_z;rootpb.matrix=rootmatrix
 rootpb.keyframe_insert(data_path='rotation_quaternion',frame=frame_no);rootpb.keyframe_insert(data_path='location',frame=frame_no)
 bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get()
 after=min((o.matrix_world@v.co).z for o in boots for v in o.evaluated_get(dg).data.vertices)
 audit.append({'frame':frame_no,'boot_min_before':min_z,'boot_min_after':after,'root':list(rootpb.matrix.translation),'left_ankle':list(rig.pose.bones['bip01_l_foot'].matrix.translation),'right_ankle':list(rig.pose.bones['bip01_r_foot'].matrix.translation)})
for fc in action.fcurves:
 for kp in fc.keyframe_points:kp.interpolation='LINEAR'
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
from io_scene_psk_psa.psa.builder import build_psa,PsaBuildOptions,PsaBuildSequence
from io_scene_psk_psa.psa.writer import write_psa
opt=PsaBuildOptions();opt.animation_data=rig.animation_data
seq=PsaBuildSequence();seq.name=outname;seq.nla_state.action=action;seq.nla_state.frame_start=1;seq.nla_state.frame_end=len(frames);seq.fps=d['fps'];opt.sequences=[seq]
psa=build_psa(bpy.context,opt);write_psa(psa,str(ROOT/(outname+'.psa')))
bpy.context.scene.frame_set(len(frames)//2)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(outname+'.blend')))
(ROOT/(outname+'-report.json')).write_text(json.dumps({'source':str(source),'mapping':mapping,'scale':scale,'frames':len(frames),'fps':d['fps'],'bones':len(rig.data.bones),'limitations':['First automatic retarget; visual QA and foot/hand correction required.','Exercise movement, not final bomb choreography.','Only female Fighter skeleton.']},indent=2))
print('RETARGET_PSA_EXPORTED',len(psa.bones),len(psa.keys))

(ROOT/(outname+'-grounding.json')).write_text(json.dumps({'native_root_rest':list(rig.data.bones['Bip01'].head_local),'frames':audit,'max_abs_boot_ground_error':max(abs(a['boot_min_after']) for a in audit)},indent=2))
