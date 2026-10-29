from pathlib import Path
import urllib.request,json,hashlib
root=Path(__file__).resolve().parent/'review-tests';root.mkdir(exist_ok=True)
url='https://api.github.com/gists/8a14f647661440a3333405f8e6619c0b'
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HELLGAMES-source-review'}),timeout=30) as r:d=json.load(r)
records=[]
for i,f in enumerate(d['files'].values()):
    if f.get('truncated'):raise RuntimeError('Truncated gist')
    b=f['content'].encode();p=root/('lisvus-'+str(i)+'.patch');p.write_bytes(b)
    records.append({'file':p.name,'upstream_filename':f['filename'],'url':f['raw_url'],'sha256':hashlib.sha256(b).hexdigest(),'revision':d['history'][0]['version']})
(root/'lisvus-download.json').write_text(json.dumps(records,indent=2))
print('Downloaded',len(records),'gist file(s); revision',d['history'][0]['version'])
