import pathlib,sys,json,struct,math
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[2];sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Edit
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
rects=json.loads((D/'rectangles.json').read_text());source=MeshLibrary(str(ROOT.parent/'l2/StaticMeshes')).get('deco01','Box02');vs,ts=source;assert len(ts)==12
pkg=Edit(D/'stage/Maps/24_19.unr');actors=[e for e in pkg.exports if e['name'].startswith('HGDust2Floor')];assert len(actors)==len(rects)
covered=set();queries=0
for e,(gx,gy,z,w,h) in zip(actors,rects):
 p=pkg.props(e);wv=transform(vs,actor_matrix(None,p['DrawScale'],p['DrawScale3D']),p['Location']);lo=[min(v[i] for v in wv) for i in range(3)];hi=[max(v[i] for v in wv) for i in range(3)]
 assert abs(hi[2]-(z-43.35))<.002
 assert abs((hi[2]-lo[2])-4)<.002
 assert lo[0]<131072+gx*16 and hi[0]>131072+(gx+w)*16
 assert lo[1]<32768+gy*16 and hi[1]>32768+(gy+h)*16
 for y in range(gy,gy+h):
  for x in range(gx,gx+w):
   assert (x,y,z) not in covered;covered.add((x,y,z));queries+=1
 # Ray-test top triangles at corners and center of each native rectangle.
 for fx,fy in [(0,0),(1,0),(0,1),(1,1),(.5,.5)]:
  x=131072+(gx+fx*w)*16;y=32768+(gy+fy*h)*16;hits=[]
  for face in ts:
   a,b,c=[wv[i] for i in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];nz=u[0]*v[1]-u[1]*v[0]
   if abs(nz)<1e-9:continue
   s=((x-a[0])*v[1]-(y-a[1])*v[0])/nz;t=(u[0]*(y-a[1])-u[1]*(x-a[0]))/nz
   if s>=-1e-7 and t>=-1e-7 and s+t<=1.0000001:hits.append(a[2]+s*u[2]+t*v[2])
  assert hits and abs(max(hits)-hi[2])<.002,(e['name'],fx,fy,hits)
assert len(covered)==61234
audit=json.loads((D.parent/'geodata-audit.json').read_text())
for spawn in audit['spawns']['ct']+audit['spawns']['t']:
 assert ((spawn[0]-131072)//16,(spawn[1]-32768)//16,spawn[2]-24) in covered
report=dict(stock_mesh='deco01.Box02',stock_triangles=12,actors_verified=len(actors),reachable_layer_centers_covered=queries,native_rectangle_ray_queries=len(actors)*5,original_spawns_covered=40,thin_floor_thickness=4,client_physics_verified=False)
(D/'verification.json').write_text(json.dumps(report,indent=2));print('NATIVE_SUPPORT_GEOMETRY_PASS',json.dumps(report))
