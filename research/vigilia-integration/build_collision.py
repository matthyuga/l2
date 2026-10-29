"""Stock L2 colliders covering reachable layers and closed navigation edges."""
from pathlib import Path
import sys,json,collections,struct
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import *
decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
raw=json.loads((D/'encoded-layers.json').read_text());layers={int(i):[(decode(v),v&15) for v in vs] for i,vs in raw.items()}
W,N=131072,32768
spawns={'cubierta':[146500,52000,12056],'proa':[147400,52000,12056]}
seen=set();resolved={};components={}
for name,(x,y,z) in spawns.items():
 cell=((y-N)//16)*2048+(x-W)//16
 assert cell in layers,('Missing spawn cell',name)
 h=min(layers[cell],key=lambda v:abs(v[0]-z))[0];assert abs(h-z)<60,(name,h,z)
 resolved[name]=[x,y,h+24];start=(cell,h);found={start};q=collections.deque(found)
 while q:
  c,z=q.popleft();gx=c%2048;gy=c//2048;ns=next(n for h,n in layers[c] if h==z)
  for dx,dy,bit in [(1,0,1),(-1,0,2),(0,1,4),(0,-1,8)]:
   if ns&bit:
    nc=(gy+dy)*2048+gx+dx
    for nz,_ in layers.get(nc,[]):
     if -96<=nz-z<=24 and (nc,nz) not in found:found.add((nc,nz));q.append((nc,nz))
 seen.update(found);components[name]=len(found)
 assert len(found)>100,(name,'spawn boxed in')
print('REACHABLE',len(seen),components,flush=True)
planes=collections.defaultdict(set)
for c,z in seen:planes[z].add((c%2048,c//2048))
rects=[]
for z,plane in sorted(planes.items()):
 todo=set(plane)
 while todo:
  x,y=min(todo,key=lambda p:(p[1],p[0]));w=1
  while w<64 and (x+w,y) in todo:w+=1
  h=1
  while h<64 and all((xx,y+h) in todo for xx in range(x,x+w)):h+=1
  todo.difference_update((xx,yy) for yy in range(y,y+h) for xx in range(x,x+w))
  rects.append((x,y,z,w,h))
edges={};open_heights=collections.defaultdict(set);open_count=0;drops=0
for c,z in sorted(seen):
 x,y=c%2048,c//2048;nswe=next(n for h,n in layers[c] if h==z)
 for dx,dy,bit,rev in [(1,0,1,2),(-1,0,2,1),(0,1,4,8),(0,-1,8,4)]:
  nc=(y+dy)*2048+x+dx;ns=layers.get(nc,[])
  xy=(0,x+(dx>0),y) if dx else (1,y+(dy>0),x)
  if nswe&bit:open_heights[xy].add(z);open_count+=1;continue
  if any(-24<=nz-z<=96 and nn&rev and (nc,nz) in seen for nz,nn in ns):drops+=1;continue
  above=[h-z-8 for h,_ in layers[c] if h-z>=100];height=min([256]+above)
  edges[(*xy,z)]=min(edges.get((*xy,z),99999),height)
aliases=0
for key,height in list(edges.items()):
 axis,ln,along,z=key;hs=open_heights.get((axis,ln,along),set())
 if any(abs(h-z)<=96 for h in hs):del edges[key];aliases+=1;continue
 caps=[h-z-8 for h in hs if h>z+96]
 if caps:edges[key]=min([height]+caps)
seg=collections.defaultdict(set)
for (axis,ln,a,z),height in edges.items():seg[axis,ln,z,height].add(a)
walls=[]
for (axis,ln,z,h),aa in sorted(seg.items()):
 todo=set(aa)
 while todo:
  a=min(todo);l=1
  while l<64 and a+l in todo:l+=1
  todo.difference_update(range(a,a+l));walls.append((axis,ln,a,z,h,l))
print('COLLISION_PLAN',len(rects),'floors',len(walls),'walls',flush=True)
sys.path.insert(0,str(ROOT/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary
v,t=MeshLibrary(str(ROOT.parent/'l2/StaticMeshes')).get('deco01','Box02');assert len(t)==12
lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
m=Edit(D/'stage/Maps/24_19.unr');assert not any(e['name'].startswith('HGVigiliaFloor') for e in m.exports)
levelref=next(i+1 for i,e in enumerate(m.exports) if e['name']=='LevelInfo0');mesh=m.imp('deco01.Box02');cl=m.imp('Engine.StaticMeshActor','Core.Class');refs=[];boxes=[]
def actor(name,center,size):
 scale=[size[i]/(hi[i]-lo[i]) for i in range(3)];loc=[center[i]-(hi[i]+lo[i])/2*scale[i] for i in range(3)]
 raw=m.obj('StaticMesh',mesh)+m.obj('Level',levelref)+m.vector('Location',loc)+m.vector('ColLocation',loc)+m.float('DrawScale',1)+m.vector('DrawScale3D',scale)
 for n in ['bDynamicActorFilterState','bIgnoredRange','bWorldGeometry','bStatic','bCollideActors','bBlockActors','bBlockPlayers','bBlockZeroExtentTraces','bBlockNonZeroExtentTraces','bHidden']:raw+=m.boolean(n,True)
 raw+=m.boolean('bUseCylinderCollision',False)+m.boolean('bSunAffect',False)+m.nametag('Tag','StaticMeshActor')+m.end();frame=ci(cl)*2+struct.pack('<Qi',0xffffffffffffffff,0)+ci(-1)
 refs.append(m.add(name,'Engine.StaticMeshActor',frame+raw,flags=0x2070001));boxes.append(dict(name=name,center=center,size=size))
for i,(x,y,z,w,h) in enumerate(rects):actor('HGVigiliaFloor'+str(i).zfill(5),[W+x*16+w*8,N+y*16+h*8,z-43.35-2],[w*16+.1,h*16+.1,4])
for i,(axis,ln,a,z,h,l) in enumerate(walls):
 center=[W+ln*16,N+(a+l/2)*16] if axis==0 else [W+(a+l/2)*16,N+ln*16]
 size=[2,l*16+.2,h+4] if axis==0 else [l*16+.2,2,h+4]
 actor('HGVigiliaWall'+str(i).zfill(5),center+[z-43.35-4+size[2]/2],size)
level=next(e for e in m.exports if e['name']=='myLevel');m.props(level);r=Reader(m.b,m.last_props_end);n=r.num('i');assert r.num('i')==n
for _ in range(n):r.compact()
start=r.p;cnt=r.num('i');assert r.num('i')==cnt;oldrefs=[r.compact() for _ in range(cnt)];end=r.p
m.replace(level,m.b[level['offset']:start]+struct.pack('<2i',cnt+len(refs),cnt+len(refs))+b''.join(ci(i) for i in oldrefs+refs)+m.b[end:level['offset']+level['size']]);m.save(D/'stage/Maps/24_19.unr')
audit=dict(reachable_layers=len(seen),components=components,spawns=resolved,native_floor_actors=len(rects),native_wall_actors=len(walls),closed_edges=len(edges),open_directed_edges=open_count,directed_drops=drops,aliases_omitted=aliases)
(D/'collision-audit.json').write_text(json.dumps(audit,indent=2));(D/'rectangles.json').write_text(json.dumps(rects));(D/'walls.json').write_text(json.dumps(walls));(D/'collision-boxes.json').write_text(json.dumps(boxes))
(D/'reachable.json').write_text(json.dumps(sorted(seen)));print(json.dumps(audit,indent=2))
