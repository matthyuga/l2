from pathlib import Path
import json,collections,sys
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'research/gludio-sky'));from package_tools import Reader
r=Reader((D/'stage/Geodata/24_19.l2j').read_bytes());cells={};decode=lambda v:((v if v<32768 else v-65536)&~15)>>1
for bx in range(256):
 for by in range(256):
  ty=r.num('B')
  if ty==0:z=r.num('h');vs=[[(z,15)]]*64
  else:
   vs=[]
   for _ in range(64):
    n=1 if ty==1 else r.num('B');vs.append([(decode(v),v&15) for v in (r.num('H') for _ in range(n))])
  for i,v in enumerate(vs):
   x,y=bx*8+i//8,by*8+i%8
   if any(7500<z<8850 for z,n in v):cells[x,y]=[(z,n) for z,n in v if 7500<z<8850]
exact={(x,y,z):h for x,y,z,h in json.loads((D/'visual-floors.json').read_text())};candidates=[]
for (x,y),vals in cells.items():
 for z,n in vals:
  for dx,dy,bit,rev in [(1,0,1,2),(-1,0,2,1),(0,1,4,8),(0,-1,8,4)]:
   if n&bit:continue
   for nz,nn in cells.get((x+dx,y+dy),[]):
    if 0<nz-z<=48 and nn&rev:
     vz=exact.get((x,y,z));nvz=exact.get((x+dx,y+dy,nz))
     if vz is None or nvz is None:continue
     candidates.append([131072+x*16+8,32768+y*16+8,z,131072+(x+dx)*16+8,32768+(y+dy)*16+8,nz,vz,nvz])
print('Blocked uphill edges with open return',len(candidates),'geo rises',dict(collections.Counter(c[5]-c[2] for c in candidates)),'visual rises',dict(collections.Counter(c[7]-c[6] for c in candidates)))
(D/'blocked-step-edges.json').write_text(json.dumps(candidates))
print('Samples',candidates[:8])
