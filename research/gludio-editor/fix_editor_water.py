"""Add an isolated root-level Water01 alias; leave client and open map alone."""
from pathlib import Path
import sys,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'gludio-sky'))
from package_tools import Edit
dst=ROOT/'Packages/HGEditorWater.usx'
p=Edit(ROOT/'Packages/water.usx')
e=next(e for e in p.exports if e['name']=='Water01')
before=e['outer'];e['outer']=0
p.save(dst)
work=ROOT/'Working-v2';work.mkdir(exist_ok=True)
target=work/'24_19.unr'
if target.exists():raise SystemExit('Refusing to overwrite existing v2 work map.')
m=Edit(ROOT/'Working/24_19.unr')
edits=[]
for imp in m.imports:
 if imp['outer']==0 and imp['cl']=='Package' and imp['name'].lower()=='water':
  edits.append(dict(imp));imp['name']='HGEditorWater';m.name('HGEditorWater')
m.save(target)
out=ROOT/'Exports-v2';out.mkdir(exist_ok=True)
args=[str(ROOT/'System/UCC.exe'),'batchexport',str(target),'Level','t3d',str(out),'ini=GludioEditor.ini','log=GludioLoad-v2.log','-unattended','-nosound']
r=subprocess.run(args,cwd=ROOT/'System',capture_output=True,text=True,errors='replace',timeout=60)
(ROOT/'native-load-v2.txt').write_text(r.stdout+r.stderr)
log=(ROOT/'System/GludioLoad-v2.log').read_text(errors='replace')
warn=[l for l in log.splitlines() if 'Warning:' in l]
manifest=json.loads((ROOT/'snapshot.json').read_text())
unchanged=all(hashlib.sha256(Path(f['source']).read_bytes()).hexdigest()==f['sha256'] for f in manifest['files'])
proof={'exit':r.returncode,'originals_unchanged':unchanged,'water_mesh_missing':any('Missing StaticMesh' in l and 'Water01' in l for l in warn),'remaining_warnings_count':len(warn),'unique_warnings':sorted(set(warn)),'map':str(target),'editor_only_mesh_alias':str(dst),'original_mesh_outer':before,'client_modified':False,'gui_verified':False,'ready_for_install':False}
(ROOT/'waterfix-proof.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
