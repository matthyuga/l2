from pathlib import Path
import concurrent.futures,requests,re,html,hashlib,json,time
ROOT=Path(__file__).resolve().parent
OUT=Path(r'E:\l2-local\descarga de assets\interfaces\2026-10-14')
OUT.mkdir(parents=True,exist_ok=True)
PACKS=[
 ('nexus-interlude-visual','NexuS Interlude Visual Patch','https://maxcheaters.com/topic/200405-new-interfaces-visual-patch-interlude-gracia-final/','https://www.mediafire.com/file/enfrw5d4dw7qnw0/'),
 ('atlas-v9.6-interface','L2Atlas v9.6 con interfaz (parche de servidor)','https://l2atlas.net/downloads','https://www.mediafire.com/file/r9ofizbsy5124qz/'),
 ('moon-modern-interface','L2Moon Modern Interface (parche de servidor)','https://www.l2moonserver.com/index.php?id=start_lk','https://www.mediafire.com/file/4zxb6anhvt9r1ax/'),
]
def download(pack):
 ident,title,source,url=pack
 result=dict(id=ident,title=title,source=source,download_page=url,consulted='2026-10-14',compatibility='Interlude declarado; no probado',installed=False)
 try:
  session=requests.Session()
  page=session.get(url,timeout=30);page.raise_for_status()
  links=[html.unescape(x) for x in re.findall(r'href=[\"\x27]([^\"\x27]+)',page.text)]
  direct=next(x for x in links if re.match(r'https://download\d+\.mediafire\.com/',x))
  extension='.rar' if '.rar' in direct.lower() else '.zip'
  target=OUT/(ident+extension);partial=OUT/(ident+extension+'.part')
  response=session.get(direct,stream=True,timeout=(30,60));response.raise_for_status()
  total=int(response.headers.get('Content-Length',0));h=hashlib.sha256();size=0
  with partial.open('wb') as out:
   for chunk in response.iter_content(1024*1024):
    if chunk:out.write(chunk);h.update(chunk);size+=len(chunk)
  assert not total or size==total,(size,total)
  magic=partial.open('rb').read(8)
  assert magic.startswith((b'Rar!\x1a\x07',b'PK\x03\x04',b'7z\xbc\xaf\x27\x1c')),magic
  partial.replace(target)
  result.update(status='downloaded',path=str(target),bytes=size,sha256=h.hexdigest(),magic=magic.hex())
 except Exception as e:result.update(status='unavailable',error=str(e))
 print(json.dumps(result,ensure_ascii=True),flush=True)
 return result
if __name__=='__main__':
 results=list(concurrent.futures.ThreadPoolExecutor(3).map(download,PACKS))
 (ROOT/'download-manifest.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
