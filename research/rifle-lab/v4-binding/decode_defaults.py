import sys,struct,json
from pathlib import Path
sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\native')
from inspect_package import *
ROOT=Path(r'E:\l2-local\research\rifle-lab\v4-binding')
def props(p,data,start):
 r=Reader(data,start);out=[]
 while True:
  n=r.ci()
  if n==0:return out,r.p
  assert 0<n<len(p.names)
  tag=data[r.p];r.p+=1;typ=tag&15;sc=(tag>>4)&7
  assert typ in range(1,16)
  sn=None
  if typ==10:sn=p.names[r.ci()]
  size=[1,2,4,12,16,None,None,None][sc]
  if sc==5:size=data[r.p];r.p+=1
  elif sc==6:size=struct.unpack_from('<H',data,r.p)[0];r.p+=2
  elif sc==7:size=r.u()
  ix=0
  if tag&128 and typ!=3:
   ix=data[r.p];r.p+=1
   if ix&128:raise ValueError()
  if typ==3:v=bool(tag&128);size=0
  else:
   assert size<100000 and r.p+size<=len(data)
   d=data[r.p:r.p+size];r.p+=size;v=d.hex()
   if typ==4 and size==4:v=struct.unpack('<f',d)[0]
   elif typ==2 and size==4:v=struct.unpack('<i',d)[0]
   elif typ==6:v=p.names[Reader(d).ci()]
   elif typ==5:v=p.obj(Reader(d).ci())
   elif typ==10 and sn=='Vector' and size==12:v=list(struct.unpack('<3f',d))
  out.append(dict(name=p.names[n],type=typ,index=ix,struct=sn,value=v))
for pkg,cls in [('LineageNPC','a_traderB_FHuman'),('LineageWarrior','LineagePawn'),('Engine','Pawn'),('Engine','Actor')]:
 p=Package(fr'E:\l2\system-hud\{pkg}.u');ex=next(e for i,e in enumerate(p.exports) if p.obj(i+1)==cls);d=p.d[ex['offset']:ex['offset']+ex['size']];found=[]
 for start in range(len(d)):
  try:
   out,end=props(p,d,start)
   if end==len(d) and len(out)>=3:found.append((start,out))
  except Exception:pass
 start,out=max(found,key=lambda z:len(z[1]))
 print(pkg,cls,'start',start,'properties',len(out))
 (ROOT/(pkg+'-'+cls+'-defaults.json')).write_text(json.dumps(out,indent=2))
 for a in out:
  if any(s in a['name'].lower() for s in ['pivot','scale','height','mesh','animname','collision']):print(a)
