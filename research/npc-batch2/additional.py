from pathlib import Path
import json,re,subprocess,concurrent.futures,hashlib
ROOT=Path(r'E:\l2-local');S=ROOT/'research/npc-batch2';UM=ROOT/'research/amber-l2/tools/umodel.exe';seven=Path(r'K:\assets descargables de l2\_herramientas/7zip/7zr.exe')
def more(p):
 j=json.loads(p.read_text(encoding='utf-8'));assets=p.parent/'assets';src=j['source'];id=p.parent.name
 # Collect native files from nested archives too, retaining package isolation.
 orig=src['archivo'];sub=p.parent/'nested';sub.mkdir(exist_ok=True)
 subprocess.run([str(seven),'x','-o'+str(sub),'-ir!*.7z','-y',orig],capture_output=True,timeout=100)
 for n in sub.rglob('*.7z'):
  subprocess.run([str(seven),'x','-o'+str(assets/'nested'/n.stem),'-ir!*.ukx','-ir!*.utx','-ir!*.usx','-ir!*.u','-ir!*.txt','-y',str(n)],capture_output=True,timeout=100)
 known={m['package_file'] for m in j['models']};new=[]
 for f in assets.rglob('*'):
  if not f.is_file() or f.suffix.lower() not in ['.u','.ukx','.usx'] or str(f) in known:continue
  r=subprocess.run([str(UM),'-list','-game=l2','-path='+str(assets),str(f)],capture_output=True,text=True,errors='replace',timeout=50)
  (p.parent/(f.stem+'-extra-list.txt')).write_text(r.stdout+r.stderr,encoding='utf-8')
  if r.returncode:continue
  for kind,obj in re.findall(r'^\s*\d+\s+[0-9A-F]+\s+[0-9A-F]+\s+(SkeletalMesh|StaticMesh)\s+(\S+)\s*$',r.stdout,re.M):
   mesh=f.stem+'.'+obj;key='b2_'+hashlib.sha256((id+mesh).encode()).hexdigest()[:18]
   new.append({'key':key,'mesh':mesh,'package':f.stem,'extension':f.suffix,'kind':kind,'textures':[],'archive_id':id,'archive_title':src['titulo'],'version':src['version_anunciada'],'asset_root':str(assets.relative_to(ROOT)).replace('\\','/'),'package_file':str(f),'source_archive':orig})
 unique={m['key']:m for m in j['models']+new};j['models']=list(unique.values());p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8');return len(new)
ps=list((S/'packages').glob('*/plan.json'))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 counts=list(ex.map(more,ps))
print('Additional models',sum(counts),flush=True)
allmodels=[m for p in ps for m in json.loads(p.read_text(encoding='utf-8'))['models']];(S/'plan.json').write_text(json.dumps({'models':allmodels},ensure_ascii=False,indent=2),encoding='utf-8');print('TOTAL',len(allmodels),flush=True)
