"""Alpha in specular diffuse textures must not turn opaque shader bodies into cutouts."""
from pathlib import Path
import json,re,os
import build_gallery as build
root=Path(__file__).resolve().parent
build.texture_cache={k:v for k,v in build.texture_cache.items() if not v.get('alpha')}
report=json.loads((root/'gallery.json').read_text(encoding='utf-8'))
changed=0
for m in report['models']:
    if m.get('status')!='ready':continue
    p=root/m['gltf'];data=json.loads(p.read_text(encoding='utf-8'))
    mats=data.get('materials',[])
    if not any(mat.get('alphaMode')=='MASK' for mat in mats):continue
    text=(root/'build-logs'/(m['key']+'.log')).read_text(encoding='utf-8')
    loaded={name.lower():Path(path).stem+'.'+name for _,name,path in re.findall(r'Loading (Texture|Shader|FinalBlend|Combiner|TexPanner|TexScaler) (\S+) from package (\S+)',text)}
    overrides=m['npcs'][0].get('textures',[]) if m['npcs'] else []
    altered=False
    for i,mat in enumerate(mats):
        if mat.get('alphaMode')!='MASK':continue
        ref=overrides[i] if len(overrides)==len(mats) else loaded.get(mat.get('name','').lower())
        result=build.texture(ref) if ref else None
        if result is None:
            native=loaded.get(mat.get('name','').lower());result=build.texture(native) if native else None
        if result and not result['alpha']:
            mat.pop('alphaMode',None);mat.pop('alphaCutoff',None);altered=True
    if altered:p.write_text(json.dumps(data),encoding='utf-8');changed+=1
(root/'texture-cache.json').write_text(json.dumps(build.texture_cache,indent=2),encoding='utf-8')
print('Opaque shader correction: '+str(changed)+' models')
