from pathlib import Path
import json,re,subprocess,concurrent.futures,hashlib
ROOT=Path(r'E:\l2-local');STAGE=ROOT/'research/npc-batch2';SRC=Path(r'K:\assets descargables de l2\02-monstruos-bosses-y-npcs');SEVEN=Path(r'K:\assets descargables de l2\_herramientas\7zip\7zr.exe');UM=ROOT/'research/amber-l2/tools/umodel.exe';records=json.loads((SRC/'_catalogo/resultado-descargas.json').read_text(encoding='utf-8'))
def process(m):
 id=m['id_drive'];folder=STAGE/'packages'/id;assets=folder/'assets';assets.mkdir(parents=True,exist_ok=True)
 r=subprocess.run([str(SEVEN),'x','-o'+str(assets),'-ir!*.ukx','-ir!*.utx','-ir!*.usx','-ir!*.u','-ir!*.txt','-y',m['archivo']],capture_output=True,timeout=180)
 if r.returncode:raise RuntimeError(m['titulo']+' extraction')
 refs={}
 for p in assets.rglob('*.txt'):
  if 'npcgrp' not in p.name.lower():continue
  text=p.read_bytes().decode('utf-8-sig',errors='replace')
  for line in text.splitlines():
   fields=line.split('\t')
   if len(fields)>2 and '.' in fields[2]:
    mesh=fields[2].strip();textures=[]
    # Param texture overrides usually appear immediately after the mesh and animation flags.
    for v in fields[3:15]:
     if re.fullmatch(r'[A-Za-z0-9_]+\.[A-Za-z0-9_.]+',v) and not v.startswith(('ItemSound.','ChrSound.','LineageEffect.')):textures.append(v)
    refs[mesh.lower()]={'textures':textures,'source_id':fields[0]}
 plan=[];errors=[]
 for p in list(assets.rglob('*.ukx'))+list(assets.rglob('*.usx')):
  r=subprocess.run([str(UM),'-list','-game=l2','-path='+str(assets),p.name],capture_output=True,text=True,errors='replace',timeout=45)
  (folder/(p.stem+'-list.txt')).write_text(r.stdout+r.stderr,encoding='utf-8')
  if r.returncode:errors.append({'package':p.name,'error':(r.stdout+r.stderr)[-500:]});continue
  meshes=re.findall(r'^\s*\d+\s+[0-9A-F]+\s+[0-9A-F]+\s+(SkeletalMesh|StaticMesh)\s+(\S+)\s*$',r.stdout,re.M)
  for kind,obj in meshes:
   mesh=p.stem+'.'+obj;key='b2_'+hashlib.sha256((id+mesh).encode()).hexdigest()[:18];ref=refs.get(mesh.lower(),{})
   plan.append({'key':key,'mesh':mesh,'package':p.stem,'extension':p.suffix,'kind':kind,'source_id':ref.get('source_id'),'textures':ref.get('textures',[]),'archive_id':id,'archive_title':m['titulo'],'version':m['version_anunciada'],'asset_root':str(assets.relative_to(ROOT)).replace('\\','/'),'package_file':str(p),'source_archive':m['archivo']})
 (folder/'plan.json').write_text(json.dumps({'models':plan,'errors':errors,'source':m},ensure_ascii=False,indent=2),encoding='utf-8');return plan,errors
plans=[];errors=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for i,(p,e) in enumerate(ex.map(process,records),1):
  plans+=p;errors+=e
  if i%20==0:print('PACKAGES',i,'MODELS',len(plans),'ERRORS',len(errors),flush=True)
(STAGE/'plan.json').write_text(json.dumps({'models':plans,'errors':errors,'archives':len(records)},ensure_ascii=False,indent=2),encoding='utf-8');print('TOTAL',len(plans),len(errors),flush=True)
