import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;states=json.loads((R/'states.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R.parent/'v4-textures/RifleNPCV4.blend'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');s=bpy.context.scene
bpy.ops.mesh.primitive_plane_add(size=180,location=(0,0,-.3));floor=bpy.context.object;m=bpy.data.materials.new('Floor');m.diffuse_color=(.12,.13,.16,1);floor.data.materials.append(m)
bpy.ops.object.camera_add(location=(-50,-85,50));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,22))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=60;s.camera=cam
for loc,power in [((30,-50,85),100000),((-45,-10,40),50000),((0,40,60),65000)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.size=50;l.rotation_euler=(Vector((0,0,20))-l.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='BLENDER_EEVEE';s.eevee.use_gtao=True;s.world=bpy.data.worlds.new('World');s.world.color=(.16,.16,.16);s.render.resolution_x=500;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard'
for state in states:
 with bpy.data.libraries.load(state['blend'],link=False) as (src,dst):dst.actions=src.actions
 action=dst.actions[0];rig.animation_data.action=action;s.frame_set(max(1,round(state['frames']*.35)));s.render.filepath=str(R/(state['state']+'.png'));bpy.ops.render.render(write_still=True)
print('PREVIEWS6_DONE')
