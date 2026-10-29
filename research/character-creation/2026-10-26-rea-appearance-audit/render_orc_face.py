import bpy
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent;AUD=D.parent/'2026-10-26-mega-audit'
exec((AUD/'render_preview.py').read_text().split('scene=bpy.context.scene')[0]);root=AUD
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=500;scene.render.resolution_y=560;scene.render.resolution_percentage=100;scene.world.color=(.15,.15,.15)
lights=[]
for loc,power,size in [((8,-12,10),1700,10),((-9,-5,2),900,9),((2,8,6),1900,8)]:
 bpy.ops.object.light_add(type='AREA');o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;lights.append((o,Vector(loc)))
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
for tag,mesh in [('native-UV',D/'exports/Orc/SkeletalMesh/MOrc_m000_f.psk'),('donor-UV',D/'donor-exports/Orc/SkeletalMesh/MOrc_m001_f.psk')]:
 for face in [3,4,5]:
  tex=D/'exports/NexusAppearanceV1/Texture'/('MOrc_Face'+str(face)+'.png');obj=load(mesh,texture_override=tex);coords=[Vector(c) for c in obj.bound_box];lo=Vector(tuple(min(c[i] for c in coords) for i in range(3)));hi=Vector(tuple(max(c[i] for c in coords) for i in range(3)));target=(lo+hi)*.5;camera.data.ortho_scale=7
  for o,offset in lights:o.location=target+offset;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
  for view,offset in [('front',(0,-24,0)),('side',(17,-20,0))]:
   camera.location=target+Vector(offset);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(D/('Orc-Face'+str(face)+'-'+tag+'-'+view+'.png'));bpy.ops.render.render(write_still=True)
  bpy.data.objects.remove(obj,do_unlink=True)
