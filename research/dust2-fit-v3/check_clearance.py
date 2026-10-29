"""Conservative finite-width/height checks against the actual native wall boxes."""
import pathlib,json,collections,sys
D=pathlib.Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import Reader
rects=json.loads((D/'native-floor/rectangles.json').read_text());floors={(x,y,z):vz for gx,gy,z,w,h,vz in rects for y in range(gy,gy+h) for x in range(gx,gx+w)}
walls=json.loads((D/'native-walls/walls.json').read_text());buckets=collections.defaultdict(list)
radius=10.5;height=70
for axis,line,start,z,h,length in walls:
 if axis==0:lo=[131072+line*16-1,32768+start*16-.1,z-47.35];hi=[lo[0]+2,32768+(start+length)*16+.1,z-43.35+h]
 else:lo=[131072+start*16-.1,32768+line*16-1,z-47.35];hi=[131072+(start+length)*16+.1,lo[1]+2,z-43.35+h]
 for x in range(int((lo[0]-radius-131072)//16),int((hi[0]+radius-131072)//16)+1):
  for y in range(int((lo[1]-radius-32768)//16),int((hi[1]+radius-32768)//16)+1):buckets[x,y].append((lo,hi))
blocked=set()
for key,z in floors.items():
 x,y,_=key;px,py=131072+x*16+8,32768+y*16+8
 for lo,hi in buckets[x,y]:
  if hi[2]<=z+16 or lo[2]>=z+height:continue
  dx=max(lo[0]-px,0,px-hi[0]);dy=max(lo[1]-py,0,py-hi[1])
  if dx*dx+dy*dy<radius*radius:blocked.add(key);break
allowed=set(floors)-blocked;bycell=collections.defaultdict(list)
for x,y,z in allowed:bycell[x,y].append(z)
g=json.loads((D/'geodata-audit.json').read_text());spawns=[((x-131072)//16,(y-32768)//16,z-24) for x,y,z in g['spawns']['ct']+g['spawns']['t']]
seed=spawns[0];assert seed in allowed,('spawn intersects native wall',seed)
seen={seed};q=collections.deque(seen)
while q:
 x,y,z=q.popleft()
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  for nz in bycell.get((x+dx,y+dy),[]):
   key=x+dx,y+dy,nz
   if -96<=nz-z<=16 and key not in seen:seen.add(key);q.append(key)
missing=[s for s in spawns if s not in seen]
report=dict(radius=radius,body_height=height,wall_blocked_centers=len(blocked),clear_centers=len(allowed),connected_clear_centers=len(seen),connected_spawns=40-len(missing),missing=missing,client_physics_verified=False)
(D/'clearance-audit.json').write_text(json.dumps(report,indent=2));print(report)
assert not missing,'Finite-width path missing between CT and T'
