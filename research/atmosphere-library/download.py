"""Resumable downloads of the atmosphere resources requested by Kevin."""
import concurrent.futures, datetime, hashlib, json, os, pathlib, re, threading, time, urllib.error, urllib.parse, urllib.request, zipfile
from discover import ROOT, SOURCES, read
LOCK=threading.Lock()
STATE={}
PROGRESS=ROOT/'progress.json'
def save(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8');temp.replace(path)
def update(key,**kw):
 with LOCK:
  STATE.setdefault(key,{}).update(kw)
  save(PROGRESS,{'updated':datetime.datetime.now().isoformat(),'items':STATE})
def fetch(job):
 key=job['path'];target=ROOT/key;target.parent.mkdir(parents=True,exist_ok=True)
 record=target.with_suffix(target.suffix+'.source.json')
 if target.exists() and record.exists():
  update(key,status='complete',bytes=target.stat().st_size);return
 part=target.with_suffix(target.suffix+'.part')
 for attempt in range(4):
  try:
   offset=part.stat().st_size if part.exists() else 0
   headers={'User-Agent':'Mozilla/5.0 L2LabAssetLibrary/1.0'}
   if offset:headers['Range']=f'bytes={offset}-'
   with urllib.request.urlopen(urllib.request.Request(job['url'],headers=headers),timeout=45) as r:
    if offset and r.status!=206:offset=0
    length=int(r.headers.get('Content-Length','0'));total=offset+length if length else job.get('size',0)
    update(key,status='downloading',bytes=offset,total=total,url=job['url'])
    last=time.monotonic()
    with part.open('ab' if offset else 'wb') as out:
     while True:
      buf=r.read(1024*1024)
      if not buf:break
      out.write(buf);offset+=len(buf)
      if time.monotonic()-last>5:update(key,bytes=offset);last=time.monotonic()
   if total and offset!=total:raise ValueError(f'Incomplete download: {offset}/{total}')
   update(key,status='verifying',bytes=offset,total=offset)
   digest=hashlib.sha256();md5=hashlib.md5()
   with part.open('rb') as f:
    for buf in iter(lambda:f.read(4*1024*1024),b''):digest.update(buf);md5.update(buf)
   if job.get('md5') and md5.hexdigest()!=job['md5']:
    part.unlink();raise ValueError('Provider MD5 mismatch')
   if target.suffix=='.zip':
    with zipfile.ZipFile(part) as z:
     bad=z.testzip()
     if bad:part.unlink();raise ValueError('ZIP CRC failed: '+bad)
     names=z.namelist()
    save(target.with_suffix('.contents.json'),names)
   part.replace(target)
   save(record,{**job,'bytes':offset,'sha256':digest.hexdigest(),'downloaded':datetime.datetime.now().isoformat(),'verification':'ZIP CRC and SHA256' if target.suffix=='.zip' else 'provider MD5 and local SHA256'})
   if target.suffix=='.zip' and job.get('extract'):
    dest=target.parent/'extracted'/target.stem;dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target) as z:
     for member in z.infolist():
      resolved=(dest/member.filename).resolve()
      if not resolved.is_relative_to(dest.resolve()):raise ValueError('Unsafe ZIP path')
     z.extractall(dest)
   update(key,status='complete',bytes=offset,total=offset)
   print('COMPLETE '+key+' '+str(offset),flush=True);return
  except urllib.error.HTTPError as e:
   if e.code==416 and part.exists():
    # A full partial file may remain if the process stopped before verification.
    # Restart this file instead of accepting an unverified server response.
    part.unlink()
   update(key,status='retrying' if attempt<3 else 'failed',error=str(e),attempt=attempt+1)
   print('ERROR '+key+' '+str(e),flush=True)
   if attempt<3:time.sleep(2*(attempt+1))
  except Exception as e:
   update(key,status='retrying' if attempt<3 else 'failed',error=str(e),attempt=attempt+1)
   print('ERROR '+key+' '+str(e),flush=True)
   if attempt<3:time.sleep(2*(attempt+1))
def links(name):return json.loads((ROOT/'sources'/f'{name}-links.json').read_text())
def build():
 jobs=[]
 for name in ['cloudy','kenney-sky','kenney-particles','kenney-smoke','spritepilot']:
  for url in links(name):
   if urllib.parse.urlsplit(url).path.endswith('.zip'):
    jobs.append({'path':name+'/'+urllib.parse.unquote(url.split('/')[-1]),'url':url,'source':SOURCES[name],'license':'CC0-1.0','extract':True})
 # Download each Sonniss archive once, excluding duplicate mirrors and torrents.
 for name in ['sonniss','sonniss-2026']:
  for url in links(name):
   if url.startswith('https://downloads.sonniss.com/') and url.endswith('.zip'):
    jobs.append({'path':'sonniss/'+urllib.parse.unquote(url.split('/')[-1]),'url':url,'source':SOURCES[name],'license':'Sonniss GDC Bundle license; sources/sonniss-license.html'})
 save(ROOT/'plan.json',jobs)
 return jobs
def main():
 old=ROOT/'progress.json'
 if old.exists():STATE.update(json.loads(old.read_text(encoding='utf8')).get('items',{}))
 jobs=build()
 print(f'Planned {len(jobs)} initial files',flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(fetch,jobs))
 print('QUEUE FINISHED',flush=True)
if __name__=='__main__':main()
