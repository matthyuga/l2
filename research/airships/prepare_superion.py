import sys,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/airships';CAT=ROOT/'research/model-catalog'
sys.path.insert(0,str(CAT));import build_gallery as b
sys.path.insert(0,str(D));from read_map import Package
b.OPTIONS=['-game=l2','-path='+str(D/'superion-assets')]
original=b.run;b.run=lambda args:original([x.replace('.ukx','.usx') for x in args])
report=json.loads((CAT/'gallery.json').read_text(encoding='utf-8'))
# Complete native mesh library, with explicit component labels (not claimed to be a complete map).
for pkg in ['Superion_S','Superion_Du_S']:
 p=Package(D/'superion-assets/StaticMeshes'/f'{pkg}.usx')
 for e in p.exports:
  if p.ref(e['cl'])!='Engine.StaticMesh':continue
  name=e['name'];key='superion_'+pkg.lower()+'_'+name.lower()
  old=next((x for x in report['models'] if x['key']==key),None)
  if old and old['textured_materials']==old['material_count']:continue
  report['models']=[x for x in report['models'] if x['key']!=key]
  title='Superion · '+('Interior · ' if pkg=='Superion_Du_S' else 'Exterior · ')+name
  m=dict(key=key,mesh=pkg+'.'+name,package=pkg,category='Personalizados',title=title,names=['Superion','Fortaleza aérea',title],npcs=[],npc_count=0,types=['Estructura'],external_source=True)
  try:
   b.prepare(m);m['note']='Componente original de Superion; no es el escenario completo. Pose y materiales representativos, sin efectos del cliente. Fuente: launcher.exiliumworld.com/patch.'
   report['models'].append(m);print('SUPERION',name,m['textured_materials'],m['material_count'],flush=True)
  except Exception as ex:print('FAILED',name,str(ex)[-200:],flush=True)
  report['model_count']=len(report['models']);(CAT/'gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
  b.cache_file.write_text(json.dumps(b.texture_cache,indent=2),encoding='utf-8')
