"""Multilayer geometry plus original BSP empty-space checks. Preserve existing region."""
import pathlib,sys,json,struct,hashlib,collections,math
D=pathlib.Path(__file__).resolve().parent;ROOT=D.parents[1];SRC=ROOT/'research/dust2'
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Reader
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'))
from geolib.meshes import MeshLibrary,actor_matrix,transform
from geolib.generate import _prep_geometry,_column,_span_layers,_wall_between
build=json.loads((D/'build-audit.json').read_text());lib=MeshLibrary(str(D/'stage/StaticMeshes'));triangles=[];world=[]
for part in build['parts']:
 mesh=lib.get('HGDust2Arena',part);assert mesh,lib.failed
 v,t=mesh;wv=transform(v,actor_matrix(None,build['scale'],[1,1,1]),build['location']);world.extend(wv);triangles.extend(tuple((wv[i][0],wv[i][1],wv[i][2]+43.35) for i in face) for face in t)
bsp=(SRC/'source/de_dust2.bsp').read_bytes();lumps=[struct.unpack_from('<2i',bsp,4+i*8) for i in range(15)]
def lump(i):o,n=lumps[i];return bsp[o:o+n]
planes=list(struct.iter_unpack('<4fi',lump(1)));nodes=list(struct.iter_unpack('<i2h6h2H',lump(5)));leaves=list(struct.iter_unpack('<2i6h2H4B',lump(10)));head=struct.unpack_from('<i',lump(14),36)[0]
def contents(x,y,z):
 ox,oy,oz=build['location'];q=((x-ox)/1.5,(y-oy)/1.5,(z-43.35-oz)/1.5);n=head
 while n>=0:
  nd=nodes[n];p=planes[nd[0]];n=nd[1 if sum(p[i]*q[i] for i in range(3))-p[3]>=0 else 2]
 return leaves[-n-1][0]
west,north=131072,32768;fc,grid,walls,wgrid=_prep_geometry(triangles,west,north);layers={};rejected=0
for cell,idx in grid.items():
 gy,gx=divmod(cell,2048);x,y=west+gx*16+8,north+gy*16+8;floor,ceil=_column(x,y,idx,fc)
 ls=[]
 for z in _span_layers(floor,ceil,[]):
  if contents(x,y,z+24) in (-1,-3,-4,-5):ls.append(z&~7)
  else:rejected+=1
 if ls:layers[cell]=sorted(set(ls),reverse=True)
print('Columns prepared',len(layers),'rejected solid/outside',rejected,flush=True)
encoded={};blocked=0
for cell,ls in layers.items():
 gy,gx=divmod(cell,2048);px,py=west+gx*16+8,north+gy*16+8;out=[]
 for z in ls:
  n=0
  for dx,dy,bit in ((1,0,1),(-1,0,2),(0,1,4),(0,-1,8)):
   nc=(gy+dy)*2048+gx+dx
   if not any(-96<=nz-z<=24 for nz in layers.get(nc,[])):continue
   ids=set(wgrid.get(cell,[]))|set(wgrid.get(nc,[]))
   if ids and _wall_between(px,py,px+dx*16,py+dy*16,z,ids,walls):blocked+=1;continue
   if any(contents(px+dx*f,py+dy*f,z+24)==-2 for f in (4,8,12)):blocked+=1;continue
   n|=bit
  out.append(((z<<1)&0xfff0)|n)
 encoded[cell]=out
