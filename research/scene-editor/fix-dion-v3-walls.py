"""Section the perimeter before trimming: no continuous coping over a breach."""
from pathlib import Path
import bpy,bmesh,json,random,math
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R.parent/'model-catalog/exports/dion-hecatombe-v3'
p=json.loads((O/'native-placement.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(O/'source.blend'))
for obj in list(bpy.data.objects):
 if obj.name not in p['walls']:bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update();rng=random.Random(271028);report=[]
for number,name in enumerate(p['walls']):
 src=bpy.data.objects[name];transform=src.matrix_world.copy();mesh=src.data.copy()
 for v in mesh.vertices:v.co=transform@v.co
 points=[v.co for v in mesh.vertices];lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)));span=hi-lo;axis=0 if span.x>span.y else 1;other=1-axis
 severity=[.28,.75,.48,.9,.18,.65,.4][number%7];cells=max(8,min(24,int(span[axis]/1.2)));survived=0
 for j in range(cells):
  t=(j+.5)/cells;breach=math.exp(-((t-.38)/.14)**2)+.75*math.exp(-((t-.76)/.09)**2)
  fraction=max(.06,1-severity*(.3+breach*.9)-.12*rng.random())
  top=lo.z+span.z*fraction;bm=bmesh.new();bm.from_mesh(mesh)
  for value,sign in [(lo[axis]+span[axis]*j/cells,1),(lo[axis]+span[axis]*(j+1)/cells,-1)]:
   point=Vector((0,0,0));point[axis]=value;normal=Vector((0,0,0));normal[axis]=sign
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,clear_inner=True,dist=.00001)
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=Vector((0,0,top)),plane_no=Vector((0,0,-1)),clear_inner=True,dist=.00001)
  if not bm.faces:bm.free();continue
  # Tiny variation on the new top edge; leave foundations in their native place.
  for v in bm.verts:
   if abs(v.co.z-top)<.03:v.co.z+=rng.uniform(-.055,.025)
  m=bpy.data.meshes.new(f'Muro {number+1} sección {j+1}');bm.to_mesh(m);bm.free()
  for mat in mesh.materials:m.materials.append(mat)
  obj=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(obj);survived+=1
 material=next((m for m in mesh.materials if m),None)
 for j in range(int(12+severity*20)):
  point=(lo+hi)/2;point[axis]=lo[axis]+span[axis]*rng.uniform(.1,.9);point[other]+=rng.uniform(-1.3,1.3);point.z=lo.z+.1
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=point);stone=bpy.context.object;stone.name=f'Mampostería caída {number+1}-{j+1}';stone.scale=(rng.uniform(.12,.32),rng.uniform(.12,.3),rng.uniform(.09,.18))
  if material:stone.data.materials.append(material)
 bpy.data.objects.remove(src,do_unlink=True);report.append({'actor':name,'severity':severity,'sections':survived,'continuousCopingRemoved':True})
bpy.ops.export_scene.gltf(filepath=str(O/'damaged-walls.glb'),export_format='GLB',export_animations=False,export_yup=True)
(O/'wall-audit.json').write_text(json.dumps(report,indent=2));print('WALLS FIXED',flush=True)
