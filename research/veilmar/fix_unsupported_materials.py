"""Use source material references to recover diffuse fallbacks UModel cannot traverse."""
import pathlib,sys,json,re,os
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/veilmar';CAT=ROOT/'research/model-catalog'
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package
sys.path.insert(0,str(CAT));import build_gallery as b
b.OPTIONS=['-game=l2','-path='+str(D/'assets')]
p=Package(D/'assets/textures/Veilmar_T.utx');lookup={p.ref(i+1).lower():e for i,e in enumerate(p.exports)};short={e['name'].lower():e for e in p.exports};audit=[]
def resolve(ref,seen=None):
 seen=set() if seen is None else seen;name=ref.split('.',1)[-1];e=lookup.get(name.lower()) or short.get(name.split('.')[-1].lower())
 if not e or e['name'] in seen:return None
 seen.add(e['name']);cls=p.ref(e['cl'])
 if cls=='Engine.Texture':return b.texture(ref)
 props=p.props(e)
 for key in ['Diffuse','Material','Material1','Material2','Texture','FallbackMaterial']:
  child=props.get(key)
  if isinstance(child,str) and child!='None':
   tex=resolve('Veilmar_T.'+child,seen)
   if tex:return tex
 return None
meshes=json.loads((D/'scene-meshes.json').read_text())
for ref,m in meshes.items():
 if m['textured_materials']==m['material_count']:continue
 path=CAT/m['gltf'];data=json.loads(path.read_text());log=(CAT/'build-logs'/(m['key']+'.log')).read_text()
 refs={name.lower():pathlib.Path(pkg).stem+'.'+name for name,pkg in re.findall(r'Loading \w+ (\S+) from package (\S+)',log)}
 for mat in data.get('materials',[]):
  if 'baseColorTexture' in mat.get('pbrMetallicRoughness',{}):continue
  original=refs.get(mat.get('name','').lower())
  if not original:continue
  try:tex=resolve(original)
  except Exception as ex:print('UNRESOLVED',original,str(ex),flush=True);continue
  if not tex:continue
  idx=len(data.setdefault('images',[]));data['images'].append(dict(uri=os.path.relpath(CAT/tex['file'],path.parent).replace('\\','/')));data.setdefault('textures',[]).append(dict(source=idx,sampler=0));data.setdefault('samplers',[dict(wrapS=10497,wrapT=10497)])
  mat['pbrMetallicRoughness']=dict(baseColorFactor=[1,1,1,1],baseColorTexture=dict(index=idx),metallicFactor=0,roughnessFactor=.9);mat['doubleSided']=True
  if tex.get('alpha'):mat['alphaMode']='MASK';mat['alphaCutoff']=.35
  audit.append(dict(mesh=ref,material=original,diffuse=tex['source'],note='Representative source diffuse, without original UV source/blend/vertex-color shader.'))
 m['textured_materials']=sum('baseColorTexture' in mat.get('pbrMetallicRoughness',{}) for mat in data.get('materials',[]));path.write_text(json.dumps(data),encoding='utf-8')
(D/'material-fallback-audit.json').write_text(json.dumps(audit,indent=2));(D/'scene-meshes.json').write_text(json.dumps(meshes,indent=2));b.cache_file.write_text(json.dumps(b.texture_cache,indent=2),encoding='utf-8');print('DIFFUSE_FALLBACKS',len(audit),flush=True)
