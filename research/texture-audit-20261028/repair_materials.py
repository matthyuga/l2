"""Material-only GLB revisions. Original BIN prefix and all non-material data stay intact."""
import pathlib,json,struct,hashlib,re,io,copy,sqlite3,datetime,shutil,sys
from PIL import Image,ImageChops
ROOT=pathlib.Path(__file__).resolve().parent
CAT=pathlib.Path(r'E:\l2-local\research\model-catalog')
sha=lambda b:hashlib.sha256(b).hexdigest()
def norm(s):return re.sub(r'[\W_]','',s.casefold())
def basename(s):return s.replace('\\','/').split('/')[-1]
def read(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);off=20+n;return g,b[off+8:]
def write(p,g,b):
 g['buffers'][0]['byteLength']=len(b);j=json.dumps(g,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*(-len(j)%4);b+=b'\0'*(-len(b)%4)
 p.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b)
def immutable(g):
 g=copy.deepcopy(g)
 for key in ['materials','images','textures','samplers','buffers','bufferViews']:g.pop(key,None)
 for mesh in g.get('meshes',[]):
  for prim in mesh['primitives']:prim.pop('material',None)
 return g
def resolve(name,files):
 target=norm(pathlib.Path(basename(name)).stem)
 found=[p for p in files if norm(p.stem)==target or norm(p.stem)==target+'tga']
 if not found:
  def semantic(s):
   s=norm(s)
   for alias,canonical in [('basecolour','albedo'),('basecolor','albedo'),('emission','emissive'),('alpha','opacity')]:s=s.replace(alias,canonical)
   return s
  found=[p for p in files if semantic(p.stem)==semantic(pathlib.Path(basename(name)).stem)]
 return found[0] if found else None
def imagebytes(p):
 im=Image.open(p);im.load();return im.convert('RGBA')
