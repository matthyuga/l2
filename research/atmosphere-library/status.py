import collections,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
for name in ['progress','polyhaven-progress']:
 path=ROOT/(name+'.json')
 if not path.exists():print(name+': preparando');continue
 d=json.loads(path.read_text(encoding='utf8'));items=d['items'];counts=collections.Counter(v['status'] for v in items.values())
 plan=ROOT/('plan.json' if name=='progress' else 'polyhaven-plan.json')
 planned=len(json.loads(plan.read_text(encoding='utf8'))) if plan.exists() else '?'
 print(name,dict(counts),'planificados',planned,'actualizado',d['updated'])
 print('  Transferidos: %.2f GB'%(sum(v.get('bytes',0) for v in items.values())/1e9))
 for k,v in items.items():
  if v['status'] in ['failed','retrying']:print(' ',k,v.get('error'))
run=ROOT/'run.json'
if run.exists():print(run.read_text(encoding='utf8'))
print('Freesound Rain and Thunder: descarga original pendiente de inicio de sesion.')
