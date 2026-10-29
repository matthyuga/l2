"""OFFLINE one-sequence replacement. Original input package is never written."""
import argparse,pathlib,struct,json,hashlib
from inspect_package import Package,Reader
from write_l2_animation import ci
P=struct.pack

def animation(p,export_name):
 e=next(e for e in p.exports if p.names[e['name']]==export_name)
 r=Reader(p.d,e['offset']);assert p.names[r.ci()]=='None','Unexpected serialized UObject properties';assert r.i()==1
 n=r.ci();bones=[]
 for _ in range(n):bones.append((p.names[r.ci()],r.u(),r.i()))
 prefix=p.d[e['offset']:r.p];global_end=r.i();nm=r.ci();moves=[]
 for _ in range(nm):
  local_end=r.i();assert r.p<=local_end<=global_end;moves.append(p.d[r.p:local_end]);r.p=local_end
 assert r.p==global_end
 ns=r.ci();assert ns==nm;seqs=[]
 for _ in range(ns):
  start=r.p;r.p+=4;name=p.names[r.ci()]
  for _ in range(r.ci()):r.ci()
  sf=r.i();nf=r.i()
  for _ in range(r.ci()):r.p+=4;r.ci();r.ci()
  rate=struct.unpack_from('<f',r.d,r.p)[0];r.p+=4
  r.p+=12;r.ci();r.p+=8 # f2c,f30,f34, object f38,f3c,f40
  r.p+=1
  nitems=r.ci();r.p+=nitems*8
  for _ in range(r.ci()):r.p+=4;nitems=r.ci();r.p+=nitems*8
  r.p+=8;nitems=r.ci();r.p+=nitems*8
  seqs.append(dict(name=name,frames=nf,fps=rate,raw=p.d[start:r.p]))
 assert r.p==e['offset']+e['size'],(r.p,e['offset']+e['size'])
 return e,prefix,bones,moves,seqs

def replace(original,new,out,target):
 p=Package(original);q=Package(new)
 e,prefix,bones,moves,seqs=animation(p,'FFighter_anim');_,_,newbones,newmoves,newseqs=animation(q,'Dust2Motion')
 assert [b[0] for b in bones]==[b[0] for b in newbones]
 idx=next(i for i,s in enumerate(seqs) if s['name']==target);old=seqs[idx]
 # Replacement has zero optional metadata/notifies and original name-table reference.
 nf=newseqs[0]['frames'];rate=newseqs[0]['fps']
 raw=P('<f',0)+ci(p.names.index(target))+ci(0)+P('<ii',0,nf)+ci(0)+P('<f',rate)+P('<3i',0,0,0)+ci(0)+P('<2i',0,0)+b'\0'+ci(0)*2+P('<2i',0,0)+ci(0)
 oldmovehash=hashlib.sha256(moves[idx]).hexdigest();moves[idx]=newmoves[0];seqs[idx]=dict(name=target,frames=nf,fps=rate,raw=raw)
 off=len(p.d);position=off+len(prefix)+4+len(ci(len(moves)));parts=[]
 for m in moves:position+=4+len(m);parts.append(P('<i',position)+m)
 payload=prefix+P('<i',position)+ci(len(moves))+b''.join(parts)+ci(len(seqs))+b''.join(s['raw'] for s in seqs)
 exp=[]
 for v in p.exports:
  size,offset=(len(payload),off) if v is e else (v['size'],v['offset'])
  exp.append(ci(v['cls'])+ci(v['super'])+P('<i',v['outer'])+ci(v['name'])+P('<I',v['flags'])+ci(size)+(ci(offset) if size else b''))
 data=bytearray(p.d+payload+b''.join(exp));struct.pack_into('<I',data,24,off+len(payload))
 out=pathlib.Path(out);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 # Re-read own result independently: every unrelated native move/seq and every unrelated export is byte-identical.
 verify=Package(out);ve,vprefix,vbones,vmoves,vseqs=animation(verify,'FFighter_anim')
 _,oprefix,obones,omoves,oseqs=animation(p,'FFighter_anim')
 assert prefix==vprefix and bones==vbones
 assert all(vmoves[i]==omoves[i] and vseqs[i]['raw']==oseqs[i]['raw'] for i in range(len(moves)) if i!=idx)
 preserved=0
 for i,(a,b) in enumerate(zip(p.exports,verify.exports)):
  if a is e:continue
  assert p.d[a['offset']:a['offset']+a['size']]==verify.d[b['offset']:b['offset']+b['size']];preserved+=1
 report=dict(original=str(original),source=str(new),output=str(out),replaced_sequence=target,sequence_index=idx,original_frames=old['frames'],new_frames=nf,fps=rate,other_sequences_preserved=len(moves)-1,other_exports_preserved=preserved,original_sha256=hashlib.sha256(pathlib.Path(original).read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),runtime_validated=False)
 out.with_suffix('.validation.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('original');a.add_argument('new');a.add_argument('output');a.add_argument('--target',default='Social_bow_FFighter');v=a.parse_args();print(json.dumps(replace(v.original,v.new,v.output,v.target),indent=2))

