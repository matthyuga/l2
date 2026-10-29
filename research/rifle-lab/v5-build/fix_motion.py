import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path(__file__).parent;sys.path.insert(0,r'E:\l2-local\research\amber-l2\tools\psk_addon');import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psa.builder import build_psa,PsaBuildOptions,PsaBuildSequence
from io_scene_psk_psa.psa.writer import write_psa
states=json.loads((R.parent/'v4-build/states.json').read_text());outstates=[]
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'v4-motion/Idle_Aiming_FFighter.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');bpy.context.scene.frame_set(1);bpy.context.view_layer.update();rh=rig.pose.bones['Bip01_R_Hand'];lh=rig.pose.bones['Bip01_L_Hand'];gunlocal=rh.matrix.to_quaternion().inverted()@(lh.head-rh.head).normalized()
def sample():return {p.name:(p.location.copy(),p.rotation_quaternion.copy()) for p in rig.pose.bones}
def blend(a,b,t):return {n:(a[n][0].lerp(b[n][0],t),a[n][1].slerp(b[n][1],t)) for n in a}
def assign(pose):
 for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.location=pose[p.name][0];p.rotation_quaternion=pose[p.name][1]
 bpy.context.view_layer.update()
def ground():
 dg=bpy.context.evaluated_depsgraph_get();boots=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('FFighter_m001_b')];lo=min((o.matrix_world@v.co).z for o in boots for v in o.evaluated_get(dg).data.vertices);root=rig.pose.bones['Bip01'];m=root.matrix.copy();m.translation.z-=lo;root.matrix=m;bpy.context.view_layer.update();return lo
allposes=[];metrics=[]
for state in states:
 bpy.ops.wm.open_mainfile(filepath=state['blend']);rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');frames=[];gaze=[]
 for f in range(1,state['frames']+1):
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
  for side,fn in [('L','bip01_l_foot'),('R','bip01_r_foot')]:
   foot=rig.pose.bones[fn];toe=rig.pose.bones['Bip01_'+side+'_Toe0'];a=toe.bone.head_local-foot.bone.head_local;b=toe.head-foot.head;a.z=0;b.z=0
   yaw=math.atan2(b.y,b.x)-math.atan2(a.y,a.x);rot=Matrix.Rotation(yaw,4,'Z')@foot.bone.matrix_local;rot.translation=foot.head;foot.matrix=rot;bpy.context.view_layer.update();toe.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
  if state['state'] in ['aim','fire']:
   rh=rig.pose.bones['Bip01_R_Hand'];head=rig.pose.bones['Bip01_head'];target=(rh.matrix.to_quaternion()@gunlocal).normalized();current=(head.matrix.to_quaternion()@head.bone.matrix_local.to_quaternion().inverted()@Vector((0,-1,0))).normalized();delta=current.rotation_difference(target);m=(delta@head.matrix.to_quaternion()).to_matrix().to_4x4();m.translation=head.head;head.matrix=m;bpy.context.view_layer.update();actual=head.matrix.to_quaternion()@head.bone.matrix_local.to_quaternion().inverted()@Vector((0,-1,0));gaze.append(math.degrees(actual.angle(target)))
  ground();frames.append(sample())
 # Seal the loop locally; source remains retained in V4.
 for i in range(max(0,len(frames)-9),len(frames)):
  t=(i-(len(frames)-9))/8;t=t*t*(3-2*t);frames[i]=blend(frames[i],frames[0],t)
 action=bpy.data.actions.new(state['state']+'_FeetGazeV5');rig.animation_data.action=action
 for f,pose in enumerate(frames,1):
  bpy.context.scene.frame_set(f);assign(pose);ground()
  for p in rig.pose.bones:p.keyframe_insert('location',frame=f);p.keyframe_insert('rotation_quaternion',frame=f)
 for fc in action.fcurves:
  for kp in fc.keyframe_points:kp.interpolation='LINEAR'
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;opt=PsaBuildOptions();opt.animation_data=rig.animation_data;seq=PsaBuildSequence();seq.name=state['state'];seq.nla_state.action=action;seq.nla_state.frame_start=1;seq.nla_state.frame_end=len(frames);seq.fps=60;opt.sequences=[seq];psk=build_psa(bpy.context,opt);dest=R/(state['state']+'.psa');write_psa(psk,str(dest));blendpath=R/(state['state']+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blendpath));state.update(psa=str(dest),blend=str(blendpath));outstates.append(state);metrics.append({'state':state['state'],'max_gaze_error_degrees':max(gaze) if gaze else None,'toe_bending_removed':True});print('V5',metrics[-1],flush=True)
 # Visual cycle: all states get 4s, legs animate in place, 0.4s blends between stages.
 stage=[frames[i%len(frames)] for i in range(240)]
 if allposes:
  a=allposes[-1];b=stage[0]
  for i in range(1,25):
   t=i/24;t=t*t*(3-2*t);allposes.append(blend(a,b,t))
 allposes+=stage
# Loop final->first continuously, one NPC no respawn.
a=allposes[-1];b=allposes[0]
for i in range(1,25):
 t=i/24;t=t*t*(3-2*t);allposes.append(blend(a,b,t))
action=bpy.data.actions.new('RifleDemo_ContinuousV5');rig.animation_data.action=action
for f,pose in enumerate(allposes,1):
 bpy.context.scene.frame_set(f);assign(pose);ground()
 for p in rig.pose.bones:p.keyframe_insert('location',frame=f);p.keyframe_insert('rotation_quaternion',frame=f)
for fc in action.fcurves:
 for k in fc.keyframe_points:k.interpolation='LINEAR'
opt=PsaBuildOptions();opt.animation_data=rig.animation_data;seq=PsaBuildSequence();seq.name='wait_Hand';seq.nla_state.action=action;seq.nla_state.frame_start=1;seq.nla_state.frame_end=len(allposes);seq.fps=60;opt.sequences=[seq];write_psa(build_psa(bpy.context,opt),str(R/'continuous.psa'));bpy.ops.wm.save_as_mainfile(filepath=str(R/'continuous.blend'));(R/'states.json').write_text(json.dumps(outstates,indent=2));(R/'motion-corrections.json').write_text(json.dumps({'states':metrics,'continuous_frames':len(allposes),'stage_seconds':4,'transition_seconds':.4,'npc_respawns_between_states':False},indent=2));print('CONTINUOUS',len(allposes),flush=True)
