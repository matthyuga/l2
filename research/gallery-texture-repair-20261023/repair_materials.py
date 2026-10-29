"""Recover documented gallery materials. Never writes native packages or game data."""
from pathlib import Path
import json,copy,hashlib,os,re,collections,concurrent.futures,sys
sys.stdout.reconfigure(encoding='utf8')
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'research/model-catalog';OUT=Path(__file__).resolve().parent
BACK=ROOT/'backups/gallery-textures-20261023';BACK.mkdir(parents=True,exist_ok=True)
catalog=json.loads((R/'gallery.json').read_text(encoding='utf8'));before=copy.deepcopy(catalog)
if not (BACK/'gallery.json').exists():(BACK/'gallery.json').write_bytes((R/'gallery.json').read_bytes())
audit=json.loads((OUT/'audit-before.json').read_text(encoding='utf8'))['rows'];amap={r['gltf']:r for r in audit}
models=collections.defaultdict(list)
for m in catalog['models']:
 if m.get('status')=='ready' and m.get('gltf'):models[m['gltf']].append(m)
cache={}
def load(path):
 if path not in cache:
  try:
   b=(R/path).read_bytes()
   if b[:4]==b'glTF':return None
   cache[path]=json.loads(b.decode('utf-8-sig'))
  except Exception:return None
 return cache[path]
def texpath(g,mat,path):
 try:
  ti=mat['pbrMetallicRoughness']['baseColorTexture']['index'];t=g['textures'][ti];im=g['images'][t['source']]
  return str(((R/path).parent/im['uri']).resolve()) if im.get('uri') else None
 except Exception:return None
