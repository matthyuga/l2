"""Subtract only the exact V2 layers recorded at installation, keeping later work."""
from pathlib import Path
import sys,json,collections,struct,hashlib
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
sys.path.insert(0,str(ROOT/'research/gludio-sky'));from package_tools import Reader
source=ROOT/'server/game/data/geodata/24_19.l2j';b=source.read_bytes();r=Reader(b)
old={int(k):v for k,v in json.loads((D.parent/'vigilia-clan-v2/encoded-layers.json').read_text()).items()}
out=bytearray();removed=0
for bx in range(256):
 for by in range(256):
  start=r.p;ty=r.num('B')
  if ty==0:
   z=r.num('h');cells=[[((z<<1)&0xfff0)|15] for _ in range(64)]
  else:
   assert ty in [1,2];cells=[]
   for _ in range(64):cells.append([r.num('H') for _ in range(1 if ty==1 else r.num('B'))])
  deletes=[old.get((by*8+cy)*2048+bx*8+cx,[]) for cx in range(8) for cy in range(8)]
  if not any(deletes):out+=b[start:r.p];continue
  out.append(2)
  for vs,ds in zip(cells,deletes):
   for v in ds:assert v in vs,('V2 layer changed',bx,by,v);vs.remove(v);removed+=1
   assert vs,'Removal would erase original world floor'
   out.append(len(vs));out+=struct.pack('<'+'H'*len(vs),*vs)
out+=b[r.p:];(D/'clean-source.l2j').write_bytes(out)
(D/'retirement-audit.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(b).hexdigest(),removed_v1_layers=removed,removed_v1_cells=len(old)),indent=2))
print('REMOVED_ONLY_V2_GEO',removed,'layers')
