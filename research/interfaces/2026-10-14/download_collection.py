from pathlib import Path
import requests,re,html,json,concurrent.futures,base64,struct,hashlib,subprocess
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from download_public import download,OUT,ROOT
COLLECTION='https://maxcheaters.com/topic/238573-compiled-all-interfaces-interlude-shared-so-far/'
UNRAR=Path(r'C:\Program Files\WinRAR\UnRAR.exe')
def mega(entry):
 ident,url=entry
 result=dict(id=ident,title=ident,source=COLLECTION,download_page=url,consulted='2026-10-14',installed=False,compatibility='Interlude declarado; no probado')
 try:
  handle,encoded=url.split('/file/')[1].split('#')
  raw=base64.urlsafe_b64decode(encoded+'='*((-len(encoded))%4))
  key=bytes(a^b for a,b in zip(raw[:16],raw[16:]))
  response=requests.post('https://g.api.mega.co.nz/cs',params={'id':ident},json=[{'a':'g','g':1,'p':handle}],timeout=25)
  response.raise_for_status();info=response.json()[0]
  if isinstance(info,int):raise RuntimeError('MEGA API '+str(info))
  attr=base64.urlsafe_b64decode(info['at']+'='*((-len(info['at']))%4))
  decrypt=Cipher(algorithms.AES(key),modes.CBC(bytes(16))).decryptor()
  metadata=(decrypt.update(attr)+decrypt.finalize()).rstrip(b'\x00')
  assert metadata.startswith(b'MEGA')
  name=json.loads(metadata[4:])['n'];result['original_name']=name
  ext=Path(name).suffix or '.rar';target=OUT/(ident+ext);partial=target.with_suffix(ext+'.part')
  decrypt=Cipher(algorithms.AES(key),modes.CTR(raw[16:24]+bytes(8))).decryptor()
  r=requests.get(info['g'],stream=True,timeout=(20,45));r.raise_for_status();size=0;h=hashlib.sha256()
  with partial.open('wb') as f:
   for chunk in r.iter_content(1024*1024):
    if chunk:
     content=decrypt.update(chunk);f.write(content);h.update(content);size+=len(content)
   tail=decrypt.finalize();f.write(tail);h.update(tail);size+=len(tail)
  assert size==info['s']
  assert partial.open('rb').read(8).startswith((b'Rar!\x1a\x07',b'PK\x03\x04',b'7z\xbc\xaf\x27\x1c'))
  partial.replace(target);result.update(status='downloaded',path=str(target),bytes=size,sha256=h.hexdigest(),integrity='size checked; archive CRC check pending; MEGA MAC not independently checked')
 except Exception as e:result.update(status='unavailable',error=str(e))
 print(json.dumps(result,ensure_ascii=True),flush=True)
 return result
if __name__=='__main__':
 text=requests.get(COLLECTION,timeout=25).text
 links=list(dict.fromkeys(html.unescape(x) for x in re.findall(r'href=[\"\x27]([^\"\x27]+)',text) if 'mega.nz/file/' in x))
 # Each collection pair offers an installer and the same pack as an archive;
 # collect the archive once, plus the standalone Silent V2 archive.
 handles={'qAtByKzS':'celestine-mxc','yRcWTDQI':'opal-snow','HF0FyaKC':'iordanov-3.6.10','3QEGhR7R':'iordanov-full-functions','KAklgAwJ':'wellinton-v3-collection','WRlH3Kra':'essence-aikon-2.0','jAdlhY5D':'essence-sanyou','uF02XCRL':'recompiled-interface','vdsk1AKR':'iordanov-update','TA8yGDSI':'interface-compilation-2021','3YV3XCQJ':'neophron-classic','jcklHAZL':'silent-v2','yV0VBSbT':'collection-last-variant'}
 entries=[(handles[u.split('/file/')[1].split('#')[0]],u) for u in links if u.split('/file/')[1].split('#')[0] in handles]
 results=list(concurrent.futures.ThreadPoolExecutor(4).map(mega,entries))
 results.extend(concurrent.futures.ThreadPoolExecutor(2).map(download,[
  ('classic-shooter-v1.1','Classic ShooteR v1.1','https://maxcheaters.com/topic/246225-interface-classic-shooter-lineage-2-interlude/','https://www.mediafire.com/file/s30plhdny1k4vhh/'),
  ('wellinton-v3-2020','Wellinton V3 2020','https://maxcheaters.com/topic/237024-classic-interface-interlude-completed-wellinton/','https://www.mediafire.com/file/8s7ogjxn8u8xa1c/')]))
 (ROOT/'collection-manifest.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
