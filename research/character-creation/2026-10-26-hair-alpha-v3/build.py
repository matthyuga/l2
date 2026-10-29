from pathlib import Path
import sys,json,hashlib,subprocess,struct,zlib
D=Path(__file__).resolve().parent;P=Path('E:/l2-local');sys.path.insert(0,str(P/'research/gludio-sky'))
from package_tools import Edit,change_props,tags
sha=lambda b:hashlib.sha256(b).hexdigest()
for n in ['raw','stage']:(D/n).mkdir(exist_ok=True)
files=[];total=0
for name in ['NexusHairMaterialsV2.utx','NexusHairT2M11.utx','NexusHairGRepairV12.utx']:
 target=Path('E:/l2/SysTextures')/name;p=Edit(target);before={e['name']:(p.ref(e['cl']),p.b[e['offset']:e['offset']+e['size']]) for e in p.exports};properties={};changed=[]
 for e in p.exports:
  if p.ref(e['cl'])!='Engine.FinalBlend':continue
  props=p.props(e);blend=p.b[props['FrameBufferBlending']['raw_offset']];assert blend==2
  assert all(props[k] for k in ['ZWrite','ZTest','TwoSided','AlphaTest'])
  properties[e['name']]=props
  p.replace(e,change_props(p,e,{'FrameBufferBlending':p.prop('FrameBufferBlending',1,b'\0')}));changed.append(e['name'])
 raw=D/'raw'/name;p.save(raw);q=Edit(raw);assert q.names==p.names and q.imports==p.imports
 for e in q.exports:
  props=q.props(e)
  if e['name'] in changed:
   old=properties[e['name']];assert q.b[props['FrameBufferBlending']['raw_offset']]==0
   assert props['Material']==old['Material'];assert all(props[k]==old[k] for k in ['ZWrite','ZTest','TwoSided','AlphaTest'])
   assert q.b[props['AlphaRef']['raw_offset']]==p.b[old['AlphaRef']['raw_offset']]
   # Exactly one byte in each serialized material changes; no texture payload.
   oldraw=before[e['name']][1];newraw=q.b[e['offset']:e['offset']+e['size']];assert len(oldraw)==len(newraw);assert sum(a!=b for a,b in zip(oldraw,newraw))==1
  else:assert q.b[e['offset']:e['offset']+e['size']]==before[e['name']][1]
 codec=P/'tools/open-l2encdec-1.3.9/l2encdec_win.exe';out=D/'stage'/name
 r=subprocess.run([str(codec),'-c','encode','-p','121','-f',name,'-o',str(out),str(raw)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0
 check=D/'raw'/('roundtrip-'+name);r=subprocess.run([str(codec),'-f',name,'-o',str(check),str(out)],capture_output=True,input=b'\n',timeout=30);assert r.returncode==0 and check.read_bytes()==raw.read_bytes()
 b=out.read_bytes();assert b[:28].decode('utf-16le')=='Lineage2Ver121';assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
 files.append(dict(target=str(target),before_sha256=sha(target.read_bytes()),after_sha256=sha(b),materials=len(changed),names=changed,changes='FB_AlphaBlend 2 -> FB_Overwrite 0 only; original alpha cutoff/TwoSided/ZWrite/ZTest and texture retained'))
 total+=len(changed)
(D/'assets-manifest.json').write_text(json.dumps(dict(files=files,total_materials=total),indent=2))
print('Prepared',total,'hair-only material corrections; texture pixels/meshes/alpha cutoffs unchanged; protocol121 CRC and decode verified.')
