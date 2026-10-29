"""Read local map archives and export static resources into isolated viewer folders."""
from pathlib import Path
import sys,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;CAT=ROOT/'research/model-catalog'
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package
sys.path.insert(0,str(CAT));import build_gallery as b
specs={
 'r4_arena':('R4 Arena.rar','R4 Arena','16_14'),
 'canon_cathedral':('Canon Cathedral_IL.rar','Canon Cathedral · Interlude','17_17'),
}
ident=sys.argv[1];folder=D/ident;folder.mkdir(exist_ok=True)
if (folder/'task.json').exists():
 task=json.loads((folder/'task.json').read_text(encoding='utf-8'));assets=Path(task['assets']);archive=Path(task['source']);title=task['title'];tile=task['tile'];mapfile=Path(task['mapfile'])
else:
 filename,title,tile=specs[ident];assets=folder/'assets';assets.mkdir(parents=True,exist_ok=True)
 sources=list(Path(r'K:\assets descargables de l2\01-escenarios-y-estructuras').rglob(filename));assert len(sources)==1;archive=sources[0]
 listing=subprocess.check_output(['tar','-tf',str(archive)],text=True,errors='replace').splitlines();native=[n for n in listing if Path(n).suffix.lower() in ['.unr','.usx','.utx','.ukx']]
 assert native and all(not Path(n).is_absolute() and '..' not in Path(n).parts and ':' not in n for n in native)
 subprocess.run([r'C:\Program Files\WinRAR\UnRAR.exe','x','-o+','-idq',str(archive),*[n.replace('/','\\') for n in native],str(assets)+'\\'],check=True,capture_output=True)
 mapfile=next(assets.rglob(tile+'.unr'))
package=Package(mapfile);actors=package.actors();assert actors
(folder/'actors.json').write_text(json.dumps(actors,indent=2),encoding='utf-8')
index={p.stem.lower():p for p in assets.rglob('*') if p.suffix.lower() in ['.usx','.utx','.ukx']}
index[mapfile.stem.lower()]=mapfile
nativeindex=json.loads((ROOT/'research/npc-batch2/native-package-index.json').read_text(encoding='utf-8'))
b.EXPORT=CAT/'exports/scenario-parts'/ident;b.EXPORT.mkdir(parents=True,exist_ok=True);b.LOGS=folder/'logs';b.LOGS.mkdir(exist_ok=True);b.texture_cache={}
def run(args):
 args=list(args);i=next((i for i,a in enumerate(args) if not a.startswith('-')),None);path=assets
 if i is not None:
  stem=Path(args[i]).stem if args[i].lower().endswith(('.ukx','.usx','.utx','.u')) else args[i]
  target=index.get(stem.lower())
  if target:args[i]=str(target)
  elif stem.lower() in nativeindex:args[i]=nativeindex[stem.lower()];path=ROOT.parent/'l2'
 p=subprocess.run([str(b.UMODEL),*args,'-game=l2','-path='+str(path)],capture_output=True,text=True,errors='replace',timeout=60)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr)[-700:])
 return p.stdout+'\n'+p.stderr
shared=D/'shared-parts'/hashlib.sha1(str(assets).encode()).hexdigest()[:16];shared.mkdir(parents=True,exist_ok=True)
b.run=run;meshes={};failed=[]
cachefile=folder/'parts-cache.json'
if cachefile.exists():meshes=json.loads(cachefile.read_text(encoding='utf-8'))
for ref in sorted({a['StaticMesh'] for a in actors}):
 if ref in meshes and (CAT/meshes[ref]['gltf']).is_file():continue
 partcache=shared/(hashlib.sha1(ref.encode()).hexdigest()+'.json')
 if partcache.exists():
  try:
   cached=json.loads(partcache.read_text(encoding='utf-8'))
   if (CAT/cached['gltf']).is_file():meshes[ref]=cached;continue
  except (ValueError,KeyError,OSError):pass
 if '.' not in ref:failed.append({'mesh':ref,'error':'Referencia interna no calificada'});continue
 pkg,obj=ref.split('.',1);m={'key':ident+'_'+hashlib.sha1(ref.encode()).hexdigest()[:12],'mesh':pkg+'.'+obj.split('.')[-1],'npcs':[]}
 try:
  b.prepare(m);m['mesh']=ref;meshes[ref]=m;cachefile.write_text(json.dumps(meshes),encoding='utf-8');temp=partcache.with_suffix('.'+ident+'.tmp');temp.write_text(json.dumps(m),encoding='utf-8');temp.replace(partcache)
 except Exception as e:failed.append({'mesh':ref,'error':str(e)})
 if (len(meshes)+len(failed))%10==0:print(ident,'parts',len(meshes),'missing',len(failed),flush=True)
manifest=dict(ident=ident,title=title,tile=tile,source=str(archive),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),actors=actors,meshes=meshes,failed=failed,map_version=package.version)
(folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(ident,'ACTORS',len(actors),'PARTS',len(meshes),'FAILED',len(failed),flush=True)
