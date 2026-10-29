import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).parent
prefix='Dust2_BombWork_FFighter' if '--hands' in sys.argv else 'StudioSquat_FFighter'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/(prefix+'.blend')))
s=bpy.context.scene
for obj in bpy.data.objects:
 if obj.type=='MESH':
  mat=bpy.data.materials.new('QA clay '+obj.name);mat.diffuse_color=(.28,.47,.61,1);mat.use_nodes=True
  mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.28,.47,.61,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7
  obj.data.materials.clear();obj.data.materials.append(mat)
  for poly in obj.data.polygons:poly.material_index=0;poly.use_smooth=True
bpy.ops.mesh.primitive_plane_add(size=160,location=(0,0,-.25));floor=bpy.context.object
m=bpy.data.materials.new('Floor');m.diffuse_color=(.09,.11,.14,1);floor.data.materials.append(m)
bpy.ops.object.camera_add(location=(72,-105,60));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,21))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=60;s.camera=cam
for loc,power,size in [((30,-50,85),110000,50),((-45,-10,40),65000,40),((0,40,60),90000,40)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,20))-l.location).to_track_quat('-Z','Y').to_euler()
s.world=bpy.data.worlds.new('QA World');s.world.color=(.16,.16,.16);s.render.engine='BLENDER_EEVEE';s.eevee.use_gtao=True;s.eevee.gtao_distance=3;s.eevee.gtao_factor=1.2
s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast'
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');stats=[]
for f in range(1,s.frame_end+1):
 s.frame_set(f);stats.append({'frame':f,'hip':list(rig.pose.bones['Bip01_Pelvis'].head),'foot_l':list(rig.pose.bones['bip01_l_foot'].head),'foot_r':list(rig.pose.bones['bip01_r_foot'].head)})
low=min(stats,key=lambda x:x['hip'][2]);high=max(stats,key=lambda x:x['hip'][2])
for label,f in [('first',1),('low',low['frame']),('high',high['frame'])]:
 s.frame_set(f);s.render.filepath=str(ROOT/f'{prefix}-preview-{label}.png');bpy.ops.render.render(write_still=True)
(ROOT/(prefix+'-pose-metrics.json')).write_text(json.dumps({'frames':stats,'lowest':low,'highest':high},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(prefix+'-QA.blend')))

