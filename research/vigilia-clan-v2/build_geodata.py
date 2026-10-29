"""Add only the stationary ship layers, retaining dock and lower Coliseum."""
import pathlib,sys,json,struct,hashlib,collections
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1]
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Reader
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'))
from geolib.meshes import MeshLibrary,actor_matrix,transform
import geolib.generate as gg
gg.BIG_PLANE=20000
from geolib.generate import _prep_geometry,_column,_span_layers,_wall_between
build=json.loads((D/'build-audit.json').read_text());lib=MeshLibrary(str(D/'stage/StaticMeshes'));triangles=[];world=[]
source_triangles=json.loads((D/'navigation-source.json').read_text())
for tri in source_triangles:
 wv=[tuple(p[i]*100+build['location'][i] for i in range(3)) for p in tri];world.extend(wv)
 triangles.append(tuple((p[0],p[1],p[2]+43.35) for p in wv))
west,north=131072,32768;fc,grid,walls,wgrid=_prep_geometry(triangles,west,north);layers={}
for cell,idx in grid.items():
 gy,gx=divmod(cell,2048);floor,ceil=_column(west+gx*16+8,north+gy*16+8,idx,fc);ls=_span_layers(floor,ceil,[])
 if ls:layers[cell]=ls
encoded={}
for cell,ls in layers.items():
 gy,gx=divmod(cell,2048);px,py=west+gx*16+8,north+gy*16+8;out=[]
 for z in ls:
  n=0
  for dx,dy,bit in ((1,0,1),(-1,0,2),(0,1,4),(0,-1,8)):
   nc=(gy+dy)*2048+gx+dx
   if not any(-96<=nz-z<=24 for nz in layers.get(nc,[])):continue
   ids=set(wgrid.get(cell,[]))|set(wgrid.get(nc,[]))
   if ids and _wall_between(px,py,px+dx*16,py+dy*16,z,ids,walls):continue
   n|=bit
  out.append(((z<<1)&0xfff0)|n)
 encoded[cell]=out
source=ROOT/'server/game/data/geodata/24_19.l2j';b=(D/'clean-source.l2j').read_bytes();r=Reader(b);result=bytearray();changed=0;oldlayers=0
for bx in range(256):
 for by in range(256):
  start=r.p;ty=r.num('B')
  if ty==0:
   z=r.num('h');cells=[[((z<<1)&0xfff0)|15] for _ in range(64)]
  else:
   assert ty in (1,2);cells=[]
   for _ in range(64):
    n=1 if ty==1 else r.num('B');assert 1<=n<=125;cells.append([r.num('H') for _ in range(n)])
  additions=[encoded.get((by*8+cy)*2048+bx*8+cx,[]) for cx in range(8) for cy in range(8)]
  if not any(additions):result+=b[start:r.p];continue
  changed+=1;result.append(2)
  for original,new in zip(cells,additions):
   values=original+new;assert len(values)<=125;values.sort(key=lambda x:(x if x<32768 else x-65536)&~15,reverse=True);result.append(len(values));result+=struct.pack('<'+'H'*len(values),*values);oldlayers+=len(original)
assert b[r.p:] in (b'',b'Kuoja');result+=b[r.p:];out=D/'stage/Geodata/24_19.l2j';out.parent.mkdir(exist_ok=True);out.write_bytes(result)
def decode(v):return ((v if v<32768 else v-65536)&~15)>>1
seed=((52000-north)//16)*2048+(146500-west)//16;assert seed in encoded
spawn=min(encoded[seed],key=lambda x:abs(decode(x)-12056));assert abs(decode(spawn)-12056)<40 and spawn&15
seen={(seed,decode(spawn))};q=collections.deque(seen)
while q:
 cell,z=q.popleft();gy,gx=divmod(cell,2048);val=min(encoded[cell],key=lambda v:abs(decode(v)-z))
 for dx,dy,bit in ((1,0,1),(-1,0,2),(0,1,4),(0,-1,8)):
  if not val&bit:continue
  nc=(gy+dy)*2048+gx+dx
  for v in encoded.get(nc,[]):
   nz=decode(v)
   if -96<=nz-z<=24 and (nc,nz) not in seen:seen.add((nc,nz));q.append((nc,nz))
assert len(seen)>100
report=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),clean_source_sha256=hashlib.sha256(b).hexdigest(),new_cells=len(encoded),changed_blocks=changed,preserved_old_layers=oldlayers,spawn=[146500,52000,decode(spawn)+24],spawn_floor=decode(spawn),reachable_layers=len(seen),triangles=len(triangles),bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)])
(D/'encoded-layers.json').write_text(json.dumps(encoded));
(D/'geodata-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
