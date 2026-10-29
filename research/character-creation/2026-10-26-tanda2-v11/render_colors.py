import bpy,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent;AUD=D.parent/'2026-10-26-mega-audit'
exec((AUD/'render_preview.py').read_text().split('scene=bpy.context.scene')[0]);root=AUD;USE_CREATOR_TEXTURES=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.render.resolution_x=300;scene.render.resolution_y=340;scene.render.resolution_percentage=100;scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='AgX'
lights=[]
for loc,power,size in [((8,-12,10),1700,10),((-9,-5,2),900,9),((2,8,6),1900,8)]:
 bpy.ops.object.light_add(type='AREA');o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;lights.append((o,Vector(loc)))
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';dest=D/'color-previews';dest.mkdir(exist_ok=True)
for item in json.loads((D/'assets-manifest.json').read_text())['items']:
 model=item['model'];mesh=item['mesh'].split('.')[-1];pkg=dict(MElf='Elf',MDarkElf='DarkElf',MOrc='Orc',FOrc='Orc',MShaman='Shaman',FDwarf='Dwarf')[model]
 folder=AUD/'comparison/assets'/pkg/'SkeletalMesh';head=next(f for f in folder.glob('*.psk') if f.stem.lower()==(model+'_m000_f').lower())
 for color in range(4):
  tex=D/'export-check/NexusHairT2V11/Texture'/(item['color_textures'][color][0]+'.png');objects=[load(head,True),load(D/'export-check/NexusHairT2V11/SkeletalMesh'/(mesh+'.psk'),texture_override=tex)]
  coords=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box];lo=Vector(tuple(min(c[i] for c in coords) for i in range(3)));hi=Vector(tuple(max(c[i] for c in coords) for i in range(3)));target=(lo+hi)*.5;camera.data.ortho_scale=max((hi.z-lo.z)*1.3,(hi.x-lo.x)*1.3*340/300,8)
  for o,offset in lights:o.location=target+offset;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
  camera.location=target+Vector((7,-24,1));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(dest/(model+'-'+item['letter']+'-'+str(color)+'.png'));bpy.ops.render.render(write_still=True)
  for o in objects:bpy.data.objects.remove(o,do_unlink=True)
