"""Publish live status, then retry imports once with the corrected readers."""
from pathlib import Path
import json,time,subprocess,html,sys
R=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;G=R/'research/model-catalog';pid=int(sys.argv[1])
def live():
 tasks=json.loads((D/'remaining-tasks.json').read_text(encoding='utf-8'));rows=[]
 for task in tasks:
  folder=D/task['ident'];p=folder/'import-result.json';res={}
  if p.exists():
   try:res=json.loads(p.read_text(encoding='utf-8'))
   except ValueError:pass
  stage='Pendiente'
  for label in ['prepare','assemble','terrain','add-terrain','render']:
   if (folder/(label+'.log')).exists():stage=label
  rows.append(dict(title=task['title'],key=res.get('key'),status='Disponible' if res.get('published') else 'Revisar' if res.get('error') else stage,terrain=res.get('terrain'),omitted=res.get('omitted'),error=res.get('error')))
 data=dict(total=len(rows),available=sum(r['status']=='Disponible' for r in rows),review=sum(r['status']=='Revisar' for r in rows),rows=rows)
 tmp=G/'import-progress.tmp';tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(G/'import-progress.json')
 return data
page='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Preparación de escenarios L2</title><style>body{font:16px system-ui;background:#111a22;color:#dbe7ee;max-width:1200px;margin:30px auto;padding:20px}a{color:#edc27d}td,th{padding:10px;border-bottom:1px solid #425462;text-align:left}table{width:100%}small{display:block}</style><h1>Preparación de escenarios descargados</h1><p><a href="/?category=Escenarios">Abrir escenarios del visor</a></p><p>Vistas de inspección. Terreno incluido no certifica BSP, efectos, colisiones ni funcionamiento en el juego. Las variantes se mantienen separadas.</p><p id="summary">Cargando…</p><table><thead><tr><th>Escenario</th><th>Estado</th><th>Terreno</th><th>Actores omitidos</th></tr></thead><tbody id="rows"></tbody></table><script>async function update(){try{const r=await fetch('import-progress.json',{cache:'no-store'});const d=await r.json();document.getElementById('summary').textContent=d.available+' disponibles de '+d.total+' mapas/variantes pendientes; '+d.review+' requieren revisión.';const body=document.getElementById('rows');body.replaceChildren();for(const m of d.rows){const row=document.createElement('tr');for(const value of [m.title,m.status,m.terrain===true?'Incluido':m.terrain===false?'Pendiente':'—',m.omitted??'—']){const td=document.createElement('td');td.textContent=value;row.append(td);}if(m.key){const td=row.firstChild;td.replaceChildren();const a=document.createElement('a');a.textContent=m.title;a.href='/?model='+encodeURIComponent(m.key)+'&view=3d';td.append(a);}if(m.error){const small=document.createElement('small');small.textContent=m.error;row.children[1].append(small);}body.append(row);}}catch(e){document.getElementById('summary').textContent='No se pudo consultar el estado.'}}update();setInterval(update,10000)</script></html>'''
(G/'import-progress.html').write_text(page,encoding='utf-8')
while True:
 data=live()
 proc=subprocess.run(['powershell','-NoProfile','-Command',f'if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{exit 0}} else {{exit 1}}'],capture_output=True)
 if proc.returncode:break
 time.sleep(10)
print('INITIAL_RUN_FINISHED',data['available'],flush=True)
with (D/'remaining-retry.log').open('wb') as f:subprocess.run(['python',str(D/'import_remaining.py')],stdout=f,stderr=subprocess.STDOUT)
data=live();(D/'live-import-final.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('ALL_RUNS_FINISHED',data['available'],'OF',data['total'],'REVIEW',data['review'],flush=True)
catalog=json.loads((G/'gallery.json').read_text(encoding='utf-8'))
bykey={m['key']:m for m in catalog['models']}
for task in json.loads((D/'remaining-tasks.json').read_text(encoding='utf-8')):
 folder=D/task['ident'];result=folder/'import-result.json';model=folder/'model.json'
 if result.exists() and model.exists() and json.loads(result.read_text(encoding='utf-8')).get('published'):
  m=json.loads(model.read_text(encoding='utf-8'));bykey[m['key']]=m
catalog['models']=list(bykey.values());catalog['model_count']=len(catalog['models']);temp=G/'gallery-watch.tmp';temp.write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(G/'gallery.json')
import shutil
shutil.copy2(G/'gallery.json',R/'cloud-repo/research/model-catalog/gallery.json')
text='# Importación de escenarios descargados — resultado\n\n'+str(data['available'])+' vistas disponibles de '+str(data['total'])+' mapas/variantes únicos pendientes. '+str(data['review'])+' requieren revisión. No se instalaron en el juego. Las fichas señalan si el terreno está incluido; BSP, agua, efectos, iluminación y colisiones no se certifican por esta conversión.\n\nVer http://127.0.0.1:32280/import-progress.html . Resultados y logs en E:\\l2-local\\research\\scenario-batches.\n'
(D/'RESULTADO-IMPORTACION.md').write_text(text,encoding='utf-8')
Path(r'K:\assets descargables de l2\RESULTADO-IMPORTACION-VISOR.md').write_text(text,encoding='utf-8')
Path(r'K:\_CodexNexus\inbox\20261013-lineage2-importacion-escenarios-resultado.md').write_text(text,encoding='utf-8')
