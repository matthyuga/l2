"""Continuous stock-client collision boxes following reachable multilayer geodata."""
import pathlib,sys,struct,json,collections,hashlib,subprocess,zlib
D=pathlib.Path(__file__).resolve().parent;BASE=D.parent;ROOT=BASE.parents[1];CLIENT=ROOT.parent/'l2'
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
geo=BASE/'stage/Geodata/24_19.l2j';data=geo.read_bytes();r=Reader(data);cells={};west,north=131072,32768
decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:
   z=r.num('h');vals=[[((z<<1)&0xfff0)|15]]*64
  else:
   assert ty in (1,2);vals=[]
   for _ in range(64):
    n=1 if ty==1 else r.num('B');vals.append([r.num('H') for _ in range(n)])
  for i,vs in enumerate(vals):
   cx,cy=divmod(i,8);gx,gy=bx*8+cx,by*8+cy;x,y=west+gx*16+8,north+gy*16+8
   if not(137000<x<144100 and 54500<y<62800):continue
   out=[(decode(v),v&15) for v in vs if 7500<decode(v)<8850]
   if out:cells[(gx,gy)]=out
seed=json.loads((BASE/'geodata-audit.json').read_text())['spawns']['ct'][0];sc=((seed[0]-west)//16,(seed[1]-north)//16,seed[2]-24);seen={sc};q=collections.deque(seen)
while q:
 x,y,z=q.popleft();n=next(n for h,n in cells[x,y] if h==z)
 for dx,dy,bit in [(1,0,1),(-1,0,2),(0,1,4),(0,-1,8)]:
  if not n&bit:continue
  for nz,_ in cells.get((x+dx,y+dy),[]):
   target=(x+dx,y+dy,nz)
   if -96<=nz-z<=24 and target not in seen:seen.add(target);q.append(target)
assert len(seen)>4000
byz=collections.defaultdict(set)
for x,y,z in seen:byz[z].add((x,y))
rects=[];covered=set()
for z,plane in sorted(byz.items()):
 todo=set(plane)
 while todo:
  x,y=min(todo,key=lambda p:(p[1],p[0]));w=1
  while (x+w,y) in todo and w<64:w+=1
  h=1
  while h<64 and all((xx,y+h) in todo for xx in range(x,x+w)):h+=1
  for yy in range(y,y+h):
   for xx in range(x,x+w):todo.remove((xx,yy));covered.add((xx,yy,z))
  rects.append((x,y,z,w,h))
assert covered==seen
print('NATIVE_FLOOR_PLAN',len(seen),'layers',len(rects),'rectangles',flush=True)
# Original Box02 is an exact 12-triangle rectangular cuboid. No imported mesh or
# generated collision payload is used; only native actor transforms.
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary
vs,ts=MeshLibrary(str(CLIENT/'StaticMeshes')).get('deco01','Box02');assert len(ts)==12
lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];assert abs(lo[0]+hi[0])<.001 and abs(lo[1]+hi[1])<.001
source=BASE/'stage/Maps/24_19.unr';m=Edit(source);assert not any(e['name'].startswith('HGDust2V2Floor') for e in m.exports),'Already staged/installed'
levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');mesh=m.imp('deco01.Box02');cl=m.imp('Engine.StaticMeshActor','Core.Class');newrefs=[];removed=[]
for i,e in enumerate(m.exports):
 if e['name'].startswith('HGDust2NativeArrival'):
  removed.append(i+1);changes={n:m.boolean(n,False) for n in ['bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces']};changes['bHidden']=m.boolean('bHidden',True);m.replace(e,change_props(m,e,changes))
for idx,(gx,gy,z,w,h) in enumerate(rects):
 # A 0.1-unit overlap removes floating-point seams; 4u thickness leaves vertical
 # passages intact. Floor datum matches the project's +43.35 geo calibration.
 sx=(w*16+.1)/(hi[0]-lo[0]);sy=(h*16+.1)/(hi[1]-lo[1]);sz=4/(hi[2]-lo[2]);loc=[west+gx*16+w*8,north+gy*16+h*8,z-43.35-hi[2]*sz]
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',loc)+m.vector('ColLocation',loc)+m.float('DrawScale',1.)+m.vector('DrawScale3D',[sx,sy,sz])
 for name in ['bDynamicActorFilterState','bIgnoredRange','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces','bHidden']:raw+=m.boolean(name,True)
 raw+=m.boolean('bUseCylinderCollision',False)+m.boolean('bSunAffect',False)+m.nametag('Tag','StaticMeshActor')+m.end();frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
 newrefs.append(m.add('HGDust2V2Floor'+str(idx).zfill(5),'Engine.StaticMeshActor',frame+raw,flags=0x2070001))
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;count=r.num('i');assert r.num('i')==count;refs=[r.compact() for _ in range(count)];end=r.p;refs=[i for i in refs if i not in removed]+newrefs
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',len(refs),len(refs))+b''.join(ci(i) for i in refs)+m.b[end:level['offset']+level['size']]);raw=m.save(D/'stage/Maps/24_19.unr')
old=Edit(source);new=Edit(raw);preserved=0
for a,b in zip(old.exports,new.exports):
 if a['name']=='myLevel' or a['name'].startswith('HGDust2NativeArrival'):continue
 assert old.b[a['offset']:a['offset']+a['size']]==new.b[b['offset']:b['offset']+b['size']],a['name'];preserved+=1
for e in new.exports:
 if e['name'].startswith('HGDust2V2Floor'):
  p=new.props(e);assert p['bHidden'] and p['bBlockPlayers'] and p['StaticMesh']=='deco01.Box02'
encoded=D/'client/Maps/24_19.unr';encoded.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([str(ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),'-c','encode','-p','121','-f','24_19.unr','-o',str(encoded),str(raw)],capture_output=True,check=True,timeout=30)
b=encoded.read_bytes();key=sum(map(ord,'24_19.unr'))&255;assert b[28:-20].translate(bytes(x^key for x in range(256)))==raw.read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
(D/'rectangles.json').write_text(json.dumps(rects));(D/'audit.json').write_text(json.dumps(dict(source_map_sha256=sha(source),source_geodata_sha256=sha(geo),reachable_layers=len(seen),floor_actors=len(newrefs),stock_mesh='deco01.Box02',stock_mesh_triangles=len(ts),original_payloads_preserved=preserved,removed_arrival_references=removed,geodata_changed=False,client_physics_verified=False),indent=2));print('STAGED_NATIVE_FLOOR',len(newrefs),'actors',preserved,'prior payloads preserved',flush=True)
