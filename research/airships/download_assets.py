import json, pathlib, urllib.request, gzip, hashlib, concurrent.futures, subprocess
ROOT=pathlib.Path(__file__).resolve().parent
d=json.loads((ROOT/'pride-manifest.json').read_text())
selected=[x for x in d['archivos'] if (x[0].lower().startswith(('staticmeshes/','textures/')) and any(s in x[0].lower() for s in ['glacia','grac_','l2_ship_l01','spirit_island_v_t','bereth_t'])) or x[0].lower() in ['animations/lineagevehicles.ukx','system/lineagevehicle.u','system/vehiclepartsgrp.dat']]
def get(x):
 name,size,sha,z,*rest=x
 out=ROOT/'gracia-assets'/name;out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists() and hashlib.sha256(out.read_bytes()).hexdigest()==sha:return name
 url=d['base']+sha[:2]+'/'+sha+('.gz' if z else '.bin')
 raw=out.with_suffix(out.suffix+'.download')
 subprocess.run(['curl.exe','-f','-sS','-L','--retry','2','--max-time','60','-e','https://l2pride.us/downloads',url,'-o',str(raw)],check=True)
 b=raw.read_bytes()
 if z:b=gzip.decompress(b)
 assert len(b)==size and hashlib.sha256(b).hexdigest()==sha,name
 out.write_bytes(b);raw.unlink();print('Verified',name,size,flush=True)
 return name
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(get,selected))
 (ROOT/'download-manifest.json').write_text(json.dumps({'source':'https://l2pride.us/downloads','manifest':'https://l2pride.us/updater/manifest.json','files':selected},indent=2))
