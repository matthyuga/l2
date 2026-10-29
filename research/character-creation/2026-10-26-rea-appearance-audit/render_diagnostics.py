import bpy,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent;AUD=D.parent/'2026-10-26-mega-audit'
exec((AUD/'render_preview.py').read_text().split('scene=bpy.context.scene')[0]);root=AUD;USE_CREATOR_TEXTURES=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=500;scene.render.resolution_y=560;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.world.color=(.1,.1,.1)
lights=[]
for loc,power,size in [((8,-12,10),1700,10),((-9,-5,2),900,9),((2,8,6),1900,8)]:
 bpy.ops.object.light_add(type='AREA');o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;lights.append((o,Vector(loc)))
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
cases=[('DarkElf-G','DarkElf','MDarkElf',D/'exports/NexusAppearanceV1/SkeletalMesh/MDarkElf_Hair2.psk',D/'exports/NexusAppearanceV1/Texture/MDarkElf_Hair2_Color0.png'),('FOrc-J','Orc','FOrc',D/'exports/NexusHairT2V11/SkeletalMesh/FOrc_T2_1.psk',D/'exports/NexusHairT2V11/Texture/FOrc_T2_1_Color0_Tex0.png')]
for tag,pkg,model,hair,texture in cases:
 head=next(f for f in (AUD/'comparison/assets'/pkg/'SkeletalMesh').glob('*.psk') if f.stem.lower()==(model+'_m000_f').lower())
 for alpha in [True,False]:
  objects=[load(head,True),load(hair,texture_override=texture)]
  if not alpha:
   for m in objects[-1].data.materials:
    bs=m.node_tree.nodes.get('Principled BSDF')
    for link in list(bs.inputs['Alpha'].links):m.node_tree.links.remove(link)
    bs.inputs['Alpha'].default_value=1
  coords=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box];lo=Vector(tuple(min(c[i] for c in coords) for i in range(3)));hi=Vector(tuple(max(c[i] for c in coords) for i in range(3)));target=(lo+hi)*.5;camera.data.ortho_scale=max((hi.z-lo.z)*1.25,(hi.x-lo.x)*1.25*560/500,8)
  for o,offset in lights:o.location=target+offset;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
  for view,offset in [('back',(3,24,1)),('side',(24,-4,1))]:
   camera.location=target+Vector(offset);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(D/(tag+'-'+view+('-alpha' if alpha else '-opaque')+'.png'));bpy.ops.render.render(write_still=True)
  for o in objects:bpy.data.objects.remove(o,do_unlink=True)
