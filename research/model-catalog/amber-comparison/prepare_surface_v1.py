"""Preview the exact installed UE2 mask data in glTF (lighting/reflections remain approximate)."""
from pathlib import Path
import json,copy,os
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parents[1]; ROOT=OUT.parents[1]
STAGE=ROOT/'research/amber-l2/exports/surface-v1'
DEST=OUT/'amber-comparison/surface-v1';DEST.mkdir(exist_ok=True)
gallery=json.loads((OUT/'gallery.json').read_text(encoding='utf-8'))
variants=json.loads((OUT/'amber-comparison/variants.json').read_text(encoding='utf-8'))
def srgb(x):return np.where(x<=.0031308,x*12.92,1.055*np.maximum(x,0)**(1/2.4)-.055)
def linear(x):return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
for key in ['amber-npc','amber-summon']:
    model=next(m for m in gallery['models'] if m['key']==key)
    source=OUT/model['gltf'];data=json.loads(source.read_text(encoding='utf-8'))
    for entries in [data.get('images',[]),data.get('buffers',[])]:
        for entry in entries:
            if 'uri' in entry:entry['uri']=os.path.relpath((source.parent/entry['uri']).resolve(),DEST).replace('\\','/')
    old=DEST/(key+'-before.gltf')
    if not old.exists():old.write_text(json.dumps(data),encoding='utf-8')
    # Always derive from the stored full-bright baseline, never compound an earlier preview.
    data=json.loads(old.read_text(encoding='utf-8'))
    for ext in ['extensionsUsed','extensionsRequired']:
        data[ext]=[e for e in data.get(ext,[]) if e!='KHR_materials_unlit']
    for i,material in enumerate(data['materials']):
        atlas='AmberBody' if i==0 else 'AmberOutfit'
        original=data['textures'][material['pbrMetallicRoughness']['baseColorTexture']['index']]['source']
        image=Image.open(DEST/data['images'][original]['uri']).convert('RGBA')
        rgba=np.asarray(image,dtype=np.float32)/255
        mask=np.asarray(Image.open(STAGE/(atlas+'LightMask.png')).getchannel('A').resize(image.size,Image.Resampling.BILINEAR),dtype=np.float32)/255
        rgb=linear(rgba[:,:,:3]);amount=mask[:,:,None]
        material.pop('extensions',None)
        indices=[]
        for suffix,color in [('Diffuse',rgb*(1-amount)),('Emissive',rgb*amount)]:
            pixels=np.empty_like(rgba);pixels[:,:,:3]=srgb(color);pixels[:,:,3]=rgba[:,:,3]
            file=DEST/(atlas+suffix+'.png');Image.fromarray(np.clip(np.rint(pixels*255),0,255).astype('uint8'),'RGBA').save(file)
            index=len(data['images']);data['images'].append({'uri':file.name})
            indices.append(len(data['textures']));data['textures'].append({'source':index,'sampler':0})
        pbr=material['pbrMetallicRoughness'];pbr['baseColorTexture']={'index':indices[0]};pbr['baseColorFactor']=[1,1,1,1]
        pbr['metallicFactor']=0;pbr['roughnessFactor']=.85
        material['emissiveTexture']={'index':indices[1]};material['emissiveFactor']=[1,1,1]
        # A glTF view cannot reproduce L2's world-space TexEnvMap. Keep this explicit.
        material['extras']={'ue2_surface_mask':atlas+'LightMask','reflection_preview':'not reproduced; see native shader audit'}
    file=DEST/(key+'-surface-v1.gltf');file.write_text(json.dumps(data),encoding='utf-8')
    model['surface_preview']=str(file.relative_to(OUT)).replace('\\','/')
    model['gltf']=model['surface_preview'];model['surface_revision']=1;model['self_illuminated']=False
    model['note']='Integración V1: máscaras de iluminación por superficie. Reflejos UE2 aproximados en el visor; comprobar ingame.'
variants['current']='amber-comparison/surface-v1/amber-summon-before.gltf'
variants['variants']['surface']='amber-comparison/surface-v1/amber-summon-surface-v1.gltf'
variants['surface_revision']=1
(OUT/'amber-comparison/variants.json').write_text(json.dumps(variants,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'gallery.json').write_text(json.dumps(gallery,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: before/after previews use native mask alpha, linear color blending and unchanged geometry/opacity.')