def run():
 gallery=json.loads((CAT/'gallery.json').read_text('utf-8'));by={m['key']:m for m in gallery['models']};records=[]
 selected=next((a.split('=',1)[1].split(',') for a in sys.argv if a.startswith('--keys=')),None)
 for row in json.loads((ROOT/'jobs.json').read_text('utf-8')):
  if selected and row['key'] not in selected:continue
  key=row['key'];m=by[key];path=CAT/m['gltf']
  baseline=ROOT/'before'/key/'model.glb'
  g,oldbin=read(baseline if baseline.exists() else path);original=copy.deepcopy(g);binary=bytearray(oldbin);files=[pathlib.Path(row['root'])/f for f in row['files']];source=json.loads((ROOT/'sources'/(key+'.json')).read_text('utf-8'));changes=[];unresolved=[];cache={}
  def texture(im,label):
   out=io.BytesIO();im.save(out,format='PNG');data=out.getvalue();digest=sha(data)
   if digest in cache:return cache[digest]
   binary.extend(b'\0'*(-len(binary)%4));offset=len(binary);binary.extend(data)
   views=g.setdefault('bufferViews',[]);view=len(views);views.append({'buffer':0,'byteOffset':offset,'byteLength':len(data)})
   imgs=g.setdefault('images',[]);ii=len(imgs);imgs.append({'name':label,'bufferView':view,'mimeType':'image/png'})
   ts=g.setdefault('textures',[]);ti=len(ts);ts.append({'source':ii});cache[digest]={'index':ti};return cache[digest]
  mats=g.setdefault('materials',[])
  if not mats and key=='ext3_d346aea0f43e05':
   mats.append({'name':'DefaultMaterial','pbrMetallicRoughness':{}})
   for mesh in g['meshes']:
    for prim in mesh['primitives']:prim['material']=0
  for mi,mat in enumerate(mats):
   name=mat.get('name','');sn=next((s for s in source.get('materials',[]) if s['name']==name),{});slots={};evidence={}
   for slot,details in sn.get('slots',{}).items():
    imgs=details.get('images',[])
    if len(imgs)==1:
     info=source['images'][imgs[0]];p=resolve(info['filepath'],files)
     if not p and info.get('packed_path'):p=pathlib.Path(info['packed_path'])
     if p:slots[slot]=p;evidence[slot]='source-reference'
     else:unresolved.append({'material':name,'slot':slot,'reference':info['filepath']})
   # Recover omitted FBX connections only for a unique material-prefixed map.
   prefix='DefaultMaterial' if key=='ext3_cdaea01fbc1830' and name=='base' else re.sub(r'\.\d{3}$','',name)
   patterns={'Base Color':['basecolor','albedo','diffuse','diff','color','col','d'],'Normal':['normalopengl','normal','nml','n'],'Roughness':['roughness'],'Metallic':['metallic'],'Emission Color':['emissive','emission','e'],'AO':['mixedao','ao'],'Alpha':['opacity','alpha']}
   for slot,suffixes in patterns.items():
    if slot in slots:continue
    matches=[p for p in files if any(norm(p.stem)==norm(prefix+s) for s in suffixes)]
    if matches:slots[slot]=matches[0];evidence[slot]='unique-material-map-name'
   # The package provides one named diffuse atlas for all seven authored diffuse slots.
   # This mapping is an explicit candidate until visual review, not an authored path.
   if key=='ext3_d2e535fbed12ff':
    for slot,filename in [('Base Color','Zeromus_d.png'),('Normal','Zeromus_n.png'),('Emission Color','Zeromus_e.png')]:
     p=resolve(filename,files)
     if p:slots[slot]=p;evidence[slot]='single-package-atlas-candidate'
    m['preview_review']={'status':'partial','text':'Atlas único del paquete reconectado a las siete piezas. La correspondencia UV requiere revisión visual; las rutas originales no identificaban los archivos.'}
   if key=='ext3_1b503079fd52f4' and name in ['SKIN','HAIR']:
    slots['Base Color']=resolve('COLOR.png' if name=='SKIN' else 'COLOR2.png',files);evidence['Base Color']='visual-body-hair-atlas-candidate'
    m['preview_review']={'status':'partial','text':'Atlas de cuerpo y cabello asignados por contenido visual. Revisar los materiales auxiliares y las transparencias.'}
   if key=='ext3_e101d68bf367ad':
    slots['Base Color']=resolve('model1.BMP',files);evidence['Base Color']='paired-OBJ-BMP-basename-after-CRC-verified-RAR-extraction'
   if key=='ext3_b531b47f902dcf':
    aliases={'window_1':'window_001','door_1':'door_001','board_1':'boards_001','board_2':'boards_002','board_3':'boards_003','board_4':'boards_004','roof':'roof_001','roof_2':'roof_002','brick_1':'brick_001','brus_02':'brus_002','brus_03':'brus_003'}
    if name in aliases:
     for slot,suffix in [('Base Color',''),('Normal','_normal')]:
      p=resolve(aliases[name]+suffix+'.png',files)
      if p:slots[slot]=p;evidence[slot]='material-part-name-correspondence'
     m['preview_review']={'status':'partial','text':'Texturas recuperadas por nombres de piezas. Algunos materiales del archivo antiguo siguen incompletos; revisar correspondencia visual.'}
   unresolved[:]=[u for u in unresolved if u['material']!=name or u['slot'] not in slots]
   pbr=mat.setdefault('pbrMetallicRoughness',{})
   def record(slot,paths):changes.append({'material':name,'slot':slot,'files':[{'path':str(p),'sha256':sha(p.read_bytes())} for p in paths],'authority':evidence.get(slot,'source-map-combination')})
   if 'Base Color' in slots:
    im=imagebytes(slots['Base Color'])
    if 'Alpha' in slots:
     alpha=imagebytes(slots['Alpha']).convert('L').resize(im.size);im.putalpha(alpha);mat['alphaMode']='MASK';mat['alphaCutoff']=0.5
    pbr['baseColorTexture']=texture(im,name+' color');pbr['baseColorFactor']=[1,1,1,1];record('Base Color',[slots['Base Color']]+([slots['Alpha']] if 'Alpha' in slots else []))
   if 'Normal' in slots:mat['normalTexture']=texture(imagebytes(slots['Normal']),name+' normal');record('Normal',[slots['Normal']])
   if 'AO' in slots:mat['occlusionTexture']=texture(imagebytes(slots['AO']),name+' AO');record('AO',[slots['AO']])
   if 'Emission Color' in slots:mat['emissiveTexture']=texture(imagebytes(slots['Emission Color']),name+' emission');mat['emissiveFactor']=[1,1,1];record('Emission Color',[slots['Emission Color']])
   if 'Metallic' in slots or 'Roughness' in slots:
    size=imagebytes(next(slots[s] for s in ['Metallic','Roughness'] if s in slots)).size
    channel=lambda s,default:imagebytes(slots[s]).convert('L').resize(size) if s in slots else Image.new('L',size,round(default*255))
    im=Image.merge('RGB',(Image.new('L',size,255),channel('Roughness',pbr.get('roughnessFactor',.5)),channel('Metallic',pbr.get('metallicFactor',0))))
    pbr['metallicRoughnessTexture']=texture(im,name+' metallic roughness');pbr['metallicFactor']=1;pbr['roughnessFactor']=1;record('Metallic/Roughness',[slots[s] for s in ['Metallic','Roughness'] if s in slots])
  if changes:
   assert immutable(g)==immutable(original)
   assert g.get('bufferViews',[])[:len(original.get('bufferViews',[]))]==original.get('bufferViews',[])
   backup=ROOT/'before'/key;backup.mkdir(parents=True,exist_ok=True)
   for filename in ['model.glb','analysis.json','thumbnail.png']:
    if not (backup/filename).exists():shutil.copy2(path.with_name(filename),backup/filename)
   before=sha((backup/'model.glb').read_bytes());write(path,g,bytes(binary));afterg,afterbin=read(path)
   assert immutable(afterg)==immutable(original) and afterbin[:len(oldbin)]==oldbin
   rec={'key':key,'title':m['title'],'before_sha256':before,'after_sha256':sha(path.read_bytes()),'original_bin_sha256':sha(oldbin),'immutable_json_sha256':sha(json.dumps(immutable(original),sort_keys=True).encode()),'geometry_rig_animation_unchanged':True,'changes':changes,'unresolved_source_slots':unresolved,'backup':str(backup)};records.append(rec)
   # Remove only source warnings whose corresponding image was actually recovered.
   unresolved_names={basename(v['reference']) for v in unresolved};hasbase=sum('baseColorTexture' in ma.get('pbrMetallicRoughness',{}) for ma in mats)
   previous=m.get('material_review',{}).get('status')
   recovered={norm(pathlib.Path(f['path']).stem) for c in changes for f in c['files']}
   for oldref in m.get('material_review',{}).get('missing_slots',[]):
    p=resolve(oldref,files)
    if not p or norm(p.stem) not in recovered:unresolved_names.add(oldref)
   status='pending' if unresolved_names else 'complete' if hasbase==len(mats) else previous
   m['material_review']={'status':status,'text':'Texturas reconectadas; quedan referencias ausentes o ambiguas' if status=='pending' else 'Texturas reconectadas y archivos de imagen verificados','missing_slots':sorted(unresolved_names),'audit_path':'../texture-audit-20261028/REVISION.md'}
   m['textured_materials']=sum(bool(ma.get('pbrMetallicRoughness',{}).get('baseColorTexture') or ma.get('normalTexture')) for ma in mats);m['asset_analysis']['images']=len(g.get('images',[]));m['asset_analysis']['missing_images']=sorted(unresolved_names)
   a=json.loads(path.with_name('analysis.json').read_text('utf-8'));a['texture_revision']=rec;path.with_name('analysis.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
   print(key,len(changes),status,flush=True)
 if selected and (ROOT/'revisions.json').exists():records=[r for r in json.loads((ROOT/'revisions.json').read_text('utf-8')) if r['key'] not in selected]+records
 (ROOT/'revisions.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');(CAT/'gallery.json').write_text(json.dumps(gallery,ensure_ascii=False,indent=2),encoding='utf-8')
 return records
if __name__=='__main__':run()
