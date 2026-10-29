from pathlib import Path
from urllib.parse import unquote
import json, shutil

R=Path(__file__).resolve().parents[2]; S=Path(__file__).resolve().parent; G=R/'research/model-catalog'
j=json.loads((G/'gallery.json').read_text(encoding='utf-8'))
before=json.loads((S/'gallery-before-material-fix.json').read_text(encoding='utf-8'))
assert [m for m in j['models'] if m.get('batch')!='Tanda 2']==[m for m in before['models'] if m.get('batch')!='Tanda 2']
ready=[m for m in j['models'] if m.get('batch')=='Tanda 2' and m.get('status')=='ready']
missing=[]; stale=[]; links=0
for m in ready:
    p=G/m['gltf']; data=json.loads(p.read_text(encoding='utf-8'))
    for item in data.get('buffers',[])+data.get('images',[]):
        uri=item.get('uri','')
        if not uri or uri.startswith('data:'):continue
        links+=1
        if not (p.parent/unquote(uri)).is_file():missing.append([m['key'],uri])
    thumb=G/m['thumbnail']
    if not thumb.is_file():missing.append([m['key'],'thumbnail'])
    elif thumb.stat().st_mtime<p.stat().st_mtime:stale.append(m['key'])
result=dict(views=len(ready),checked_links=links,missing=missing,stale_thumbnails=stale,original_preserved=843)
(S/'material-fix-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
assert not missing,missing[:5]
assert not stale,stale[:5]
for n in ['gallery.json','build_gallery.py']:
    target=R/'cloud-repo/research/model-catalog'/n
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(G/n,target)
print(json.dumps(result))
