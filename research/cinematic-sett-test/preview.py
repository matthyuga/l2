import bpy,math,json,pathlib
from mathutils import Vector
out=pathlib.Path(r'E:\l2-local\research\cinematic-sett-test')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=r'E:\l2-local\research\model-catalog\exports\external-assets-3\ext3_02b86c82826120\model.glb')
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=8
s.render.resolution_x=400;s.render.resolution_y=400;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.16,.22,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.6
s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast'
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4,-7,3));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=4.8;aim(cam,(0,0,1.2));s.camera=cam
for pos,power,size in [((2,-4,6),900,5),((-4,-1,3),650,4),((1,3,4),1000,3)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;aim(o,(0,0,1))
samples=[]
for f in [1,240,480,720,960,1200,1440,1680,1920,2160]:
 s.frame_set(f);s.render.filepath=str(out/('pose-%04d.png'%f));bpy.ops.render.render(write_still=True)
 rig=next(o for o in s.objects if o.type=='ARMATURE');samples.append({'frame':f,'bones':{n:list(rig.matrix_world@rig.pose.bones[n].head) for n in ['bip001_pelvis','bip001_l_foot','bip001_r_foot'] if n in rig.pose.bones}})
(out/'poses.json').write_text(json.dumps(samples,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'inspection.blend'))
