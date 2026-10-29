import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).parent;M=R.parent/'v4-motion';D=R/'contact';D.mkdir(exist_ok=True)
sys.path.insert(0,r'E:\l2-local\research\amber-l2\tools\psk_addon');import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psa.builder import build_psa,PsaBuildOptions,PsaBuildSequence
from io_scene_psk_psa.psa.writer import write_psa
bpy.ops.wm.open_mainfile(filepath=str(M/'Idle_Aiming_FFighter.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');bpy.context.scene.frame_set(1);bpy.context.view_layer.update();rel=rig.pose.bones['Bip01_R_Hand'].matrix.inverted()@rig.pose.bones['Bip01_L_Hand'].matrix
states=json.loads((M/'states.json').read_text());reports=[]
for state in states:
 bpy.ops.wm.open_mainfile(filepath=state['blend']);rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');source=rig.animation_data.action;frames=[];errors=[]
 for f in range(1,state['frames']+1):
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();upper=rig.pose.bones['Bip01_L_UpperArm'];fore=rig.pose.bones['Bip01_L_Forearm'];hand=rig.pose.bones['Bip01_L_Hand'];rh=rig.pose.bones['Bip01_R_Hand'];targetmat=rh.matrix@rel;target=targetmat.translation
  shoulder=upper.head.copy();elbow=fore.head.copy();wrist=hand.head.copy();a=(elbow-shoulder).length;b=(wrist-elbow).length;direction=target-shoulder;distance=direction.length;direction.normalize();reach=max(abs(a-b)+.001,min(distance,a+b-.001));mid=(a*a-b*b+reach*reach)/(2*reach);height=math.sqrt(max(0,a*a-mid*mid));pole=elbow-shoulder;pole-=direction*pole.dot(direction)
  if pole.length<1e-5:pole=Vector((0,1,0))
  pole.normalize();newelbow=shoulder+direction*mid+pole*height
  delta=(elbow-shoulder).normalized().rotation_difference((newelbow-shoulder).normalized());m=(delta@upper.matrix.to_quaternion()).to_matrix().to_4x4();m.translation=shoulder;upper.matrix=m;bpy.context.view_layer.update()
  elbow=fore.head.copy();wrist=hand.head.copy();end=shoulder+direction*reach;delta=(wrist-elbow).normalized().rotation_difference((end-elbow).normalized());m=(delta@fore.matrix.to_quaternion()).to_matrix().to_4x4();m.translation=elbow;fore.matrix=m;bpy.context.view_layer.update()
  targetmat.translation=hand.head;hand.matrix=targetmat;bpy.context.view_layer.update();errors.append((hand.head-target).length);frames.append({p.name:p.matrix_basis.copy() for p in rig.pose.bones})
 action=bpy.data.actions.new(state['state']+'_RifleContact');rig.animation_data.action=action
 for f,pose in enumerate(frames,1):
  bpy.context.scene.frame_set(f)
  for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.matrix_basis=pose[p.name];p.keyframe_insert('location',frame=f);p.keyframe_insert('rotation_quaternion',frame=f)
 for fc in action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 opt=PsaBuildOptions();opt.animation_data=rig.animation_data;seq=PsaBuildSequence();seq.name=state['state'];seq.nla_state.action=action;seq.nla_state.frame_start=1;seq.nla_state.frame_end=state['frames'];seq.fps=state['fps'];opt.sequences=[seq];p=build_psa(bpy.context,opt);out=D/(state['state']+'.psa');write_psa(p,str(out));blend=D/(state['state']+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend));state['psa']=str(out);state['blend']=str(blend);state['hand_contact_max_error']=max(errors);reports.append({'state':state['state'],'max_left_hand_contact_error':max(errors)});print('CONTACT',reports[-1],flush=True)
(R/'states-contact.json').write_text(json.dumps(states,indent=2));(R/'contact-validation.json').write_text(json.dumps(reports,indent=2))
