import io, urllib.request, zipfile, json, pathlib, argparse
URL='https://www.lineage2.org.uk/download/lineage_files/lineage_clients/Lineage%20II%20-%20The%20Chaotic%20Throne%20-%20The%202nd%20Throne%20-%20Gracia%20Final.zip'
class Remote(io.RawIOBase):
 def __init__(self,url):
  self.url=url; self.pos=0
  with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=30) as r:self.size=int(r.headers['Content-Length'])
 def seek(self,o,w=0):
  self.pos=o if w==0 else self.pos+o if w==1 else self.size+o
  return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  n=self.size-self.pos if n<0 else min(n,self.size-self.pos)
  if n<=0:return b''
  req=urllib.request.Request(self.url,headers={'Range':f'bytes={self.pos}-{self.pos+n-1}'})
  with urllib.request.urlopen(req,timeout=60) as r:
   if r.status!=206:raise RuntimeError('Server ignored Range')
   b=r.read()
  self.pos+=len(b);return b
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--match',default='');a=p.parse_args()
 out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(Remote(URL)) as z:
  entries=[{'name':i.filename,'size':i.file_size,'compressed':i.compress_size} for i in z.infolist()]
  (out/'archive-index.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
  if not a.match:print(json.dumps(entries[:50],indent=2))
  else:
   for i in z.infolist():
    if a.match.lower() not in i.filename.lower():continue
    target=out/pathlib.Path(i.filename).name
    if target.exists() and target.stat().st_size==i.file_size:continue
    print('Downloading',i.filename,i.file_size,flush=True)
    target.write_bytes(z.read(i))
