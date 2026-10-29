from pathlib import Path
import json,sys,subprocess,re,hashlib
ROOT=Path(r'E:\l2-local');STAGE=ROOT/'research/npc-batch2';OUT=ROOT/'research/model-catalog';sys.path.insert(0,str(OUT));import build_gallery as b
id=sys.argv[1];folder=STAGE/'packages'/id;plan=json.loads((folder/'plan.json').read_text(encoding='utf-8'));assets=folder/'assets';b.EXPORT=OUT/'exports/tanda2'/id;b.EXPORT.mkdir(parents=True,exist_ok=True);b.LOGS=folder/'export-logs';b.LOGS.mkdir(exist_ok=True);b.texture_cache={};b.OPTIONS=['-game=l2','-path='+str(assets)]
asset_index={}
for f in assets.rglob('*'):
 if f.is_file() and f.suffix.lower() in ['.ukx','.utx','.usx','.u']:asset_index.setdefault(f.stem.lower(),[]).append(f)
native_index={k:Path(v) for k,v in json.loads((STAGE/'native-package-index.json').read_text()).items()}
def run(args):
 non=next((a for a in args if not a.startswith('-')),None);path=assets;variants=[None]
 if non:
  pkg=Path(non).stem.lower() if non.lower().endswith(('.ukx','.usx','.utx','.u')) else non.lower()
  if pkg in asset_index:
   variants=asset_index[pkg]
   order=['.ukx','.usx','.u','.utx'] if non.lower().endswith(('.ukx','.usx')) else ['.utx','.ukx','.u','.usx']
   variants=sorted(variants,key=lambda f:order.index(f.suffix.lower()))
  elif pkg in native_index:path=ROOT.parent/'l2'
 error=''
 for target in variants:
  fixed=list(args)
  if target and non:fixed[args.index(non)]=str(target)
  p=subprocess.run([str(b.UMODEL),*fixed,'-game=l2','-path='+str(path)],capture_output=True,text=True,errors='replace',timeout=80)
  if p.returncode==0:return p.stdout+'\n'+p.stderr
  error=(p.stdout+p.stderr)[-1200:]
 raise RuntimeError(error)

b.run=run;items=[];errors=list(plan['errors'])
for v in plan['models']:
 reportfile=folder/(v['key']+'.json')
 if reportfile.exists():
  old=json.loads(reportfile.read_text(encoding='utf-8'))
  if old.get('material_import_version')==2 and old.get('status')=='ready' and (OUT/old['gltf']).exists():items.append(old);continue
 title=re.sub(r'\s*\[[^]]*\]','',v['archive_title']).strip();category='Bosses' if any(x in title.lower() for x in ['boss','freya','lindvior','fafurion','balok','istina','halisha','anakazel']) else 'Objetos' if v['kind']=='StaticMesh' else 'NPC' if any(x in title.lower() for x in ['npc','guide','trader','ert ','healer','hancock','yorha','daji','kalifa','gk ']) else 'Monstruos'
 m={'key':v['key'],'mesh':v['mesh'],'package':v['package'],'title':title+' · '+v['mesh'].split('.',1)[1],'names':[title,v['version']],'category':category,'npcs':[{'textures':v['textures']}] if v['textures'] else [],'npc_count':0,'texture_variants':0,'types':['Recurso externo'],'external_source':True,'batch':'Tanda 2','archive_id':id,'archive_title':v['archive_title'],'chronicle':v['version'],'asset_root':v['asset_root'],'viewer_extension':v['extension'].lstrip('.'),'source_npc_id':v.get('source_id')}
 try:
  # prepare() assumes ukx; run() resolves the actual extension and local source package.
  b.prepare(m);m['npcs']=[];m['note']=m.get('note','')+' Vista de un recurso externo; IDs, stats e IA aun no integrados al servidor.'
 except Exception as e:m['npcs']=[];m.update(status='failed',error=str(e));errors.append({'mesh':v['mesh'],'error':str(e)})
 m['material_import_version']=2
 reportfile.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');items.append(m)
(folder/'gallery-models.json').write_text(json.dumps({'models':items,'errors':errors,'archive':plan['source']},ensure_ascii=False,indent=2),encoding='utf-8');print(id,len(items),'ready',sum(m['status']=='ready' for m in items),flush=True)
