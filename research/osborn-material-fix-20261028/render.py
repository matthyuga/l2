import bpy,pathlib,math
from mathutils import Vector
result={}
gltf=pathlib.Path(r"E:\l2-local\research\model-catalog\exports\LineageNpcs\SkeletalMesh\e_patriarch_MOrc_m00.gltf")
thumb=pathlib.Path(r"E:\l2-local\research\model-catalog\thumbs\m0527.png")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(gltf))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
bpy.context.view_layer.update()
points=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
if not all(math.isfinite(v) for v in (*lo,*hi)):raise ValueError('Non-finite bounds')
center=(lo+hi)/2;scale=max(max(hi-lo),.01)
result['bounds_blender']=[list(lo),list(hi)]
bpy.ops.object.camera_add(location=center+Vector((1,-2.8,.65)).normalized()*scale*3)
cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO'
rot=cam.rotation_euler.to_matrix().transposed();ps=[rot@(p-center) for p in points]
cam.data.ortho_scale=max(max(p.y for p in ps)-min(p.y for p in ps),(max(p.x for p in ps)-min(p.x for p in ps))*420/384,.02)*1.16
cam.data.clip_start=max(scale*.0001,.00001);cam.data.clip_end=scale*30
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=True
scene.world=bpy.data.worlds.new('External asset studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.22,.27,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
for direction,energy in [((1,-3,4),450),((-3,-1,2),260),((1,3,3),380)]:
    bpy.ops.object.light_add(type='AREA',location=center+Vector(direction)*scale)
    light=bpy.context.object;light.data.energy=energy*scale*scale;light.data.shape='DISK';light.data.size=scale*3;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.view_transform='Standard';scene.render.resolution_x=384;scene.render.resolution_y=420;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(thumb)
bpy.ops.render.render(write_still=True)