def signature(path):
 g=load(path)
 if g is None:return None
 h=hashlib.sha256();buffers={}
 try:
  for mesh in g.get('meshes',[]):
   for pr in mesh.get('primitives',[]):
    h.update(str(pr.get('material',-1)).encode())
    for field in ['POSITION','TEXCOORD_0','indices']:
     ai=pr.get('indices') if field=='indices' else pr.get('attributes',{}).get(field)
     if ai is None:h.update(b'missing');continue
     a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];bi=v['buffer']
     if bi not in buffers:buffers[bi]=((R/path).parent/g['buffers'][bi]['uri']).read_bytes()
     size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[a['componentType']]*{'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
     start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',size)
     h.update(json.dumps({k:a[k] for k in ['type','componentType','count']},sort_keys=True).encode())
     if stride==size:h.update(buffers[bi][start:start+size*a['count']])
     else:
      for i in range(a['count']):h.update(buffers[bi][start+i*stride:start+i*stride+size])
  return h.hexdigest()
 except Exception:return None
def clone_material(dst,src,mat,srcpath,dstpath):
 result=copy.deepcopy(mat)
 def copy_texture(index):
  texture=copy.deepcopy(src['textures'][index])
  if 'source'in texture:
   im=copy.deepcopy(src['images'][texture['source']])
   if 'bufferView'in im:raise ValueError('Embedded texture requires explicit extraction')
   if im.get('uri') and not im['uri'].startswith('data:'):
    absolute=((R/srcpath).parent/im['uri']).resolve()
    if not absolute.exists():raise ValueError('Texture absent '+str(absolute))
    im['uri']=os.path.relpath(absolute,(R/dstpath).parent).replace('\\','/')
   texture['source']=len(dst.setdefault('images',[]));dst['images'].append(im)
  if 'sampler'in texture:
   sampler=copy.deepcopy(src['samplers'][texture['sampler']]);texture['sampler']=len(dst.setdefault('samplers',[]));dst['samplers'].append(sampler)
  idx=len(dst.setdefault('textures',[]));dst['textures'].append(texture);return idx
 def walk(value,key=''):
  if isinstance(value,dict):
   if key.endswith('Texture') and 'index'in value:value['index']=copy_texture(value['index'])
   for k,v in value.items():walk(v,k)
  elif isinstance(value,list):
   for v in value:walk(v,key)
 walk(result)
 for ext in result.get('extensions',{}):
  if ext not in dst.setdefault('extensionsUsed',[]):dst['extensionsUsed'].append(ext)
 return result

# Build a compact exact-material index from the entire existing gallery.
donor_mesh=collections.defaultdict(list);donor_mat=collections.defaultdict(list)
def index_one(path):
 g=load(path)
 if not g:return []
 return [(i,mat,texpath(g,mat,path)) for i,mat in enumerate(g.get('materials',[])) if mat.get('pbrMetallicRoughness',{}).get('baseColorTexture')]
paths=list(models)
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
 for j,(path,items) in enumerate(zip(paths,ex.map(index_one,paths))):
  if items:
   m=models[path][0];donor_mesh[m['mesh'].lower()].append(path)
   for i,mat,tex in items:
    name=mat.get('name','').lower()
    if name and not name.startswith('dummy_material_') and tex:donor_mat[(m.get('package',m['mesh'].split('.')[0]).lower(),name)].append((path,i,tex))
  if j%600==0:print('INDEX',j,'/',len(paths),flush=True)

plans={}
for p in (ROOT/'research/npc-batch2/packages').glob('*/plan.json'):
 try:
  for m in json.loads(p.read_text(encoding='utf8')).get('models',[]):plans[m['key']]=m
 except Exception:pass
changes=[];unresolved=[];dirty={}
def original_backup(path):
 p=BACK/path;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():p.write_bytes((R/path).read_bytes())

for j,row in enumerate(audit):
 if not row.get('missing_slots') or row.get('authored_color_asset'):continue
 path=row['gltf'];g=load(path)
 if g is None:continue
 group=models[path];m=group[0];missing=row['missing_slots'];fixed=[]
 plan=plans.get(m['key'],{});overrides=plan.get('textures',[])
 # A variant's explicit texture overrides must not be replaced by a generic body.
 candidates=donor_mesh.get(m['mesh'].lower(),[]) if not overrides else []
 sig=None
 for srcpath in candidates:
  if srcpath==path:continue
  src=load(srcpath)
  if len(src.get('materials',[]))!=len(g.get('materials',[])):continue
  if sig is None:sig=signature(path)
  if not sig or signature(srcpath)!=sig:continue
  for slot in missing:
   donor=src['materials'][slot]
   if not texpath(src,donor,srcpath):continue
   original_backup(path);g['materials'][slot]=clone_material(g,src,donor,srcpath,path)
   fixed.append(slot);changes.append({'target':path,'slot':slot,'method':'identical_mesh_position_uv_topology','donor':srcpath,'donor_key':models[srcpath][0]['key'],'geometry_signature':sig})
  if fixed:break
 for slot in missing:
  if slot in fixed:continue
  name=g['materials'][slot].get('name','').lower();opts=donor_mat.get((m.get('package',m['mesh'].split('.')[0]).lower(),name),[])
  # Copy a named material only when its texture resolves unambiguously within
  # the same Unreal package namespace. Never use dummy names or fuzzy matches.
  if len(set(t for _,_,t in opts))!=1:continue
  srcpath,si,tex=opts[0];src=load(srcpath)
  original_backup(path);g['materials'][slot]=clone_material(g,src,src['materials'][si],srcpath,path)
  fixed.append(slot);changes.append({'target':path,'slot':slot,'method':'same_package_exact_material_unique_texture','donor':srcpath,'donor_slot':si,'material_name':name})
 if fixed:
  dirty[path]=g
  for entry in group:entry['material_repair']={'date':'2026-10-23','methods':sorted({c['method'] for c in changes if c['target']==path}),'recovered_slots':fixed,'representative':True}
 unresolved.append({'gltf':path,'key':m['key'],'missing':[i for i in missing if i not in fixed]})
 if j%200==0:print('MATCH',j,'recovered',len(changes),flush=True)

for path,g in dirty.items():(R/path).write_text(json.dumps(g,ensure_ascii=False,separators=(',',':')),encoding='utf8')
for path,entries in models.items():
 if path not in dirty:continue
 g=dirty[path];total=len(g.get('materials',[]));count=sum('baseColorTexture'in mat.get('pbrMetallicRoughness',{}) for mat in g.get('materials',[]))
 for m in entries:
  m['textured_materials']=count;m['material_count']=total
  note=m.get('note','').replace('Algunos materiales se muestran sin textura.','').strip()
  if count<total:note='Algunos materiales siguen sin textura. '+note
  m['note']=note+' Materiales recuperados de referencias compatibles; vista representativa.'
(R/'gallery.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'repair-matches.json').write_text(json.dumps({'changes':changes,'unresolved':unresolved},ensure_ascii=False,indent=2),encoding='utf8')
changed_models=[m for m in catalog['models'] if m.get('gltf')in dirty]
(OUT/'render-matches.json').write_text(json.dumps({'models':changed_models},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'changed_views':len(dirty),'changed_cards':len(changed_models),'recovered_slots':len(changes),'remaining_views':sum(bool(r['missing']) for r in unresolved),'methods':dict(collections.Counter(c['method'] for c in changes))}),flush=True)
