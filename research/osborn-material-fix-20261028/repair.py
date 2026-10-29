import pathlib,json,hashlib,shutil,sys,copy
from PIL import Image,ImageChops
ROOT=pathlib.Path(__file__).resolve().parent;CAT=ROOT.parent/'model-catalog';BACK=ROOT/'before';BACK.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT.parent/'airships'));from read_map import Package
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gallery_path=CAT/'gallery.json';gallery=json.loads(gallery_path.read_text('utf-8'));m=next(m for m in gallery['models'] if m['key']=='m0527');path=CAT/m['gltf'];g=json.loads(path.read_text('utf-8'));original=copy.deepcopy(g)
for p,name in [(path,'original.gltf'),(CAT/m['thumbnail'],'thumbnail.png'),(gallery_path,'gallery.json'),(CAT/'texture-cache.json','texture-cache.json')]:
 if not (BACK/name).exists():shutil.copy2(p,BACK/name)
package_path=pathlib.Path(r'E:\l2\systextures\LineageNpcsTex.utx');package=Package(package_path)
names=['e_patriarch_MOrc_m00_t00_b00','e_patriarch_MOrc_m00_t00_b01','e_patriarch_MOrc_sh','e_patriarch_MOrc_m00_t00_b01_or']
native=[]
for name in names:
 e=next(e for e in package.exports if e['name']==name);props=package.props(e)
 native.append({'object':name,'class':package.ref(e['cl']),'properties':props,'offset':e['offset'],'size':e['size']})
alpha_ref=package.b[native[1]['properties']['AlphaRef']['raw_offset']]
source=CAT/'exports/LineageNpcsTex/Texture/e_patriarch_MOrcc_t00_b01_sp.png';opacity=ROOT/'exports/LineageNpcsTex/Texture/e_patriarch_MOrc_m00_t00_b01_or.png'
color=Image.open(source).convert('RGBA');mask=Image.open(opacity).convert('RGBA');assert color.size==mask.size
rgb_equal=ImageChops.difference(color.convert('RGB'),mask.convert('RGB')).getbbox() is None
color.putalpha(mask.getchannel('A'));target=CAT/'exports/material-recovery-20261028/Osborn/e_patriarch_MOrc_b01_color_opacity.png';target.parent.mkdir(parents=True,exist_ok=True);color.save(target)
mat=g['materials'][1];assert mat['name']=='e_patriarch_MOrc_m00_t00_b01';image_index=g['textures'][mat['pbrMetallicRoughness']['baseColorTexture']['index']]['source']
import os
g['images'][image_index]['uri']=os.path.relpath(target,path.parent).replace('\\','/');mat['alphaMode']='MASK';mat['alphaCutoff']=alpha_ref/255
for k in ['meshes','nodes','skins','accessors','bufferViews','buffers','animations']:assert original.get(k)==g.get(k)
buffer_hashes={b['uri']:digest(path.parent/b['uri']) for b in g.get('buffers',[])}
path.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
cachepath=CAT/'texture-cache.json';cache=json.loads(cachepath.read_text('utf-8'));ref='LineageNpcsTex.e_patriarch_MOrc_m00_t00_b01'
cache[ref.lower()]={'file':target.relative_to(CAT).as_posix(),'alpha':True,'alpha_cutoff':alpha_ref/255,'source':'LineageNpcsTex.e_patriarch_MOrcc_t00_b01_sp','opacity_source':'LineageNpcsTex.e_patriarch_MOrc_m00_t00_b01_or','evidence':str(ROOT/'evidence.json')};cachepath.write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf-8')
m['material_review']={'status':'complete','text':'Material original reconstruido: color y máscara de transparencia separados; cuerpo completo','missing_slots':[]};gallery_path.write_text(json.dumps(gallery,ensure_ascii=False,indent=2),encoding='utf-8')
evidence={'key':m['key'],'mesh':m['mesh'],'native_package':str(package_path),'native_package_sha256':digest(package_path),'native_materials':native,'source_diffuse':str(source),'source_diffuse_sha256':digest(source),'source_opacity':str(opacity),'source_opacity_sha256':digest(opacity),'diffuse_opacity_RGB_identical':rgb_equal,'alpha_ref_byte':alpha_ref,'gltf_alpha_cutoff':alpha_ref/255,'composite':str(target),'composite_sha256':digest(target),'original_gltf_sha256':digest(BACK/'original.gltf'),'repaired_gltf_sha256':digest(path),'unchanged_buffers_sha256':buffer_hashes,'geometry_nodes_skins_animations_unchanged':True,'other_catalog_entries_unchanged':True}
before={v['key']:v for v in json.loads((BACK/'gallery.json').read_text('utf-8'))['models']}
assert all(v==before[v['key']] for v in gallery['models'] if v['key']!='m0527')
(ROOT/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8');print('FIXED Osborn alpha_ref',alpha_ref,'RGB same',rgb_equal,'geometry unchanged')
