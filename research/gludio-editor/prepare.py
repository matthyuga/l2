"""Isolated snapshot and native loading probe. Never writes to the client."""
from pathlib import Path
import sys, json, hashlib, shutil, subprocess, re, time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'airships'))
from read_map import Package
CLIENT=Path('E:/l2')
BASE=ROOT.parent/'amber-l2/tools/l2editor/L2Editor'
SYSTEM=ROOT/'System'; PACKAGES=ROOT/'Packages'; ORIGINAL=ROOT/'Original'
for d in (SYSTEM,PACKAGES,ORIGINAL,ROOT/'Exports'): d.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
index={}
for folder in ('maps','StaticMeshes','Textures','Sounds','SysTextures','system','system-hud','Animations'):
 for p in (CLIENT/folder).glob('*'):
  if p.suffix.lower() in ('.unr','.u','.utx','.usx','.uax','.ukx'):index.setdefault(p.stem.lower(),p)
native={'core','engine','editor','fire','unrealed','ipdrv','alaudio','uweb'}
manifest={'client':str(CLIENT),'map':'24_19','files':[], 'native_editor_packages':sorted(native),'missing':[]}
seen=set()
def stage(name):
 key=name.lower()
 if key in seen or key in native:return
 seen.add(key)
 src=index.get(key)
 if not src:manifest['missing'].append(name);return
 dst=ORIGINAL/src.name
 if dst.exists() and sha(dst)!=sha(src):raise RuntimeError('Existing snapshot differs: '+str(src))
 if not dst.exists():shutil.copy2(src,dst)
 raw=src.read_bytes()
 if raw[:4]!=b'\xc1\x83\x2a\x9e':
  marker=raw[:28].decode('utf-16le',errors='ignore')
  if marker not in ('Lineage2Ver111','Lineage2Ver121'):raise RuntimeError('Unsupported '+str(src))
  keybyte=172 if marker.endswith('111') else sum(map(ord,src.name.lower()))&255
  raw=raw[28:-20].translate(bytes.maketrans(bytes(range(256)),bytes(x^keybyte for x in range(256))))
 (PACKAGES/src.name).write_bytes(raw)
 p=Package(PACKAGES/src.name)
 manifest['files'].append({'source':str(src),'backup':str(dst),'sha256':sha(src),'bytes':src.stat().st_size,'version':p.version,'license':p.license})
 print('Staged',src.name,flush=True)
 for imp in p.imports:
  if imp['outer']==0 and imp['cl']=='Package':stage(imp['name'])
stage('24_19')
for p in BASE.iterdir():
 if p.is_file() and p.suffix.lower() in ('.dll','.int','.exe','.u','.ini','.bmp'):
  if p.suffix.lower()=='.u' and p.stem.lower() not in {'core','engine','editor','fire','unrealed','ipdrv','alaudio','uweb'}:continue
  if not (SYSTEM/p.name).exists():shutil.copy2(p,SYSTEM/p.name)
for folder in ('EditorRes','UDE'):
 if (BASE/folder).exists():shutil.copytree(BASE/folder,SYSTEM/folder,dirs_exist_ok=True)
ini=(BASE/'UT2003.ini').read_text()
# All package search roots are private copies, never the client.
ini=re.sub(r'^Paths=.*\n?', '', ini,flags=re.M)
ini=ini.replace('[Core.System]','[Core.System]\nPaths=./*.u\n'+'\n'.join('Paths=../Packages/*.'+ext for ext in ('u','utx','usx','unr','uax','ukx')))
(SYSTEM/'GludioEditor.ini').write_text(ini)
(ROOT/'snapshot.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
p=Package(PACKAGES/'24_19.unr')
(ROOT/'map-inventory.json').write_text(json.dumps({'exports':len(p.exports),'imports':len(p.imports),'actors':p.actors()},indent=2))
cmd=[str(SYSTEM/'UCC.exe'),'batchexport',str(PACKAGES/'24_19.unr'),'Level','t3d',str(ROOT/'Exports'),'ini=GludioEditor.ini','-unattended','-nosound']
try:
 r=subprocess.run(cmd,cwd=SYSTEM,capture_output=True,text=True,errors='replace',timeout=90)
 (ROOT/'native-load.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
 result={'exit':r.returncode,'tail':(r.stdout+r.stderr)[-5000:]}
except subprocess.TimeoutExpired as e:
 result={'timeout':True}
 (ROOT/'native-load.txt').write_bytes((e.stdout or b'')+(e.stderr or b''))
result['originals_unchanged']=all(sha(Path(f['source']))==f['sha256']==sha(Path(f['backup'])) for f in manifest['files'])
(ROOT/'probe.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'files':len(manifest['files']),'missing':manifest['missing'],'result':result}),flush=True)
