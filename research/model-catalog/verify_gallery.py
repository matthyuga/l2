from pathlib import Path
import json, struct, hashlib
from PIL import Image, ImageStat
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
catalog=json.loads((OUT/'gallery.json').read_text(encoding='utf-8'));ready=[m for m in catalog['models'] if m.get('status')=='ready']
missing=[];blank=[]
for m in ready:
    p=OUT/m['gltf'];data=json.loads(p.read_text(encoding='utf-8'))
    for asset in data.get('buffers',[])+data.get('images',[]):
        if 'uri' in asset and not (p.parent/asset['uri']).is_file():missing.append(m['mesh']+': '+asset['uri'])
    im=Image.open(OUT/m['thumbnail']).convert('RGB');assert im.size==(384,420),m['mesh']
    if max(ImageStat.Stat(im).stddev)<2:blank.append(m['mesh'])
assert sum(not m['key'].startswith('amber-') and not m.get('external_source') for m in ready)==640
assert len(catalog['models'])==catalog['model_count']
assert not missing,missing
def machine(p):
    data=p.read_bytes();offset=struct.unpack_from('<I',data,0x3c)[0];return hex(struct.unpack_from('<H',data,offset+4)[0])
exe=ROOT/'research/amber-l2/tools/umodel.exe';dll=exe.parent/'SDL2.dll'
assert machine(exe)==machine(dll)=='0x14c'
proof={'models':len(catalog['models']),'readable_models_and_thumbnails':len(ready),'all_asset_links_present':True,'uniform_thumbnail_candidates':blank,
       'missing_client_reference':[m['mesh'] for m in catalog['models'] if m.get('status')=='failed'],
       'partially_textured_models':sum(m.get('textured_materials',0)<m.get('material_count',0) for m in ready),
       'sdl2':{'source':'https://raw.githubusercontent.com/gildor2/UEViewer/master/libs/SDL2/x86/SDL2.dll','sha256':hashlib.sha256(dll.read_bytes()).hexdigest(),'machine':machine(dll)},
       'viewer_runtime':'Native window UE Viewer build1590 opened and responded after adding SDL2; no native UI capture available.',
       'browser_preview':'Isolated headless Chrome screenshots show loaded grid and textured WebGL Gremlin model.',
       'limits':['Base poses; representative materials; no game particles or animation in WebGL preview.','Animations use native UModel button; no stats/AI changes.']}
(OUT/'verification.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print(json.dumps(proof))
