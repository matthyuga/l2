"""Read selected Helios maps from a remote solid 7z; don't store whole client."""
import pathlib,sys,time,urllib.request,json
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/airships'
sys.path.insert(0,str(ROOT/'research/amber-l2/tools/python-libs'))
sys.path.insert(0,str(ROOT/'research/resource-library'))
import py7zr
from remote_zip import Remote
class BufferedRemote(Remote):
 def __init__(self,url):super().__init__(url);self.cache=b'';self.start=0;self.downloaded=0;self.last=0
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  n=min(n,self.size-self.pos)
  if n<=0:return b''
  if self.start<=self.pos and self.pos+n<=self.start+len(self.cache):
   offset=self.pos-self.start;self.pos+=n;return self.cache[offset:offset+n]
  count=min(max(n,32*1024*1024) if n>=65536 else n,self.size-self.pos)
  req=urllib.request.Request(self.url,headers={'Range':f'bytes={self.pos}-{self.pos+count-1}'})
  with urllib.request.urlopen(req,timeout=90) as r:
   assert r.status==206;self.cache=r.read()
  self.start=self.pos;self.downloaded+=len(self.cache)
  if time.monotonic()-self.last>10:print('REMOTE_MB',round(self.downloaded/1048576),'position_MB',round(self.pos/1048576),flush=True);self.last=time.monotonic()
  self.pos+=n;return self.cache[:n]
url='https://www.lineage2.org.uk/download/lineage_files/lineage_clients/Lineage%20II%20-%20Tale%20Of%20Aden%20-%20Helios.7z'
targets=['Maps/22_22.unr','Maps/22_21.unr','Maps/23_22.unr']
r=BufferedRemote(url)
with py7zr.SevenZipFile(r) as z:z.extract(path=D/'helios-maps',targets=targets)
print('MAP_EXTRACTION_COMPLETE',r.downloaded,flush=True)
(D/'helios-maps-source.json').write_text(json.dumps(dict(url=url,targets=targets,network_bytes=r.downloaded),indent=2))