def decode(v):return ((v if v<32768 else v-65536)&~15)>>1
entities=json.loads((SRC/'bsp-audit.json').read_text())['entities'];spawns={}
for group,cl in [('ct','info_player_start'),('t','info_player_deathmatch')]:
 spawns[group]=[]
 for e in entities:
  if e.get('classname')!=cl:continue
  src=list(map(float,e['origin'].split()));x,y,z=[round(build['location'][i]+src[i]*1.5) for i in range(3)];cell=((y-north)//16)*2048+(x-west)//16
  vals=encoded.get(cell,[]);assert vals,('Missing spawn',group,src,x,y,z)
  val=min(vals,key=lambda v:abs(decode(v)-(z-54+43.35)));floor=decode(val);assert abs(floor-(z-54+43.35))<80,(group,src,floor,z)
  assert val&15,('Boxed spawn',group,src)
  spawns[group].append([x,y,floor+24])
seed=spawns['ct'][0];cell=((seed[1]-north)//16)*2048+(seed[0]-west)//16;seen={(cell,seed[2]-24)};q=collections.deque(seen)
while q:
 cell,z=q.popleft();gy,gx=divmod(cell,2048);val=min(encoded[cell],key=lambda v:abs(decode(v)-z))
 for dx,dy,bit in ((1,0,1),(-1,0,2),(0,1,4),(0,-1,8)):
  if not val&bit:continue
  nc=(gy+dy)*2048+gx+dx
  for v in encoded.get(nc,[]):
   nz=decode(v)
   if -96<=nz-z<=24 and (nc,nz) not in seen:seen.add((nc,nz));q.append((nc,nz))
for group,ss in spawns.items():
 for s in ss:
  cell=((s[1]-north)//16)*2048+(s[0]-west)//16;assert (cell,s[2]-24) in seen,('Disconnected spawn',group,s)
assert len(seen)>10000
source=ROOT/'server/game/data/geodata/24_19.l2j';b=source.read_bytes();r=Reader(b);result=bytearray();changed=0;oldlayers=0
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
   assert all(abs(decode(a)-decode(c))>256 for a in original for c in new),'Overlapping existing layers'
   values=original+new;assert len(values)<=125;values.sort(key=decode,reverse=True);result.append(len(values));result+=struct.pack('<'+'H'*len(values),*values);oldlayers+=len(original)
assert b[r.p:] in (b'',b'Kuoja');result+=b[r.p:];out=D/'stage/Geodata/24_19.l2j';out.parent.mkdir(exist_ok=True);out.write_bytes(result)
bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
wall_tests=[];layer_tests=[];walk_tests=[]
for cell,z in sorted(seen):
 gy,gx=divmod(cell,2048);x,y=west+gx*16+8,north+gy*16+8;val=min(encoded[cell],key=lambda v:abs(decode(v)-z))
 if len(layer_tests)<5 and len(encoded[cell])>1:layer_tests.append([[x,y,decode(v)] for v in encoded[cell]])
 for dx,dy,bit in ((1,0,1),(0,1,4)):
  nc=(gy+dy)*2048+gx+dx;nvals=encoded.get(nc,[])
  if not nvals:continue
  nz=min((decode(v) for v in nvals),key=lambda v:abs(v-z))
  if abs(nz-z)>16:continue
  if val&bit and len(walk_tests)<8:walk_tests.append([[x,y,z],[x+dx*16,y+dy*16,nz]])
  if not val&bit and len(wall_tests)<8:wall_tests.append([[x,y,z],[x+dx*16,y+dy*16,nz]])
 if len(layer_tests)>=5 and len(wall_tests)>=8 and len(walk_tests)>=8:break
report=dict(source_sha256=hashlib.sha256(b).hexdigest(),new_cells=len(encoded),multilayer_cells=sum(len(v)>1 for v in encoded.values()),changed_blocks=changed,preserved_old_layers=oldlayers,spawns=spawns,reachable_layers=len(seen),triangles=len(triangles),bounds=bounds,rejected_solid_or_outside=rejected,wall_edges_blocked=blocked,wall_tests=wall_tests,walk_tests=walk_tests,layer_tests=layer_tests)
(D/'geodata-audit.json').write_text(json.dumps(report,indent=2));print('DUST2_GEODATA_PASS',len(encoded),'cells',len(seen),'reachable; CT and T connected',flush=True)
