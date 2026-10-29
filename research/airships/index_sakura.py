"""Index remote RAR using sparse HTTP reads, without downloading a full client."""
import urllib.request,re,html,sys,pathlib,json,time
D=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(D/'python-libs'));sys.path.insert(0,str(D.parent/'resource-library'))
import rarfile
from remote_zip import Remote
with urllib.request.urlopen('https://www.mediafire.com/file/h3wq29iklsnwx2j/KEUCEREUS_Sakura_Isle.rar/file',timeout=30) as r:page=r.read().decode('utf-8',errors='replace')
url=html.unescape(re.search(r'href="(https://download[^\"]+\.rar)"',page)[1])
(D/'sakura-source-url.txt').write_text(url)
class CachedRemote(Remote):
 def __init__(self,url):super().__init__(url);self.cache=b'';self.start=-1;self.total=0;self.requests=0
 def read(self,n=-1):
  assert 0<=n<=1048576,('unbounded remote read',n)
  n=min(n,self.size-self.pos)
  if n<=0:return b''
  if self.start<=self.pos and self.pos+n<=self.start+len(self.cache):
   off=self.pos-self.start;self.pos+=n;return self.cache[off:off+n]
  count=min(max(n,8192),self.size-self.pos)
  req=urllib.request.Request(self.url,headers={'Range':f'bytes={self.pos}-{self.pos+count-1}'})
  with urllib.request.urlopen(req,timeout=30) as r:
   assert r.status==206;self.cache=r.read()
  self.start=self.pos;self.total+=len(self.cache);self.requests+=1;self.pos+=n
  if self.requests%100==0:print('INDEX',self.requests,'requests',self.total,'bytes',flush=True)
  return self.cache[:n]
r=CachedRemote(url);z=rarfile.RarFile(r)
entries=[dict(name=x.filename,size=x.file_size,compressed=x.compress_size,method=x.compress_type,flags=x.flags,header_offset=x.header_offset,header_size=x.header_size,data_offset=x.data_offset) for x in z.infolist()]
(D/'sakura-rar-index.json').write_text(json.dumps(entries,indent=2))
print('RAR_INDEX',len(entries),'size',r.size,'sparse_bytes',r.total,'solid',z.is_solid(),flush=True)
print([x for x in entries if any(s in x['name'].lower() for s in ['chaos','airfort','superion'])],flush=True)
