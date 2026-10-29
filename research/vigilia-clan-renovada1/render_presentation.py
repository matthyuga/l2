import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;R=OUT.parents[1];DEST=R/'mapas editados/vigiliarenovada1'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Vigilia-renovada1.blend'));scene=bpy.context.scene;bpy.data.collections['VIG_13_Escala'].hide_render=True
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
for loc,power,size in [((25,-35,45),24000,25),((-20,20,35),19000,20),((30,20,20),12000,15)]:
 d=bpy.data.lights.new('Estudio','AREA');d.energy=power;d.size=size;o=bpy.data.objects.new('Estudio',d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,10))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camara',bpy.data.cameras.new('Camara'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=1000
for name,loc,target,scale in [('presentacion',(48,-65,38),(0,0,13),62),('puente-renovado',(-1,-12,10),(-7.8,0,5.1),12)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;scene.render.filepath=str(DEST/(name+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
