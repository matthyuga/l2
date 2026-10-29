import bpy,struct,math,json,re
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
exec((root/'render_preview.py').read_text().split('scene=bpy.context.scene')[0])
USE_CREATOR_TEXTURES=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12
scene.render.resolution_x=300;scene.render.resolution_y=340;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='AgX'
lights=[]
for loc,power,size in [((8,-12,10),1700,10),((-9,-5,2),900,9),((2,8,6),1900,8)]:
 bpy.ops.object.light_add(type='AREA');o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;lights.append((o,Vector(loc)))
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO'
dest=root/'gallery-renders';dest.mkdir(exist_ok=True)
groups=[('Fighter','Humano Fighter'),('Magic','Humano Mystic'),('Elf','Elfo'),('DarkElf','Elfo oscuro'),('Orc','Orco Fighter'),('Shaman','Orco Mystic'),('Dwarf','Enano')]
manifest=[]
def signature(path):
 b=path.read_bytes();p=0;out=[]
 while p<len(b):
  n,t,s,c=struct.unpack_from('<20s3i',b,p);p+=32
  if n.startswith((b'PNTS',b'VTXW',b'FACE')):out.append(b[p:p+s*c])
  p+=s*c
 return out
for pkg,title in groups:
 folder=root/'gallery-assets'/pkg/'SkeletalMesh';files={p.stem.lower():p for p in folder.glob('*.psk')}
 for sex in ['M','F']:
  prefix=sex+pkg;head=files.get((prefix+'_m000_f').lower())
  for style in range(5 if sex=='M' else 7):
   paths=[files.get((prefix+f'_m00{style}_m00_'+part).lower()) for part in ['ah','bh']];paths=[p for p in paths if p]
   if pkg in ['Orc','Shaman'] and style==0:
    paths=[p for p in paths if p.stem.lower().endswith('_bh')]
   if not paths:continue
   if len(paths)==2 and signature(paths[0])==signature(paths[1]):paths=paths[:1]
   objects=([load(head,True)] if head else [])+[load(p) for p in paths]
   coords=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
   lo=Vector(tuple(min(c[i] for c in coords) for i in range(3)));hi=Vector(tuple(max(c[i] for c in coords) for i in range(3)));target=(lo+hi)*.5
   camera.data.ortho_scale=max((hi.z-lo.z)*1.3,(hi.x-lo.x)*1.3*340/300,8)
   for o,offset in lights:o.location=target+offset;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
   outputs=[]
   for view,offset in [('frente',(7,-24,1)),('espalda',(10,24,1))]:
    output=dest/(prefix+'-'+chr(65+style)+'-'+view+'.png');outputs.append(str(output))
    if output.exists() and not (pkg in ['Orc','Shaman'] and style==0):continue
    camera.location=target+Vector(offset);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(output);bpy.ops.render.render(write_still=True)
   manifest.append(dict(group=pkg,title=title,sex=sex,style=chr(65+style),files=outputs,meshes=[p.name for p in paths]))
   for o in objects:bpy.data.objects.remove(o,do_unlink=True)
   print('GALLERY',prefix,style,flush=True)
(root/'gallery-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
