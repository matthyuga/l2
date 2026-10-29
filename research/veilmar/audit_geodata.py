"""Inspect generated L2J floors and connected directions around the author's entries."""
import pathlib,struct,json,collections
import numpy as np
D=pathlib.Path(__file__).resolve().parent
p=D/'generated-geodata/17_24.l2j'
b=p.read_bytes();offset=0;blocks={};types=collections.Counter()
for bx in range(256):
 for by in range(256):
  ty=b[offset];offset+=1;types[ty]+=1;cells=[]
  if ty==0:
   z=struct.unpack_from('<h',b,offset)[0];offset+=2;cells=[[(z,15)]]*64
  elif ty in (1,2):
   for i in range(64):
    n=1 if ty==1 else b[offset]
    if ty==2:offset+=1
    assert 1<=n<=125
    vals=struct.unpack_from('<'+'h'*n,b,offset);offset+=2*n
    cells.append([((v&~15)>>1,v&15) for v in vals])
  else:raise AssertionError(ty)
  blocks[bx,by]=cells
assert offset==len(b)
def cell(x,y,z):
 gx=(x+98304)//16;gy=(y-196608)//16
 vals=blocks[gx//8,gy//8][(gx%8)*8+gy%8]
 return min(vals,key=lambda v:abs(v[0]-z))
def walk(x,y,z):
 seen={(x//16,y//16)};q=collections.deque([(x//16,y//16,z)])
 while q:
  cx,cy,cz=q.popleft();h,nswe=cell(cx*16+8,cy*16+8,cz)
  for dx,dy,bit in ((1,0,1),(-1,0,2),(0,1,4),(0,-1,8)):
   nx,ny=cx+dx,cy+dy
   if (nx,ny) in seen or abs(nx*16-x)>1000 or abs(ny*16-y)>1000:continue
   nh,nn=cell(nx*16+8,ny*16+8,h)
   if nswe&bit and abs(nh-h)<=40:
    seen.add((nx,ny));q.append((nx,ny,nh))
 return len(seen)
results=[]
for x,y,z in ((-78552,212264,-2592),(-86840,201512,-7664),(-93640,211000,-7952)):
 h,n=cell(x,y,z)
 r=dict(x=x,y=y,author_z=z,floor=h,nswe=n,connected_cells_1000=walk(x,y,h))
 r['nearby']=[dict(dx=dx,dy=dy,floor=cell(x+dx,y+dy,h)[0],nswe=cell(x+dx,y+dy,h)[1]) for dx,dy in ((0,-300),(300,0),(-300,0),(0,300),(600,0),(0,600))]
 results.append(r)
report=dict(bytes=len(b),block_types=dict(types),entries=results)
(D/'generated-geodata-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
