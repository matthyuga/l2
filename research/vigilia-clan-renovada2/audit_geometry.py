import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Vigilia-renovada2.blend'))
vertices=[];faces=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type!='MESH' or any(c.name=='VIG_13_Escala' for c in o.users_collection):continue
 me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);me.calc_loop_triangles();offset=len(vertices);vertices.extend(o.matrix_world@v.co for v in me.vertices)
 for t in me.loop_triangles:faces.append(tuple(offset+i for i in t.vertices));owners.append(o.name)
bvh=BVHTree.FromPolygons(vertices,faces,all_triangles=True);failures=[];samples=[]
def support(x,y,z,tolerance=.02):
 p,n,i,d=bvh.ray_cast(Vector((x,y,z+.07)),Vector((0,0,-1)),.16)
 if p is None or abs(p.z-z)>tolerance:failures.append({'type':'support','point':[x,y,z],'hit':None if p is None else list(p),'object':None if i is None else owners[i]});return z
 return p.z
def clearance(x,y,z):
 p,n,i,d=bvh.ray_cast(Vector((x,y,z+.06)),Vector((0,0,1)),.54)
 if p is not None:failures.append({'type':'headroom','point':[x,y,z],'object':owners[i],'height':p.z-z})
for i in range(21):
 y=-1.37+(i+.5)*.13;z=5.43+(i+1)*1.01/21
 for dx in [-.12,0,.12]:
  x=-13+dx;actual=support(x,y,z);clearance(x,y,actual);samples.append([x,y,actual])
for x,y in [(-13,-1.54),(-13,1.57),(-12.70,1.57),(-12.45,1.57),(-12.20,1.57),(-11.5,1.0),(-10.0,.3)]:
 z=5.43 if y<-1.4 else 6.44;actual=support(x,y,z,.04);clearance(x,y,actual)
routes=[]
for side in [-1,1]:
 routes.append(('lateral '+str(side),[(-8.5,side*2.65,5.43),(-11.8,side*2.65,5.43),(-11.8,side*.6,5.43),(-10.65,side*.6,5.43)]))
routes.append(('approach roof stair',[(-11.8,-2.65,5.43),(-13,-2.65,5.43),(-13,-1.57,5.43)]))
routes.append(('roof landing',[(-13,1.57,6.44),(-12.15,1.57,6.44),(-12.15,.8,6.44),(-10.6,.8,6.44)]))
segments=0
for name,points in routes:
 for aa,bb in zip(points,points[1:]):
  a,b=Vector(aa),Vector(bb);direction=(b-a).normalized();perp=Vector((-direction.y,direction.x,0))
  for shift in [-.12,0,.12]:
   for h in [.08,.26,.45]:
    p,n,i,d=bvh.ray_cast(a+perp*shift+Vector((0,0,h)),direction,(b-a).length)
    if p is not None:failures.append({'type':'route blocked','route':name,'object':owners[i],'point':list(p),'offset':shift,'height':h})
    segments+=1
manifest=json.loads((OUT/'design-manifest.json').read_text(encoding='utf-8'))
# Confirm that each anchor sits on the original envelope mesh, not in empty air.
envelope=next(o for o in bpy.data.objects if o.name.startswith('Globo_carmesi_panelado'));me=bpy.data.meshes.new_from_object(envelope.evaluated_get(deps),depsgraph=deps);me.calc_loop_triangles();ev=[envelope.matrix_world@v.co for v in me.vertices];ef=[tuple(t.vertices) for t in me.loop_triangles];ebvh=BVHTree.FromPolygons(ev,ef,all_triangles=True);anchor_errors=[]
for a in manifest['suspensionAnchors']:
 p,n,i,d=ebvh.find_nearest(Vector(a['top']));anchor_errors.append(d)
 if d>.06:failures.append({'type':'anchor gap','top':a['top'],'distance':d})
report={'passed':not failures,'roofStairSamples':len(samples),'sweptRouteSegments':segments,'referenceHeightL2u':46,'referenceWidthL2u':24,'envelopeAnchors':len(anchor_errors),'maxAnchorGapDesignUnits':max(anchor_errors),'failures':failures}
(OUT/'geometry-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('REV2_AUDIT',json.dumps(report))
if failures:raise RuntimeError('Resolve geometry audit failures')
