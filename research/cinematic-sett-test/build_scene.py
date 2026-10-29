import bpy,math,pathlib,json,random
from mathutils import Vector,Quaternion
P=pathlib.Path(r'E:\l2-local\research\cinematic-sett-test')
s=bpy.context.scene
# Retain the imported textured character; replace diagnostic staging.
for o in list(s.objects):
 if o.type in {'LIGHT','CAMERA'}:bpy.data.objects.remove(o,do_unlink=True)
s.frame_set(1);rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data_clear()
for o in s.objects:
 if o.animation_data:o.animation_data_clear()
bpy.ops.object.empty_add();actor=bpy.context.object;actor.name='Sett_Walk_Controller'
for o in list(s.objects):
 if o!=actor and o.parent is None:o.parent=actor
# Procedural two-bone IK gait; original action is retained in the file as an unused action.
feet={}
for side,x in [('l',.13),('r',-.13)]:
 bpy.ops.object.empty_add();target=bpy.context.object;target.name='Foot_Target_'+side;target.parent=actor
 bpy.ops.object.empty_add();pole=bpy.context.object;pole.name='Knee_Pole_'+side;pole.parent=actor;pole.location=(x,-1.3,.65)
 c=rig.pose.bones['bip001_'+side+'_calf'].constraints.new('IK');c.target=target;c.pole_target=pole;c.chain_count=2;c.use_tail=True;c.pole_angle=-math.pi/2
 target.rotation_mode='QUATERNION';target.rotation_quaternion=(rig.matrix_world@rig.pose.bones['bip001_'+side+'_foot'].matrix).to_quaternion()
 rot=rig.pose.bones['bip001_'+side+'_foot'].constraints.new('COPY_ROTATION');rot.target=target;rot.target_space='WORLD';rot.owner_space='WORLD'
 feet[side]=target
# Small secondary motion on the articulated shoulder appendages.
secondary={b.name:b.rotation_quaternion.copy() for b in rig.pose.bones if 'tentacle' in b.name}
for f in range(1,193):
 t=(f-1)/24;phase=t*2*math.pi/1.0
 actor.location=(0,1.8-t*.48,0);actor.keyframe_insert('location',frame=f)
 rig.location.z=.018*(1-math.cos(2*phase));rig.keyframe_insert('location',frame=f)
 for side,x,off in [('l',.13,0),('r',-.13,math.pi)]:
  u=(t+off/(2*math.pi))%1.0;target=feet[side]
  if u<.6: yy=-.144+.48*u;zz=.17
  else: v=(u-.6)/.4;yy=.144-.288*v;zz=.17+.12*math.sin(math.pi*v)
  target.location=(x,yy,zz);target.keyframe_insert('location',frame=f)
 for j,(name,q) in enumerate(secondary.items()):
  b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.rotation_quaternion=q@Quaternion((1,0,0),.022*math.sin(phase*.5+j*.3));b.keyframe_insert('rotation_quaternion',frame=f)
for o in [actor,rig,*feet.values()]:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
# Environment generated entirely in Blender.
def mat(name,col,rough=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Roughness'].default_value=rough;return m
soil=mat('Damp forest ground',(.055,.072,.055));pathmat=mat('Earth path',(.15,.115,.078));bark=mat('Bark',(.055,.038,.028));leaf=mat('Deep teal foliage',(.027,.095,.07));stone=mat('Ancient weathered stone',(.14,.19,.17));moss=mat('Moss',(.075,.13,.055))
def cube(name,loc,scale,material,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bev:mod=o.modifiers.new('Soft worn edges','BEVEL');mod.width=bev;mod.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o
cube('Forest floor',(0,2,-.14),(60,60,.25),soil)
cube('Walking path',(0,1,-.015),(2,35,.025),pathmat)
random.seed(28)
for i in range(44):
 x=random.choice([-1,1])*random.uniform(2.2,11);y=random.uniform(-8,22);h=random.uniform(4,8)
 bpy.ops.mesh.primitive_cone_add(vertices=9,radius1=.18,radius2=.10,depth=h,location=(x,y,h/2));bpy.context.object.data.materials.append(bark)
 for z,r in [(h*.55,1.5),(h*.72,1.15),(h*.88,.8)]:
  bpy.ops.mesh.primitive_cone_add(vertices=9,radius1=r,radius2=.03,depth=h*.42,location=(x,y,z));bpy.context.object.data.materials.append(leaf)
for i in range(65):
 x=random.choice([-1,1])*random.uniform(1.25,7);y=random.uniform(-7,17);r=random.uniform(.1,.45)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=r,location=(x,y,r*.25));o=bpy.context.object;o.scale=(1.3,1,.7);o.data.materials.append(stone if i%3 else moss)
for x in [-1.6,1.6]:
 cube('Ruined gateway pillar',(x,5.5,1.7),(.65,.7,3.4),stone,.07)
 cube('Pillar cap',(x,5.5,3.45),(.9,.95,.2),stone,.05)
cube('Ancient lintel',(0,5.5,3.7),(4,.8,.45),stone,.08)
# Camera travels with the actor while crossing from a wide three-quarter view.
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Cinematic_Tracking_Camera';cam.data.lens=43;s.camera=cam
for f in range(1,193):
 t=(f-1)/191;ay=1.8-(f-1)/24*.48;ang=.48-.95*t;dist=5.7-.6*t
 cam.location=(math.sin(ang)*dist,ay-math.cos(ang)*dist,2.05-.25*t);aim(cam,(0,ay,1.2));cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.095,.13,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for name,loc,power,col,size in [('Warm key',(2,-3,6),1250,(1,.74,.48),5),('Cool rim',(-3,4,5),1800,(.32,.7,1),4),('Front fill',(-3,-4,3),500,(.58,.75,1),4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=col;o.data.size=size;aim(o,(0,0,1))
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.eevee.use_gtao=True;s.eevee.gtao_distance=3;s.eevee.use_soft_shadows=True;s.eevee.use_bloom=True;s.eevee.bloom_intensity=.07
s.view_settings.view_transform='Filmic';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=.6
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=192
s.render.image_settings.file_format='PNG';s.render.filepath=str(P/'preview.png');s.frame_set(48)
bpy.ops.render.render(write_still=True)
s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.audio_codec='NONE';s.render.filepath=str(P/'Sett-cinematic-test.mp4')
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'Sett-cinematic-test.blend'))
(P/'scene-info.json').write_text(json.dumps({'character':'Sett','duration_seconds':8,'fps':24,'frames':192,'resolution':[1280,720],'motion':'Procedural two-bone IK walk, secondary appendage motion; not a verified source walk clip','source':'https://sketchfab.com/3d-models/sett-1496e492791b492a82f498558df0be9d','author':'Vasian-Digital3D','license':'CC BY 4.0'},indent=2))
