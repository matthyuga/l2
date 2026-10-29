from pathlib import Path
from html.parser import HTMLParser
import requests, json, re, hashlib, concurrent.futures, sys, zipfile
import gdown, py7zr, rarfile
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent
OUT=Path('E:/l2-local/descarga de assets/cabellos/2026-10-23')
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'sources').mkdir(exist_ok=True)
COLLECTION='https://maxcheaters.com/topic/240179-collection-l2-shares-updated-25072023google-drive/'
ROLO='https://maxcheaters.com/topic/240008-new-hairstyles-from-the-god-chronicle-interlude/'

class Links(HTMLParser):
 def __init__(self):super().__init__();self.href=None;self.label='';self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.label=''
 def handle_data(self,data):
  if self.href:self.label+=data
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.links.append((self.label.strip(),self.href));self.href=None

entries=[dict(id='rolo-god-hairstyles-interlude',title='New hairstyles from the GOD Chronicle (Interlude)',source=ROLO,url='https://drive.google.com/file/d/1J3EQY49v3cyyJbekfPeLKQG7RCrGHgCm/view',kind='Peinados; adaptación GoD a Interlude según el autor')]
for key,url in [('rolo',ROLO),('collection',COLLECTION)]:
 try:
  r=requests.get(url,timeout=40);r.raise_for_status();(ROOT/'sources'/f'{key}.html').write_text(r.text,encoding='utf8')
  parser=Links();parser.feed(r.text)
  if key=='collection':
   for label,link in parser.links:
    if 'drive.google.com' in link and '[Interlude]' in label and re.search(r'hair|dred|dread|cabelo',label,re.I):
     slug=re.sub('[^a-z0-9]+','-',label.lower()).strip('-')
     if not any(e['url']==link for e in entries):entries.append(dict(id=slug,title=label,source=url,url=link,kind='Cabello/accesorio visual; clasificación pendiente de revisar archivos'))
 except Exception as e:print('SOURCE ERROR',key,str(e),flush=True)
(ROOT/'candidates.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf8')
print('CANDIDATES',len(entries),flush=True)

def fetch(e):
 result=dict(e,consulted='2026-10-23',installed=False,compatibility='Interlude declarado por la publicación; sin prueba en cliente')
 dest=OUT/e['id'];dest.mkdir(exist_ok=True)
 try:
  fid=re.search(r'/d/([^/]+)',e['url']).group(1)
  existing=[p for p in dest.iterdir() if p.is_file() and p.suffix.lower() in ['.7z','.zip','.rar']]
  if existing:path=existing[0]
  else:
   got=gdown.download(id=fid,output=str(dest)+'/',quiet=True,use_cookies=False)
   if not got:raise RuntimeError('Google Drive no entregó un archivo')
   path=Path(got)
  magic=path.open('rb').read(8)
  if magic.startswith(b'7z\xbc\xaf\x27\x1c'):
   with py7zr.SevenZipFile(path) as z:
    names=z.getnames();size=sum(x.uncompressed or 0 for x in z.list());valid=z.testzip()
   integrity='7z testzip: '+('OK' if valid is None else str(valid))
   if valid is not None:raise RuntimeError(integrity)
  elif magic.startswith(b'PK'):
   with zipfile.ZipFile(path) as z:names=z.namelist();size=sum(x.file_size for x in z.infolist());valid=z.testzip()
   integrity='ZIP CRC: '+('OK' if valid is None else str(valid))
   if valid is not None:raise RuntimeError(integrity)
  elif magic.startswith(b'Rar!'):
   with rarfile.RarFile(path) as z:names=z.namelist();size=sum(x.file_size for x in z.infolist())
   integrity='RAR: cabeceras e inventario leídos; CRC de contenido pendiente'
  else:raise RuntimeError('Archivo no reconocido como ZIP, RAR o 7z: '+repr(magic))
  (dest/'inventory.txt').write_text('\n'.join(names),encoding='utf8')
  h=hashlib.file_digest(path.open('rb'),'sha256').hexdigest() if hasattr(hashlib,'file_digest') else hashlib.sha256(path.read_bytes()).hexdigest()
  result.update(status='downloaded',path=str(path),bytes=path.stat().st_size,sha256=h,files=len(names),uncompressed_bytes=size,integrity=integrity,extensions=sorted(set(Path(n).suffix.lower() for n in names if Path(n).suffix)))
 except Exception as e:result.update(status='unavailable',error=str(e))
 (dest/'source.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:result[k] for k in ['id','status','bytes','files','error'] if k in result},ensure_ascii=False),flush=True)
 return result

results=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(fetch,entries))
(ROOT/'download-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
good=[r for r in results if r['status']=='downloaded']
lines=['# Cabellos para Interlude - descarga del 23/10/2026','',f'Descargados: {len(good)} de {len(results)} candidatos. Material original guardado en `{OUT}`. No instalado en cliente ni servidor.','', 'Cada carpeta contiene procedencia e inventario. Compatibilidad anunciada, todavía no verificada en juego. Los archivos HTML en sources son copias documentales, no instrucciones a ejecutar.','', '| Paquete | Resultado | Archivos / tamaño |','|---|---|---|']
for r in results:lines.append('| '+r['title']+' | '+r['status']+' | '+(str(r.get('files','-'))+' / '+str(r.get('bytes',0))+' bytes')+' |')
lines+=['','## Fuentes','',ROLO,'',COLLECTION,'','## Pendientes','','Distinguir peinados base de accesorios equipables; revisar razas y sexos cubiertos; preparar previews; probar sobre copia del cliente con respaldo de archivos. No ejecutar programas incluidos en los paquetes.']
(ROOT/'README.md').write_text('\n'.join(lines),encoding='utf8')
print('SUMMARY',len(good),len(results),sum(r.get('bytes',0) for r in good),flush=True)
