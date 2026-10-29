import bpy,pathlib,json,math
from mathutils import Vector
D=pathlib.Path(r'E:/l2-local/research/airship-integration')
bpy.ops.wm.open_mainfile(filepath=str(D/'HGSkyAirship-baked.blend'),load_ui=False,use_scripts=False)
scene=bpy.context.scene
# Render the source, preserving its materials, with an isolated inspection setup.
for o in list(scene.objects):
    if o.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
meshes=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)/2;radius=(hi-lo).length/2
scene.world=bpy.data.worlds.new('AuditWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.20,.25,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
for offset,power,size in [((1,-1,2),1800,1.4),((-1,-.3,1),1000,1.2),((0,1,1.5),1500,1)]:
    data=bpy.data.lights.new('AuditLight','AREA');data.energy=power*radius*radius/20;data.shape='DISK';data.size=radius*size;obj=bpy.data.objects.new('AuditLight',data);scene.collection.objects.link(obj);obj.location=center+Vector(offset)*radius;obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('AuditCamera',bpy.data.cameras.new('AuditCamera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=radius*2.35;cam.data.clip_end=max(1000,radius*20)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24
scene.render.resolution_x=1100;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
for name,direction in [('baked-preview',(1,-1,.7))]:
    cam.location=center+Vector(direction).normalized()*radius*3;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)

