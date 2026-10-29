"""Resumable isolated imports. Only verified nonempty scenes are published."""
from pathlib import Path
import json,subprocess,hashlib,concurrent.futures,shutil,threading,sys,time
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;G=R/'research/model-catalog';BLENDER=r'D:\BlenderVersions\blender-3.5.1-windows-x64\blender.exe'
audit=json.loads((D/'audit/library-audit.json').read_text(encoding='utf-8'));classified={r['source']:r for r in json.loads((D/'audit/classified-audit.json').read_text(encoding='utf-8'))};lock=threading.Lock()
tasks=[];seen=set()
existing={hashlib.sha256(next((D/n/'assets').rglob('*.unr')).read_bytes()).hexdigest() for n in ['r4_arena','canon_cathedral']}
for item in audit:
 source=item['source'];cl=classified[source['archive']]
 for m in item['maps']:
  path=Path(m['file']);digest=hashlib.sha256(path.read_bytes()).hexdigest()
  if digest in seen or digest in existing:continue
  seen.add(digest);ident='library_'+digest[:12];title=Path(source['name']).stem+' · '+path.stem
  if len([x for x in item['maps'] if Path(x['file']).stem==path.stem])>1:title+=' · '+path.parent.name
  task=dict(ident=ident,title=title,tile=path.stem,mapfile=str(path),assets=source['assets'],source=source['archive'],priority=0 if not cl['direct_warnings'] and not cl['declared_unresolved'] else 1,source_warnings=len(cl['direct_warnings'])+len(cl['declared_unresolved']))
  folder=D/ident;folder.mkdir(exist_ok=True);(folder/'task.json').write_text(json.dumps(task,ensure_ascii=False,indent=2),encoding='utf-8');tasks.append(task)
tasks.sort(key=lambda t:(t['priority'],0 if any(x in t['title'].lower() for x in ['heart','crow','world tree','garden']) else 1,t['title']))
(D/'remaining-tasks.json').write_text(json.dumps(tasks,ensure_ascii=False,indent=2),encoding='utf-8')
backup=D/'gallery-before-remaining-scenes.json'
if not backup.exists():shutil.copy2(G/'gallery.json',backup)
def command(folder,label,args,timeout=3600):
 log=folder/(label+'.log')
 with log.open('wb') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW)
 return r.returncode
def import_one(task):
 folder=D/task['ident'];result=dict(task=task,steps={});key='scenario_batch1_'+task['ident']
 try:
  if (folder/'import-result.json').exists():
   old=json.loads((folder/'import-result.json').read_text(encoding='utf-8'))
   if old.get('published') and (old.get('terrain') or old.get('terrain_retry_done')):return old
  result['steps']['prepare']=command(folder,'prepare',['python',str(D/'prepare.py'),task['ident']])
  if result['steps']['prepare']:raise RuntimeError('Preparacion fallida: ver prepare.log')
  result['steps']['assemble']=command(folder,'assemble',[BLENDER,'-b','-t','2','--python',str(D/'assemble.py'),'--',task['ident']])
  if not (folder/'model.json').exists():raise RuntimeError('Montaje no produjo escena: ver assemble.log')
  result['steps']['terrain']=command(folder,'terrain',['python',str(D/'terrain.py'),task['ident']],900)
  if result['steps']['terrain']==0:
   result['steps']['add_terrain']=command(folder,'add-terrain',[BLENDER,'-b','-t','2','--python',str(D/'add_terrain.py'),'--',task['ident']])
  model=json.loads((folder/'model.json').read_text(encoding='utf-8'));assembly=json.loads((folder/'audit.json').read_text(encoding='utf-8'))
  if not model.get('terrain_included'):model['note']+=' Terreno pendiente de conversion; revisar terrain.log.'
  model['batch']='Tanda 2';model['scene_review']='Terreno incluido; vista parcial' if model.get('terrain_included') else 'Solo arquitectura; terreno pendiente'
  model['scene_audit']=dict(date='2026-10-13',source_warnings=task['source_warnings'],omitted_actors=len(assembly['missing']),terrain_in_scene=bool(model.get('terrain_included')),visual_completeness='partial',ingame_verified=False)
  model['names']+=['Escenarios descargados','Tanda escenarios 2']
  (folder/'model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8');(folder/'render.json').write_text(json.dumps({'models':[model]}),encoding='utf-8')
  result['steps']['render']=command(folder,'render',[BLENDER,'-b','-t','2','--python',str(R/'research/npc-batch2/render_batch.py'),'--','--manifest='+str(folder/'render.json')],900)
  p=G/model['gltf'];g=json.loads(p.read_text(encoding='utf-8'));assert g.get('meshes') and (G/model['thumbnail']).is_file()
  from urllib.parse import unquote
  for ref in g.get('images',[])+g.get('buffers',[]):
   uri=ref.get('uri','')
   if uri and not uri.startswith('data:'):assert (p.parent/unquote(uri)).is_file(),uri
  with lock:
   path=G/'gallery.json';catalog=json.loads(path.read_text(encoding='utf-8'));catalog['models']=[m for m in catalog['models'] if m['key']!=key]+[model];catalog['model_count']=len(catalog['models']);temp=G/'gallery-import.tmp';temp.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
  result.update(published=True,key=key,actors=len(assembly['used']),omitted=len(assembly['missing']),terrain=bool(model.get('terrain_included')),gltf_bytes=p.stat().st_size,thumbnail=model['thumbnail'])
 except Exception as e:result.update(published=False,error=str(e))
 result['terrain_retry_done']=bool(result.get('published') and result.get('steps',{}).get('terrain')!=0 and (folder/'retry-terrain.log').exists())
 (folder/'import-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('SCENE_RESULT',task['title'],'PUBLISHED',result.get('published'),'TERRAIN',result.get('terrain'),'OMITTED',result.get('omitted'),result.get('error',''),flush=True)
 return result
def main():
 print('SCENES_TO_IMPORT',len(tasks),flush=True)
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for result in ex.map(import_one,tasks):
   results.append(result);(D/'remaining-import-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 shutil.copy2(G/'gallery.json',R/'cloud-repo/research/model-catalog/gallery.json')
 print('IMPORT_COMPLETE',len(results),'PUBLISHED',sum(bool(r.get('published')) for r in results),flush=True)
if __name__=='__main__':main()
