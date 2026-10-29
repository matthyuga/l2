"""Read-only archive/dependency inventory. Does not certify rendering or playability."""
from pathlib import Path,PurePosixPath
import sys,json,subprocess,concurrent.futures,zipfile,collections,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent/'audit';OUT.mkdir(exist_ok=True)
LIB=Path(r'K:\assets descargables de l2\01-escenarios-y-estructuras')
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package
UNRAR=r'C:\Program Files\WinRAR\UnRAR.exe';SEVEN=r'K:\assets descargables de l2\_herramientas\7zip\7zr.exe'
EXT={'.unr','.usx','.utx','.ukx','.uax','.u'}
archives=sorted(p for p in LIB.rglob('*') if p.suffix.lower() in ['.rar','.7z','.zip'])
def extract(p):
 ident=hashlib.sha1(str(p).encode()).hexdigest()[:12];folder=OUT/'packages'/ident;assets=folder/'assets';assets.mkdir(parents=True,exist_ok=True)
 cache=folder/'source.json'
 if cache.exists():return json.loads(cache.read_text(encoding='utf-8'))
 record=dict(id=ident,archive=str(p),name=p.name,assets=str(assets),bytes=p.stat().st_size)
 try:
  if p.suffix.lower()=='.rar':
   listing=subprocess.check_output([UNRAR,'lb','-c-',str(p)],text=True,errors='replace',timeout=60).splitlines()
   names=[n for n in listing if Path(n).suffix.lower() in EXT]
   assert all('..' not in PurePosixPath(n.replace('\\','/')).parts and ':' not in n and not n.startswith(('/','\\')) for n in names)
   test=subprocess.run([UNRAR,'t','-idq',str(p)],capture_output=True,timeout=240)
   if names:subprocess.run([UNRAR,'x','-o+','-idq',str(p),*names,str(assets)+'\\'],check=True,capture_output=True,timeout=240)
   record['integrity_exit']=test.returncode
  elif p.suffix.lower()=='.zip':
   with zipfile.ZipFile(p) as z:
    record['integrity_exit']=0 if z.testzip() is None else 1
    names=[n for n in z.namelist() if Path(n).suffix.lower() in EXT]
    assert all('..' not in PurePosixPath(n.replace('\\','/')).parts and ':' not in n and not n.startswith(('/','\\')) for n in names)
    for n in names:z.extract(n,assets)
  else:
   test=subprocess.run([SEVEN,'t',str(p)],capture_output=True,timeout=240);record['integrity_exit']=test.returncode
   subprocess.run([SEVEN,'x','-y','-o'+str(assets),*['-ir!*'+e for e in sorted(EXT)],str(p)],check=True,capture_output=True,timeout=240)
  record['files']=[str(f) for f in assets.rglob('*') if f.suffix.lower() in EXT]
 except Exception as e:record['error']=str(e)
 cache.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');return record
def parse(path):
 p=Package(path)
 exports={p.ref(i+1).lower() for i in range(len(p.exports))}
 imports=[dict(ref=p.ref(-i-1),kind=e['cl']) for i,e in enumerate(p.imports)]
 classes=collections.Counter(p.ref(e['cl']) for e in p.exports)
 result=dict(version=p.version,license=p.license,exports=exports,imports=imports,classes=dict(classes))
 if Path(path).suffix.lower()=='.unr':
  terrains=[]
  for e in p.exports:
   if p.ref(e['cl'])=='Engine.TerrainInfo':
    pr=p.props(e);layers=[]
    for k,v in pr.items():
     if k.startswith('Layers'):
      layer=p.props(dict(offset=v['raw_offset'],size=v['size'],flags=0,name=k));layers.append({a:layer.get(a) for a in ['Texture','AlphaMap']})
    terrains.append(dict(name=e['name'],heightmap=pr.get('TerrainMap'),location=pr.get('Location'),layers=layers,active_layers=sum(l.get('Texture') not in [None,'None'] for l in layers)))
  actors=p.actors();result.update(terrains=terrains,actors=len(actors),mesh_refs=sorted({a['StaticMesh'] for a in actors}),floor_named_refs=[a for a in sorted({a['StaticMesh'] for a in actors}) if any(s in a.lower() for s in ['floor','bottom','ground'])])
 return result
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
  records=[]
  for i,r in enumerate(ex.map(extract,archives),1):records.append(r);print('EXTRACTED',i,len(archives),r['name'],r.get('error','OK'),flush=True)
 (OUT/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 globalindex=collections.defaultdict(list)
 for r in records:
  for f in r.get('files',[]):globalindex[Path(f).stem.lower()].append(f)
 native=json.loads((ROOT/'research/npc-batch2/native-package-index.json').read_text(encoding='utf-8'))
 cache={};errors={}
 def get(path):
  if path not in cache:
   try:cache[path]=parse(path)
   except Exception as e:cache[path]=None;errors[path]=repr(e)
  return cache[path]
 visual={'Texture','Shader','FinalBlend','Combiner','TexPanner','TexRotator','TexScaler','ColorModifier','TexEnvMap','Cubemap','Material','StaticMesh','SkeletalMesh','TexOscillator','TexModifier'}
 reports=[]
 for n,r in enumerate(records,1):
  local=collections.defaultdict(list)
  for f in r.get('files',[]):local[Path(f).stem.lower()].append(f)
  def resolve(ref,current=None):
   if current and ref.lower() in current['exports']:return 'internal'
   if '.' not in ref:return 'internal'
   pkg,obj=ref.split('.',1);key=pkg.lower();obj=obj.lower();candidates=local.get(key,[])
   if not candidates and key in native:candidates=[native[key]]
   if not candidates:return 'other_archive' if key in globalindex else 'missing_package'
   parsed=[get(f) for f in candidates];readable=[d for d in parsed if d]
   if not readable:return 'unreadable_dependency'
   return 'resolved' if any(obj in d['exports'] for d in readable) else 'missing_object'
  report=dict(source=r,maps=[],dependencies=[],parse_errors=[])
  declared={}
  for f in r.get('files',[]):
   d=get(f)
   if not d:report['parse_errors'].append(dict(file=f,error=errors.get(f)));continue
   for imp in d['imports']:
    if imp['kind'] in visual and '.' in imp['ref']:declared[imp['ref']]=imp['kind']
   if Path(f).suffix.lower()=='.unr':
    entry={k:v for k,v in d.items() if k not in ['exports','imports']};entry['file']=f
    entry['actor_dependencies']=[dict(ref=ref,status=resolve(ref,d)) for ref in d['mesh_refs']]
    entry['terrain_dependencies']=[dict(ref=ref,status=resolve(ref,d)) for t in d['terrains'] for ref in [t['heightmap'],*[l.get(k) for l in t['layers'] for k in ['Texture','AlphaMap']]] if ref and ref!='None']
    report['maps'].append(entry)
  for ref,kind in sorted(declared.items()):
   status=resolve(ref)
   if status not in ['resolved','internal']:report['dependencies'].append(dict(ref=ref,kind=kind,status=status))
  report['declared_visual_refs']=len(declared);reports.append(report);print('AUDITED',n,r['name'],'maps',len(report['maps']),'unresolved',len(report['dependencies']),'parse_errors',len(report['parse_errors']),flush=True)
  # Keep metadata only; Package raw bytes are not retained by parse().
 (OUT/'library-audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
 print('AUDIT_COMPLETE',len(reports),flush=True)
if __name__=='__main__':main()
