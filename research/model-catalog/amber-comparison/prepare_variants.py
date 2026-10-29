from pathlib import Path
import json,os
OUT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
gallery=json.loads((OUT/'gallery.json').read_text(encoding='utf-8'));source=next(m for m in gallery['models'] if m['key']=='amber-summon');p=OUT/source['gltf']
variants={}
for mode in ['diffuse','mixed']:
    data=json.loads(p.read_text(encoding='utf-8'))
    data['extensionsUsed']=[e for e in data.get('extensionsUsed',[]) if e!='KHR_materials_unlit']
    for asset in data.get('buffers',[])+data.get('images',[]):
        if 'uri' in asset:asset['uri']=os.path.relpath((p.parent/asset['uri']).resolve(),HERE).replace('\\','/')
    for mat in data['materials']:
        mat.get('extensions',{}).pop('KHR_materials_unlit',None)
        if not mat.get('extensions'):mat.pop('extensions',None)
        if mode=='mixed':
            mat['emissiveTexture']=dict(mat['pbrMetallicRoughness']['baseColorTexture'])
            mat['emissiveFactor']=[.2,.2,.2];mat['pbrMetallicRoughness']['baseColorFactor']=[.8,.8,.8,1]
    target=HERE/('Amber-'+mode+'.gltf');target.write_text(json.dumps(data),encoding='utf-8');variants[mode]=str(target.relative_to(OUT)).replace('\\','/')
reference=next(m for m in gallery['models'] if m['key']=='m0472');rp=OUT/reference['gltf'];rdata=json.loads(rp.read_text(encoding='utf-8'))
from PIL import Image
stats={'mesh':reference['mesh'],'triangles':sum(rdata['accessors'][pr['indices']]['count']//3 for mesh in rdata['meshes'] for pr in mesh['primitives']),
       'bones':len(rdata['skins'][0]['joints']),'textures':[list(Image.open(rp.parent/i['uri']).size) for i in rdata.get('images',[])]}
(HERE/'variants.json').write_text(json.dumps({'current':source['gltf'],'variants':variants,'reference':reference['gltf'],'native_reference':stats,'simulation_only':True},indent=2),encoding='utf-8')
print(json.dumps(stats))
