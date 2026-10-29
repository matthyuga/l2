import pathlib,urllib.request,bz2,hashlib,json,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parent/'superion-assets'
BASE='https://launcher.exiliumworld.com/patch/'
def get(name):
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  with urllib.request.urlopen(BASE+name+'.bz2',timeout=60) as response:data=response.read()
  p.write_bytes(bz2.decompress(data))
 print('Downloaded',name,p.stat().st_size,flush=True)
 return dict(path=name,source=BASE+name+'.bz2',size=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':
 files=['StaticMeshes/Superion_S.usx','StaticMeshes/Superion_Du_S.usx','Textures/Superion_T.utx','Textures/Superion_Du_T.utx']
 result=list(concurrent.futures.ThreadPoolExecutor(4).map(get,files))
 (ROOT/'sources.json').write_text(json.dumps(result,indent=2))
