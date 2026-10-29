"""Native serializer save/reload check, exclusively on the isolated snapshot."""
from pathlib import Path
import sys,subprocess,json,hashlib,collections
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'airships'))
from read_map import Package
src=ROOT/'Packages/24_19.unr'; out=ROOT/'Mapconvert';out.mkdir(exist_ok=True)
dst=out/'24_19.unr'
p=Package(src)
flag='+AllowDownload' if p.flags&1 else '-AllowDownload'
def run(args,log):
 try:
  r=subprocess.run([str(ROOT/'System/UCC.exe'),*args,'ini=GludioEditor.ini','-unattended','-nosound'],cwd=ROOT/'System',capture_output=True,text=True,errors='replace',timeout=90)
  (ROOT/log).write_text(r.stdout+r.stderr,encoding='utf-8');print((r.stdout+r.stderr)[-3500:],flush=True);return r.returncode
 except subprocess.TimeoutExpired as e:
  (ROOT/log).write_bytes((e.stdout or b'')+(e.stderr or b''));return 'timeout'
result={'save_exit':run(['mapconvert',str(src),str(dst)],'mapconvert-save.txt'),'method':'mapconvert (not GUI Save)'}
if dst.exists():
 q=Package(dst)
 def inventory(pkg):return {(pkg.ref(i+1),pkg.ref(e['cl'])):e for i,e in enumerate(pkg.exports)}
 a=inventory(p);b=inventory(q)
 result.update({'before_exports':len(a),'after_exports':len(b),'missing_exports':[list(x) for x in a.keys()-b.keys()],'added_exports':[list(x) for x in b.keys()-a.keys()],'flags_before':p.flags,'flags_after':q.flags,'versions':[[p.version,p.license],[q.version,q.license]]})
 aa={x['actor']:x for x in p.actors()};bb={x['actor']:x for x in q.actors()}
 result['static_mesh_actors']=[len(aa),len(bb)]
 result['changed_actor_properties']=[k for k in aa.keys()&bb.keys() if aa[k]!=bb[k]]
 result['missing_actors']=list(aa.keys()-bb.keys())
 result['added_actors']=list(bb.keys()-aa.keys())
 export=out/'Exports';export.mkdir(exist_ok=True)
 result['reload_exit']=run(['batchexport',str(dst),'Level','t3d',str(export)],'mapconvert-reload.txt')
 result['t3d_identical']=(ROOT/'Exports/myLevel.t3d').read_bytes()==(export/'myLevel.t3d').read_bytes() if (export/'myLevel.t3d').exists() else False
 result['ready_for_install']=False
 result['note']='Native serializer check only; UI save and visual fidelity still require validation. Do not install output.'
(ROOT/'mapconvert-proof.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:(len(v) if isinstance(v,list) and len(v)>20 else v) for k,v in result.items()},indent=2),flush=True)
