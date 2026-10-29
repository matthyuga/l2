from pathlib import Path
import urllib.request,hashlib,json
s=Path(__file__).resolve().parent
commit='98e351766c569504210a24d96a9f39262f19b397'
manifest=[]
for name in ('20_17.l2j','22_15.l2j'):
    url=f'https://raw.githubusercontent.com/naustagic/L2JOrion_Interlude/{commit}/L2jOrion_Geodata/geodata/{name}'
    target=s/'geodata'/name;target.parent.mkdir(exist_ok=True)
    if not target.exists():
        with urllib.request.urlopen(url,timeout=90) as response: data=response.read()
        assert len(data)>100000, 'Unexpected download'
        target.write_bytes(data)
    manifest.append({'file':name,'url':url,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(s/'geodata-sources.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
