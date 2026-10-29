import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Vigilia-renovada1.blend'))
vertices=[];faces=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type!='MESH' or any(c.name=='VIG_13_Escala' for c in o.users_collection):continue
 me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);me.calc_loop_triangles();offset=len(vertices);vertices.extend([o.matrix_world@v.co for v in me.vertices])
 for t in me.loop_triangles:faces.append(tuple(offset+i for i in t.vertices));owners.append(o.name)
bvh=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
LOW=4.15;UP=5.43;R=.12;HEAD=.46;failures=[];stair_samples=[]
def floor(x,y,expected):
 p,n,i,d=bvh.ray_cast(Vector((x,y,expected+.08)),Vector((0,0,-1)),.20)
 if p is None:failures.append({'type':'missing support','x':x,'y':y,'expected':expected});return expected
 if abs(p.z-expected)>.018:failures.append({'type':'support height','x':x,'y':y,'expected':expected,'actual':p.z,'object':owners[i]})
 return p.z
def headroom(x,y,z):
 p,n,i,d=bvh.ray_cast(Vector((x,y,z+.06)),Vector((0,0,1)),.64)
 if p is not None:failures.append({'type':'headroom','x':x,'y':y,'clearance':p.z-z,'object':owners[i]})
for side in [-1,1]:
 for i in range(26):
  x=-4.14-(i+.5)*.16;expected=LOW+(i+1)*(UP-LOW)/26
  for shift in [-.12,0,.12]:
   y=side*2.65+shift;z=floor(x,y,expected);headroom(x,y,z);stair_samples.append({'side':side,'step':i+1,'offset':shift,'height':z})
# Sweeps represent a .24-wide, .46-high comparison envelope in design units.
routes=[('central',[(-8,0,LOW),(11.5,0,LOW)]),('room',[(-8,0,LOW),(-11.1,0,LOW)]),('port stair exit',[(-8.50,-2.65,UP),(-13.1,-2.65,UP),(-13.1,0,UP),(-10.55,0,UP)]),('starboard stair exit',[(-8.50,2.65,UP),(-13.1,2.65,UP),(-13.1,0,UP),(-10.55,0,UP)]),('gallery',[(-2,0,11.2),(6,0,11.2)])]
segments=0
for name,points in routes:
 for aa,bb in zip(points,points[1:]):
  a,b=Vector(aa),Vector(bb);delta=b-a;direction=delta.normalized();perp=Vector((-direction.y,direction.x,0))
  for shift in [-R,0,R]:
   for h in [.09,.26,.45]:
    start=a+perp*shift+Vector((0,0,h));p,n,i,d=bvh.ray_cast(start,direction,delta.length)
    if p is not None:failures.append({'type':'route blocked','route':name,'offset':shift,'height':h,'object':owners[i],'point':list(p)})
    segments+=1
manifest=json.loads((OUT/'design-manifest.json').read_text(encoding='utf-8'))
report={'stairSamples':len(stair_samples),'stairs':stair_samples,'sweptSegments':segments,'referenceHeightL2u':46,'referenceWidthL2u':24,'unchangedFurniture':len(manifest['furniture']),'allFurniturePreserved':all(f['unchanged'] for f in manifest['furniture']),'failures':failures,'passed':not failures}
(OUT/'geometry-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('GEOMETRY_AUDIT',json.dumps({k:v for k,v in report.items() if k!='stairs'}))
if failures:raise RuntimeError('Fix route/support failures before delivery')
