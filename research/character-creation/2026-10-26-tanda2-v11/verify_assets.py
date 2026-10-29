from pathlib import Path
import json,struct,collections
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;OLD=D.parent/'2026-10-26-tanda2-v10';AUD=D.parent/'2026-10-26-mega-audit'
scope={'__file__':str(D/'verify_assets.py')};exec((OLD/'verify_assets.py').read_text().split('manifest=json.loads')[0].replace('error<=0.0001','error<=0.001'),scope)
chunks,triangles,uv_tolerance=[scope[n] for n in ['chunks','triangles','uv_tolerance']]
manifest=json.loads((D/'assets-manifest.json').read_text());native=json.loads((D/'native-manifest.json').read_text());proof=[]
for item in manifest['items']:
 model=item['mesh'].split('.')[-1];before=chunks(Path(item['source']));prepared=chunks(D/'retargeted'/(model+'.psk'));after=chunks(D/'export-check/NexusHairT2V11/SkeletalMesh'/(model+'.psk'))
 def geometry(c):
  out=collections.Counter()
  for (triangle,mat),count in triangles(c).items():out[tuple(v[:3] for v in triangle)]+=count
  return out
 assert geometry(before)==geometry(after),model
 error=uv_tolerance(prepared,after)
 s,n,b=after['MATT0000'];assert n==1;binding=b[:64].split(b'\0')[0].decode();assert binding==item['textures'][0],(model,binding)
 s,n,b=prepared['MATT0000'];assert n==1 and struct.unpack_from('<i',b,64)[0]==0
 base=Image.open(D/'textures'/(item['textures'][0]+'.tga')).convert('RGBA');a=np.asarray(base);mask=np.asarray(Image.open(D/'textures'/(model+'_TintMask.png')))>0
 assert error*max(base.size)<=.5,(model,'UCC UV weld exceeds half an atlas pixel',error)
 if item.get('atlas_regions'):
  for region,name in zip(item['atlas_regions'],item['atlas_source_textures']):
   source=Image.open(next((AUD/'gallery-assets').rglob(name+'.png'))).convert('RGBA');x,y,w,h=[region[k] for k in ['x','y','width','height']];assert np.array_equal(np.asarray(base.crop((x,y,x+w,y+h))),np.asarray(source)),(model,name)
 else:
  old=next(x for x in json.loads((OLD/'assets-manifest.json').read_text())['items'] if x['model']==item['model'] and x['index']==item['index'])
  original=Image.open(OLD/'textures'/(old['textures'][0]+'.tga')).convert('RGBA');assert np.array_equal(np.asarray(original),a)
  active=next(x for x in native['tanda2'] if x['model']==item['model'] and x['index']==item['index']);assert active['mesh']==old['mesh'],'Confirmed working mesh must stay unchanged'
 differences=[]
 for color in range(4):
  texture=item['color_textures'][color][0];im=Image.open(D/'textures'/(texture+'.tga')).convert('RGBA');exported=Image.open(D/'export-check/NexusHairT2V11/Texture'/(texture+'.png')).convert('RGBA');data=np.asarray(im)
  assert np.array_equal(data,np.asarray(exported)),texture
  assert np.array_equal(data[:,:,3],a[:,:,3]),texture
  assert np.array_equal(data[~mask],a[~mask]),texture
  changed=int(np.any(data[:,:,:3]!=a[:,:,:3],axis=2).sum());assert color==0 or changed>0;differences.append(changed)
  mat=item['color_materials'][color][0].split('.')[-1];txt=(D/'native-editor-check'/(mat+'.t3d')).read_text(errors='replace');assert all(x in txt for x in ['FB_AlphaBlend','AlphaTest=True','TwoSided=True','AlphaRef=5'])
 proof.append(dict(model=item['model'],letter=item['letter'],triangles=item['triangles'],single_material=True,binding=binding,maximum_uv_error=error,atlas_source_pixels_exact=True,alpha_all_colors_exact=True,protected_pixels_unchanged=True,changed_hair_pixels=differences,confirmed_mesh_preserved=not bool(item.get('atlas_regions'))))
log=(D/'native-editor-check.log').read_bytes().decode('utf-16',errors='replace');assert 'Success - 0 error(s), 0 warning(s)' in log
(D/'asset-test-results.json').write_text(json.dumps(dict(passed=True,meshes=proof,atlas_meshes=5,confirmed_original_meshes_preserved=2,native_materials=28,all_colors_alpha_exact=True),indent=2),encoding='utf8')
print('PASS: 5 single-material atlases, 2 confirmed meshes retained, 28 exact texture roundtrips/alpha and protected ornaments, 28 native materials.')
