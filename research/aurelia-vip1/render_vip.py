import bpy, math
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];DELIVERY=ROOT/'mapas editados/aureliavip1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Aurelia-VIP1.blend'))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.10,.13,.17,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.4
for name,loc,power,size in [('Key',(-50,-70,100),160000,65),('Fill',(20,60,75),100000,65),('Rim',(70,-10,80),150000,60)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,15))-o.location).to_track_quat('-Z','Y').to_euler()
def camera(loc,target,lens):
    d=bpy.data.cameras.new('Camera','CAMERA') if False else bpy.data.cameras.new('Camera');d.type='PERSP';d.lens=lens;d.clip_end=1000;o=bpy.data.objects.new('Camera',d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
for name,loc,target,lens in [('presentacion',(-110,-124,111),(0,0,16),48),('terraza-vip',(-64,-63,70),(1,0,18),47)]:
    scene.camera=camera(loc,target,lens);scene.render.filepath=str(DELIVERY/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
