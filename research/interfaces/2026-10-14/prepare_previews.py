from pathlib import Path
import requests,re,html,json,concurrent.futures,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'previews';OUT.mkdir(exist_ok=True)
COLLECTION='https://maxcheaters.com/topic/238573-compiled-all-interfaces-interlude-shared-so-far/'
sources=[('celestine-mxc','Celestine MxC','https://i.imgur.com/2XKTBfx.png'),('classic-ona','Classic Ona / OpalSnow','https://i.imgur.com/ANjGEre.png'),('iordanov-3.6.10','Iordanov 3.6.10','https://i.imgur.com/GSAGA5v.png'),('iordanov-full','Iordanov Full Functions','https://i.imgur.com/nyl6BtF.png'),('essence-aikon','Essence 2.0 AikoN','https://s8.gifyu.com/images/Interface-Essence-2.0.gif'),('essence-sanyou','Essence Sanyou','https://i.imgur.com/pA27t6x.png'),('iordanov-3.6.9','Iordanov 3.6.9','https://i.imgur.com/S5i5Pz7.jpg'),('dandilo','Dandilo Personal Editions','https://i.imgur.com/qEDPdvJ.jpg'),('neophron','Neophron Classic Start Edition','https://i.imgur.com/3YKIyfg.jpg')]
def fetch(item):
 ident,title,url=item;row={'id':ident,'title':title,'image_url':url,'source':COLLECTION}
 try:
  r=requests.get(url,timeout=25);r.raise_for_status()
  path=OUT/(ident+Path(url).suffix);path.write_bytes(r.content)
  with Image.open(path) as im:
   im.load();row.update(size=im.size,format=im.format)
   assert im.width>=400 and im.height>=200,'Image too small: possible removed-image placeholder'
  row.update(status='downloaded',file=path.name)
 except Exception as e:row.update(status='unavailable',error=str(e))
 return row
rows=list(concurrent.futures.ThreadPoolExecutor(6).map(fetch,sources))
archive=Path(r'E:\l2-local\descarga de assets\interfaces\2026-10-14\nexus-interlude-visual.rar')
for key,name in [('nexus-ingame','Interlude Visual patch InGame.jpg'),('nexus-login','Interlude Visual patch Main Screen.jpg')]:
 member='[NexuS]Interlude Visual Patch\\'+name
 q=subprocess.run([r'C:\Program Files\WinRAR\UnRAR.exe','p','-inul',str(archive),member],capture_output=True,timeout=30)
 assert q.returncode==0
 path=OUT/(key+'.jpg');path.write_bytes(q.stdout)
 with Image.open(path) as im:im.load();size=im.size
 rows.append({'id':key,'title':'NexuS — '+('en juego' if key.endswith('ingame') else 'login'),'source':'https://maxcheaters.com/topic/200405-new-interfaces-visual-patch-interlude-gracia-final/','status':'downloaded','file':path.name,'size':size,'origin':'Image included in downloaded archive'})
cards=[]
for row in rows:
 if row['status']=='downloaded':
  cards.append('<article><h2>'+html.escape(row['title'])+'</h2><a href="previews/'+row['file']+'" target="_blank"><img loading="lazy" src="previews/'+row['file']+'"></a><p><a href="'+html.escape(row['source'])+'">Publicación de origen</a> · '+str(row['size'][0])+' × '+str(row['size'][1])+'</p></article>')
page='''<!doctype html><html lang="es"><meta charset="utf-8"><title>Interfaces L2 — capturas</title><style>body{background:#111827;color:#eee;font:16px system-ui;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:24px}article{background:#1f2937;padding:16px;border-radius:12px}img{width:100%;height:auto}a{color:#8acbff}h2{font-size:20px}</style><h1>Interfaces L2 — capturas de referencia</h1><p>Imágenes de las publicaciones o incluidas en los archivos. No son pruebas de instalación en nuestro cliente. Pulsá una captura para verla completa.</p><main>'''+''.join(cards)+'</main></html>'
(ROOT/'GALERIA-INTERFACES.html').write_text(page,encoding='utf-8')
(ROOT/'preview-manifest.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps([{'title':r['title'],'status':r['status'],'size':r.get('size'),'error':r.get('error')} for r in rows],ensure_ascii=True))
