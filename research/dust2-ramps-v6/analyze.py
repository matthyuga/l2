from pathlib import Path
import sys,json,collections,math
D=Path(__file__).resolve().parent;R=D.parents[1];V4=D.parent/'dust2-stairs-v4';V3=D.parent/'dust2-fit-v3'
sys.path.insert(0,str(R/'research/veilmar/geodata-toolkit'));from geolib.meshes import MeshLibrary,actor_matrix,transform
from geolib.generate import _prep_geometry
rects=json.loads((V4/'native-floor/rectangles.json').read_text());floors={(x,y,z):h for gx,gy,z,w,h_,h in rects for y in range(gy,gy+h_) for x in range(gx,gx+w)}
build=json.loads((V3/'build-audit.json').read_text());lib=MeshLibrary(str(R.parent/'l2/StaticMeshes'));triangles=[]
for part in build['parts']:
 v,t=lib.get('HGDust2Arena',part);world=transform(v,actor_matrix(None,build['scale'],build['scale3d']),build['location']);triangles.extend(tuple(world[i] for i in face) for face in t)
fc,grid,_,_=_prep_geometry(triangles,131072,32768)
def flat(x,y,h):
 px,py=131072+x*16+8,32768+y*16+8
 for idx in grid.get(y*2048+x,[]):
  _,ax,ay,az,ux,uy,uz,vx,vy,vz,d00,d01,d11,inv=fc[idx]
  if abs(uz)>.01 or abs(vz)>.01 or abs(az-h)>.6:continue
  dx,dy=px-ax,py-ay;d02=vx*dx+vy*dy;d12=ux*dx+uy*dy;u=(d11*d02-d01*d12)*inv;v=(d00*d12-d01*d02)*inv
  if u>=-.001 and v>=-.001 and u+v<=1.001:return True
 return False
flat_nodes={k for k,h in floors.items() if flat(k[0],k[1],h)};bycell=collections.defaultdict(list)
for x,y,z in flat_nodes:bycell[x,y].append(z)
groups=collections.defaultdict(set)
for x,y,z in sorted(flat_nodes):
 low=floors[x,y,z]
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  for nz in bycell.get((x+dx,y+dy),[]):
   high=floors[x+dx,y+dy,nz];rise=high-low
   # The original walkable stair treads rise 16u. Larger single fronts here
   # also describe crate/platform sides and produce perpendicular false ramps.
   if not 4<=rise<=18:continue
   axis=0 if dx else 1;sign=dx or dy;line=(x+(dx>0)) if dx else (y+(dy>0));along=y if dx else x
   groups[axis,sign,line,low,high].add(along)
risers=[]
for (axis,sign,line,low,high),vals in sorted(groups.items()):
 while vals:
  start=min(vals);end=start+1
  while end in vals:end+=1
  vals.difference_update(range(start,end))
  # Exclude single-cell aliases at corners, not continuous stair fronts.
  if end-start<2:continue
  risers.append(dict(axis=axis,sign=sign,line=(131072 if axis==0 else 32768)+line*16,a=(32768 if axis==0 else 131072)+start*16,b=(32768 if axis==0 else 131072)+end*16,low=low,high=high,steps=1))
# Merge consecutive risers across the same stair width into a continuous plane.
flights=[];todo=list(risers)
while todo:
 f=todo.pop(0);chain=[f];changed=True
 while changed:
  changed=False
  for n in todo:
   last=chain[-1];first=chain[0]
   if n['axis']==f['axis'] and n['sign']==f['sign'] and n['a']==f['a'] and n['b']==f['b'] and abs(n['low']-last['high'])<.1 and 0<(n['line']-last['line'])*f['sign']<=128:
    chain.append(n);todo.remove(n);changed=True;break
   if n['axis']==f['axis'] and n['sign']==f['sign'] and n['a']==f['a'] and n['b']==f['b'] and abs(n['high']-first['low'])<.1 and 0<(first['line']-n['line'])*f['sign']<=128:
    chain.insert(0,n);todo.remove(n);changed=True;break
 f=chain[0]
 high=chain[-1]['high'];end=chain[-1]['line'];run=max(2*(high-f['low']),(end-f['line'])*f['sign']+2*(f['high']-f['low']))
 flights.append(dict(axis=f['axis'],sign=f['sign'],a=f['a'],b=f['b'],start=end-f['sign']*run,end=end,low=f['low'],high=high,steps=len(chain),risers=chain))
(D/'flights.json').write_text(json.dumps(flights,indent=2));(D/'risers.json').write_text(json.dumps(risers,indent=2))
print('Flat floor nodes',len(flat_nodes),'riser fronts',len(risers),'flights',len(flights),'steps histogram',dict(collections.Counter(f['steps'] for f in flights)))
for f in flights:
 if f['axis']==1 and f['a']<=139360<=f['b'] and min(f['start'],f['end'])<56464<max(f['start'],f['end'])+1:print('Captured-stair match',f)
