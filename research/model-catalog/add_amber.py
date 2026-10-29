from pathlib import Path
import sys,json,re,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;AUDIT=OUT/'amber-comparison'
sys.path.insert(0,str(ROOT/'research/amber-l2/scripts'))
from contract_dat import Catalog
import build_gallery as build
catalog=Catalog(AUDIT/'current-npcgrp.raw','npcgrp.xml','Interlude')
gallery=json.loads((OUT/'gallery.json').read_text(encoding='utf-8'))
gallery['models']=[m for m in gallery['models'] if m.get('key') not in {'amber-npc','amber-summon'}]
audits=[]
for display,server,key,label in [(59001,902500,'amber-npc','Amber · NPC'),(59002,902501,'amber-summon','Amber · Summon')]:
    row=next(r for r in catalog.rows if r['npc_id']==display)
    refs=[r['param_texture_name'] for r in row['texture_name_items']]
    shaders=[]
    for ref in refs:
        package,obj=ref.split('.',1)
        text=build.run(['-dump','-noanim',package,obj])
        (AUDIT/(key+'-'+obj+'.txt')).write_text(text,encoding='utf-8')
        props={name:re.search(r'^\s*'+name+r' = ([^\r\n]+)',text,re.M)[1] for name in ['Diffuse','SelfIllumination','SelfIlluminationMask','Specular','SpecularityMask','OutputBlending','TwoSided','ZWrite','AlphaTest','AlphaRef']}
        shaders.append({'reference':ref,**props})
    fullbright=all(s['SelfIllumination']!='None' and s['SelfIlluminationMask']=='None' for s in shaders)
    m={'key':key,'mesh':row['mesh_name'],'package':row['mesh_name'].split('.',1)[0],'category':'Personalizados',
       'title':label,'names':[label,'Amber'],'npc_count':1,'texture_variants':1,'types':['Folk' if display==59001 else 'Pet'],
       'npcs':[{'id':server,'display_id':display,'name':label,'type':'Folk' if display==59001 else 'Pet','textures':refs}],
       'self_illuminated':fullbright}
    build.prepare(m)
    m['note']='Material actual con autoiluminación de ambos atlas. La galería aproxima ese comportamiento; el cliente L2 puede variar.'
    gallery['models'].append(m)
    path=OUT/m['gltf'];gltf=json.loads(path.read_text(encoding='utf-8'))
    triangles=sum(gltf['accessors'][primitive['indices']]['count']//3 for mesh in gltf['meshes'] for primitive in mesh['primitives'])
    from PIL import Image
    images=[{'path':image['uri'],'dimensions':list(Image.open(path.parent/image['uri']).size)} for image in gltf.get('images',[])]
    package_path=ROOT.parent/'l2/animations'/(m['package']+'.ukx')
    audits.append({'key':key,'server_id':server,'display_id':display,'mesh':m['mesh'],'triangles':triangles,
                   'bones':len(gltf.get('skins',[{'joints':[]}])[0]['joints']),'atlas_images':images,'shaders':shaders,
                   'full_self_illumination':fullbright,'package_bytes':package_path.stat().st_size,
                   'package_sha256':hashlib.sha256(package_path.read_bytes()).hexdigest()})
gallery['model_count']=len(gallery['models']);gallery['custom_models']=2
(OUT/'gallery.json').write_text(json.dumps(gallery,ensure_ascii=False,indent=2),encoding='utf-8')
build.cache_file.write_text(json.dumps(build.texture_cache,indent=2),encoding='utf-8')
(AUDIT/'audit.json').write_text(json.dumps({'installed_rows':audits},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(audits,ensure_ascii=False))
