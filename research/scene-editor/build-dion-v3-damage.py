"""Native missing DE building and uneven damage to Dion perimeter walls."""
from pathlib import Path
import bpy,bmesh,json,math,random,sys,runpy,shutil
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog';OUT=CAT/'exports/dion-hecatombe-v3';OUT.mkdir(parents=True,exist_ok=True)
actors=json.loads((ROOT.parent/'scenario-batches/library_fe488fdfccee/actors.json').read_text())
by={a['actor']:a for a in actors}
de=[a['actor']+'_0' for a in actors if a['StaticMesh'].split('.')[-1].lower()=='dion_nv_de']
roof=[a['actor']+'_0' for a in actors if a['StaticMesh'].split('.')[-1].lower()=='dion_nv_de_top']
assert len(de)==len(roof)==1
walls=[a['actor']+'_0' for a in actors if 'dion_nv_wall' in a['StaticMesh'].lower()]
names=de+roof+walls
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(ROOT.parent/'scenario-batches/library_fe488fdfccee/scene-with-terrain.blend')) as (src,dst):dst.objects=names
for o in dst.objects:bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update()
building=[o for o in dst.objects if o.name in de+roof]
points=[o.matrix_world@Vector(c) for o in building for c in o.bound_box]
lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
center=[(lo.x+hi.x)/2,lo.z,-(lo.y+hi.y)/2]
slim=OUT/'source.blend';bpy.ops.wm.save_as_mainfile(filepath=str(slim))
(OUT/'native-placement.json').write_text(json.dumps({'building':de+roof,'center':center,'walls':walls},indent=2))
if not (OUT/'damaged-walls.glb').exists():
 rng=random.Random(261027)
 for o in building:bpy.data.objects.remove(o,do_unlink=True)
 report=[]
 for number,name in enumerate(walls):
  obj=bpy.data.objects[name];obj.data=obj.data.copy()
  # Native geometry to world-space, preserving UVs and avoiding scale-dependent cuts.
  transform=obj.matrix_world.copy()
  for v in obj.data.vertices:v.co=transform@v.co
  obj.matrix_world.identity()
  points=[v.co.copy() for v in obj.data.vertices];low=Vector(tuple(min(v[i] for v in points) for i in range(3)));high=Vector(tuple(max(v[i] for v in points) for i in range(3)))
  span=high-low;axis=0 if span.x>span.y else 1;other=1-axis
  severity=[.28,.75,.48,.9,.18,.65,.4][number%7]
  # Upper cuts and two uneven breaches, with severity varying by wall segment.
  cuts=1 if severity<.4 else 2 if severity<.8 else 3
  for j in range(cuts):
   p=(low+high)/2;p[axis]=low[axis]+span[axis]*(j+1)/(cuts+1)
   p.z=low.z+span.z*(1.04-severity*.45)
   radius=max(.45,span.z*(.30+severity*.40))
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=radius,location=p)
   cutter=bpy.context.object;cutter.scale[other]=max(1.6,span[other]/radius+1)
   cutter.scale[axis]=1.15 if severity>.65 else .9
   for v in cutter.data.vertices:v.co*=rng.uniform(.9,1.1)
   bpy.context.view_layer.objects.active=obj
   modifier=obj.modifiers.new('Brecha irregular','BOOLEAN');modifier.object=cutter;modifier.operation='DIFFERENCE';modifier.solver='EXACT'
   bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
  # Add broken masonry from each breach at the foot of the wall.
  material=next((m for m in obj.data.materials if m),None)
  for j in range(int(8+severity*18)):
   along=low[axis]+span[axis]*rng.uniform(.12,.88);p=(low+high)/2;p[axis]=along;p[other]+=rng.uniform(-1.4,1.4);p.z=low.z+.13
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=p)
   stone=bpy.context.object;stone.name=f'Piedra caída muro {number+1} · {j+1}'
   stone.scale=(rng.uniform(.12,.36),rng.uniform(.12,.32),rng.uniform(.1,.22));stone.rotation_euler.z=rng.random()*math.tau
   if material:stone.data.materials.append(material)
  obj.name=f'Muro {number+1} · daño {round(severity*100)}%'
  report.append({'actor':name,'severity':severity,'cuts':cuts})
 bpy.ops.export_scene.gltf(filepath=str(OUT/'damaged-walls.glb'),export_format='GLB',export_animations=False,export_yup=True)
 (OUT/'wall-audit.json').write_text(json.dumps(report,indent=2))
raw=CAT/'exports/dion-de-v3-raw'
if not (raw/'ruins.glb').exists():
 sys.argv=['blender','--','--source',str(slim),'--output','dion-de-v3-raw','--actors',de[0],roof[0],'--static']
 runpy.run_path(str(ROOT/'build-dion-collapse.py'),run_name='__main__')
staging=OUT/'raw';staging.mkdir(exist_ok=True)
if not (staging/'house11.glb').exists():shutil.copy2(raw/'ruins.glb',staging/'house11.glb')
if not (OUT/'house11.glb').exists():
 sys.argv=['blender','--','--source-dir',str(staging),'--output','dion-hecatombe-v3','--houses','11']
 runpy.run_path(str(ROOT/'build-dion-rubble-v2.py'),run_name='__main__')
print('V3 DAMAGE COMPLETE',flush=True)
