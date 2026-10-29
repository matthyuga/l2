import bpy,struct,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.8
 if texture:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture));m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha']);m.surface_render_method='DITHERED'
 return m
skin=material('Neutral head',(.49,.42,.34));hair=material('Neutral hair',(.18,.13,.08))
def load(path,isface=False,texture_override=None):
 b=path.read_bytes();p=0;c={}
 while p<len(b):
  n,t,s,num=struct.unpack_from('<20s3i',b,p);p+=32;c[n.split(b'\0')[0].decode()]=(s,num,b[p:p+s*num]);p+=s*num
 s,num,data=c['PNTS0000'];verts=list(struct.iter_unpack('<3f',data))
 s,num,data=c['VTXW0000'];wedges=[struct.unpack_from('<HxxffBBxx',data,i*s) for i in range(num)]
 s,num,data=c['FACE0000'];faces=[struct.unpack_from('<3HBBI',data,i*s) for i in range(num)]
 mesh=bpy.data.meshes.new(path.stem);mesh.from_pydata(verts,[],[[wedges[k][0] for k in f[:3]] for f in faces]);mesh.update()
 obj=bpy.data.objects.new(path.stem,mesh);bpy.context.collection.objects.link(obj)
 s,num,data=c['MATT0000']
 for i in range(num):
  name=data[i*s:i*s+64].split(b'\0')[0].decode();tex=next(path.parents[2].rglob(name+'.png'),None)
  if globals().get('USE_CREATOR_TEXTURES') and (name=='material_0' or isface):
   import re
   fallback=re.sub(r'_m(\d{3})_m00_([ab]h)$',r'_m\1_t00_m00_\2',path.stem,flags=re.I) if not isface else path.stem.replace('_f','_t00_f')
   images={p.stem.lower():p for p in (root/'native-creator-textures').rglob('*.png')}
   tex=images.get((fallback+'_ori').lower()) or images.get(fallback.lower()) or tex
  if texture_override and not isface:tex=texture_override
  obj.data.materials.append(material(name,(.49,.42,.34) if isface else (.18,.13,.08),tex) if tex else skin if isface else hair)
 uv=mesh.uv_layers.new()
 for poly,f in zip(mesh.polygons,faces):
  poly.material_index=f[3];poly.use_smooth=True
  for loop,k in zip(poly.loop_indices,f[:3]):uv.data[loop].uv=(wedges[k][1],1-wedges[k][2])
 return obj
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=500;scene.render.resolution_y=560;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='AgX'
for loc,power,size in [((8,-12,52),1700,10),((-9,-5,44),900,9),((2,8,48),1900,8)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,42))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=11
for label in ['native','donor']:
 folder=root/'textured'/label/'Elf/SkeletalMesh'
 objects=[load(folder/'MElf_m000_f.psk',True),load(folder/'MElf_m003_m00_ah.psk')]
 if label=='native':objects.append(load(folder/'MElf_m003_m00_bh.psk'))
 for view,loc in [('frente',(0,-24,42)),('perfil',(24,0,42)),('espalda',(0,24,42))]:
  camera.location=loc;camera.rotation_euler=(Vector((0,0,42))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(root/(label+'-'+view+'.png'));bpy.ops.render.render(write_still=True)
 for o in objects:bpy.data.objects.remove(o,do_unlink=True)
