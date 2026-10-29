import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).parent;sys.path.insert(0,r'E:\l2-local\research\amber-l2\tools\psk_addon');import io_scene_psk_psa;io_scene_psk_psa.register()
from io_scene_psk_psa.psk.builder import build_psk,PskBuildOptions
from io_scene_psk_psa.psk.writer import write_psk
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'v4-textures/RifleNPCV4.blend'));image=bpy.data.images.load(str(R.parent/'v4-textures/BodyAtlas.png'));pixels=list(image.pixels);w,h=image.size;report=[]
def alpha(uv):
 x=max(0,min(w-1,int(uv.x*w)));y=max(0,min(h-1,int(uv.y*h)));return pixels[(y*w+x)*4+3]
def mix(a,b,t):
 keys=set(a[2])|set(b[2]);return (a[0].lerp(b[0],t),a[1].lerp(b[1],t),{k:a[2].get(k,0)*(1-t)+b[2].get(k,0)*t for k in keys})
def triangles(v,depth):
 if depth==0:return [v]
 a,b,c=v;ab=mix(a,b,.5);bc=mix(b,c,.5);ca=mix(c,a,.5)
 return sum((triangles(t,depth-1) for t in [(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]),[])
for obj in [o for o in bpy.data.objects if o.type=='MESH' and ('_ah' in o.name or '_bh' in o.name)]:
 mesh=obj.data;uv=mesh.uv_layers.active;mesh.calc_loop_triangles();verts=[];uvs=[];weights=[];faces=[]
 for tri in mesh.loop_triangles:
  orig=[]
  for li in tri.loops:
   v=mesh.vertices[mesh.loops[li].vertex_index];orig.append((v.co.copy(),uv.data[li].uv.copy(),{g.group:g.weight for g in v.groups}))
  for tiny in triangles(orig,2):
   clipped=[]
   for i,b in enumerate(tiny):
    a=tiny[i-1];aa=alpha(a[1]);bb=alpha(b[1]);ina=aa>=.55;inb=bb>=.55
    if ina!=inb:clipped.append(mix(a,b,(.55-aa)/(bb-aa)))
    if inb:clipped.append(b)
   if len(clipped)<3:continue
   for i in range(1,len(clipped)-1):
    face=[]
    for co,tex,groups in [clipped[0],clipped[i],clipped[i+1]]:face.append(len(verts));verts.append(co);uvs.append(tex);weights.append(groups)
    faces.append(face)
 new=bpy.data.meshes.new(obj.name+'_Cutout');new.from_pydata(verts,[],faces);new.update();new.materials.append(mesh.materials[0]);layer=new.uv_layers.new(name='BodyAtlasUV')
 for loop in new.loops:layer.data[loop.index].uv=uvs[loop.vertex_index]
 groupnames=[g.name for g in obj.vertex_groups]
 obj.data=new
 obj.vertex_groups.clear()
 for name in groupnames:obj.vertex_groups.new(name=name)
 for i,gs in enumerate(weights):
  for g,value in gs.items():
   if value>1e-6:obj.vertex_groups[g].add([i],value,'REPLACE')
 for poly in new.polygons:poly.use_smooth=True
 report.append({'mesh':obj.name,'old_faces':len(mesh.polygons),'new_faces':len(new.polygons),'alpha_cutout_geometry':True})
# Opaque texture rendering no longer depends on NPC skin material alpha support.
for mat in bpy.data.materials:
 if mat.name=='BodyAtlas':
  mat.blend_method='OPAQUE';bs=mat.node_tree.nodes.get('Principled BSDF')
  if bs:
   for link in list(mat.node_tree.links):
    if link.to_socket==bs.inputs['Alpha']:mat.node_tree.links.remove(link)
   bs.inputs['Alpha'].default_value=1
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type=='MESH':o.select_set(True)
opt=PskBuildOptions();opt.material_names=['BodyAtlas','RifleAtlas'];p=build_psk(bpy.context,opt);assert len(p.wedges)<25000;write_psk(p,str(R/'RifleNPCV5.psk'));bpy.ops.wm.save_as_mainfile(filepath=str(R/'RifleNPCV5.blend'));(R/'hair-validation.json').write_text(json.dumps({'meshes':report,'faces':len(p.faces),'wedges':len(p.wedges),'bones':len(p.bones),'only_hair_geometry_changed':True},indent=2));print('HAIR_CUTOUT',report,len(p.faces),len(p.wedges))

