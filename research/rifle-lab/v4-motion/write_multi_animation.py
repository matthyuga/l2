"""Offline Lineage2 v123/license30 MeshAnimation with one MotionChunk per sequence.
Derived from native/write_l2_animation.py. Does not install resources.
"""
import struct,json,math,uuid,hashlib,sys
from pathlib import Path
sys.path.insert(0,r'E:\l2-local\research\dust2-animation-study\native')
from write_l2_animation import ci,psa,chunks
P=struct.pack
def generate(entries,out,skeleton):
 sources=[]
 _,count,raw=chunks(skeleton)['REFSKELT']
 for entry in entries:
  src=psa(entry['psa']);assert len(src['bones'])==count
  for i,b in enumerate(src['bones']):
   nm,flags,children,parent=struct.unpack_from('<64s3i',raw,i*120)
   assert b['name']==nm.rstrip(b'\0').decode();b['parent']=parent
  src['name']=entry['name'];sources.append(src)
 bones=sources[0]['bones'];assert all(s['bones']==bones for s in sources)
 names=list(dict.fromkeys(['None','Core','Package','Class','Engine','MeshAnimation','Dust2Motion']+[s['name'] for s in sources]+[b['name'] for b in bones]))
 nr=lambda n:ci(names.index(n))
 nametable=b''.join(ci(len(n)+1)+n.encode()+b'\0'+P('<I',0x70010) for n in names)
 imports=nr('Core')+nr('Package')+P('<i',0)+nr('Engine')+nr('Core')+nr('Class')+P('<i',-1)+nr('MeshAnimation')
 refbones=ci(len(bones))+b''.join(nr(b['name'])+P('<Ii',0,b['parent']) for b in bones)
 def arr(values,fmt):return ci(len(values))+b''.join(P('<'+fmt,*v) if isinstance(v,(list,tuple)) else P('<'+fmt,v) for v in values)
 motions=[];seqs=[]
 for src in sources:
  frames=src['frames'];fps=src['fps'];assert frames and fps>0
  motion=P('<3ffii',0,0,0,len(frames),0,0)+arr(list(range(len(bones))),'i')+ci(len(bones))
  for b in range(len(bones)):
   ps=[];qs=[]
   for f in frames:
    p=f['positions'][b];q=f['rotations'][b]
    assert all(math.isfinite(x) for x in (*p,*q)) and abs(sum(x*x for x in q)-1)<0.01
    ps.append([p[0],-p[1],p[2]]);qs.append([q[0],-q[1],q[2],-q[3]])
   motion+=P('<I',0)+arr(qs,'4f')+arr(ps,'3f')+arr(list(range(len(frames))),'f')
  motion+=P('<I',0)+ci(0)*3;motions.append(motion)
  seq=P('<f',0)+nr(src['name'])+ci(0)+P('<ii',0,len(frames))+ci(0)+P('<f',fps)
  seq+=P('<3i',0,0,0)+ci(0)+P('<2i',0,0)
  seq+=b'\0'+ci(0)+ci(0)+P('<2i',0,0)+ci(0);seqs.append(seq)
 prefix=nr('None')+P('<i',1)+refbones
 nameoff=64;importoff=nameoff+len(nametable);exportoff=importoff+len(imports);dataoff=exportoff+20
 for _ in range(10):
  cursor=dataoff+len(prefix)+4+len(ci(len(motions)));movebytes=b''
  for motion in motions:
   cursor+=4+len(motion);movebytes+=P('<i',cursor)+motion
  payload=prefix+P('<i',cursor)+ci(len(motions))+movebytes+ci(len(seqs))+b''.join(seqs)
  export=ci(-2)+ci(0)+P('<i',0)+nr('Dust2Motion')+P('<I',0x70004)+ci(len(payload))+ci(dataoff)
  newoff=exportoff+len(export)
  if newoff==dataoff:break
  dataoff=newoff
 else:raise RuntimeError('Offset convergence failed')
 header=P('<IHH7I',0x9e2a83c1,123,30,1,len(names),nameoff,1,exportoff,2,importoff)+uuid.uuid5(uuid.NAMESPACE_OID,hashlib.sha256(nametable+imports+payload).hexdigest()).bytes_le+P('<3I',1,1,len(names))
 data=header+nametable+imports+export+payload;Path(out).write_bytes(data)
 return {'output':str(out),'sha256':hashlib.sha256(data).hexdigest(),'bones':len(bones),'bytes':len(data),'sequences':[{'name':s['name'],'frames':len(s['frames']),'fps':s['fps']} for s in sources],'native_client_validated':False}
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('config');ap.add_argument('output');ap.add_argument('--skeleton',required=True);a=ap.parse_args()
 report=generate(json.loads(Path(a.config).read_text()),a.output,a.skeleton);Path(a.output+'.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
