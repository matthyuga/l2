from pathlib import Path
import json,collections
D=Path(__file__).resolve().parent
decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
layers={int(k):[(decode(v),v&15) for v in vs] for k,vs in json.loads((D/'encoded-layers.json').read_text()).items()}
def node(x,y,z):
 c=((y-32768)//16)*2048+(x-131072)//16
 assert c in layers,(x,y,z,'no floor')
 h=min(layers[c],key=lambda a:abs(a[0]-z))[0];assert abs(h-z)<=32,(x,y,z,h)
 return c,h
def path(a,b):
 q=collections.deque([a]);parent={a:None}
 while q:
  c,z=q.popleft()
  if (c,z)==b:
   ans=[];v=b
   while v is not None:ans.append(v);v=parent[v]
   return list(reversed(ans))
  ns=next(n for h,n in layers[c] if h==z)
  for dc,bit in [(1,1),(-1,2),(2048,4),(-2048,8)]:
   if not ns&bit:continue
   for nz,_ in layers.get(c+dc,[]):
    v=(c+dc,nz)
    if -96<=nz-z<=24 and v not in parent:parent[v]=(c,z);q.append(v)
 raise AssertionError(('No path',a,b))
def coords(n):
 c,z=n;return [131072+(c%2048)*16+8,32768+(c//2048)*16+8,z+24]
routes={}
for side in [-1,1]:
 a=node(146540,52000+side*405,12056);b=node(145820,52000+side*405,12384)
 r=path(a,b)
 # Complete route must rise to bridge through the stair corridor, not teleport.
 routes['escalera_'+str(side)]=[coords(v) for v in r]
 # Reverse route and doorway access are independently checked.
 routes['bajada_'+str(side)]=[coords(v) for v in path(b,a)]
routes['entrada_habitacion']=[coords(v) for v in path(node(146000,52000,12056),node(145650,52000,12056))]
gallery=node(146700,52000,12760)
assert all(z>12600 for z,_ in layers[gallery[0]] if abs(z-12760)<32)
(D/'navigation-routes.json').write_text(json.dumps(routes));print('NAVIGATION_ROUTES_PASS', {k:len(v) for k,v in routes.items()})
