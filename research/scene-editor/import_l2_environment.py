"""Import a curated, read-only selection of native L2 environmental StaticMeshes."""
from pathlib import Path
import hashlib, importlib.util, json, os, re, subprocess

ROOT=Path(__file__).resolve().parent
LAB=ROOT.parents[1]
CAT=LAB/'research/model-catalog'
CLIENT=Path(r'D:\l2-hellgames\client\Lineage II')
UMODEL=LAB/'research/amber-l2/tools/umodel.exe'
EXPORT=CAT/'exports/l2-environment'
LOGS=ROOT/'l2-environment-logs'
EXPORT.mkdir(parents=True,exist_ok=True);LOGS.mkdir(exist_ok=True)

PACKAGES={
 'Aden_tree_S':('Árboles y vegetación',25),
 'dion_tree_s':('Árboles y vegetación',18),
 'gludio_tree_s':('Árboles y vegetación',18),
 'oren_tree_s':('Árboles y vegetación',18),
 'innadrill_tree_s':('Árboles y vegetación',18),
 'field_deco_S':('Naturaleza y rocas',24),
 'statues_s':('Estatuas y monumentos',18),
 'world_statue_s':('Estatuas y monumentos',18),
 'ruins_renewal_s':('Ruinas y estructuras',24),
 'deco01':('Decoración y estructuras',24),
}

spec=importlib.util.spec_from_file_location('gallery_builder',CAT/'build_gallery.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
builder.OPTIONS=['-game=l2','-path='+str(CLIENT)]

def run(args,timeout=180):
 p=subprocess.run([str(UMODEL),*args,'-game=l2','-path='+str(CLIENT)],capture_output=True,text=True,errors='replace',timeout=timeout)
 if p.returncode:raise RuntimeError((p.stdout+'\n'+p.stderr)[-2000:])
 return p.stdout+'\n'+p.stderr

def list_meshes(package):
 text=run(['-list',package+'.usx'])
 rows=[]
 for size,name in re.findall(r'^\s*\d+\s+[0-9A-F]+\s+([0-9A-F]+)\s+StaticMesh\s+(\S+)\s*$',text,re.M):
  rows.append((int(size,16),name))
 # Complete meshes generally coexist with tiny _A/_B LOD or material helper exports.
 complete=[r for r in rows if not re.search(r'_(?:A|B|LOD\d*)$',r[1],re.I) and r[0]>=900]
 complete.sort(key=lambda r:(-r[0],r[1].lower()))
 return complete,text

def inject_textures(gltf,loaded):
 data=json.loads(gltf.read_text(encoding='utf-8'));materials=data.get('materials',[])
 data['images']=[];data['textures']=[];data['samplers']=[{'wrapS':10497,'wrapT':10497,'magFilter':9729,'minFilter':9987}]
 assigned=0
 for material in materials:
  name=material.get('name','');ref=loaded.get(name.lower())
  texture=builder.texture(ref) if ref else None
  if not texture:continue
  image=len(data['images']);uri=os.path.relpath(CAT/texture['file'],gltf.parent).replace('\\','/')
  data['images'].append({'uri':uri});data['textures'].append({'source':image,'sampler':0})
  material['pbrMetallicRoughness']={'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':image},'metallicFactor':0,'roughnessFactor':.9}
  material['doubleSided']=True
  if texture.get('alpha'):material['alphaMode']='MASK';material['alphaCutoff']=.35
  assigned+=1
 if not data['images']:
  for key in ('images','textures','samplers'):data.pop(key,None)
 gltf.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
 return assigned,len(materials)

def main():
 gallery_path=CAT/'gallery.json';gallery=json.loads(gallery_path.read_text(encoding='utf-8'))
 old={m['key']:m for m in gallery['models']};created=[];audit=[]
 for package,(category,limit) in PACKAGES.items():
  meshes,list_log=list_meshes(package);chosen=meshes[:limit]
  (LOGS/(package+'-list.log')).write_text(list_log,encoding='utf-8')
  export_log=run(['-export','-gltf','-noanim','-out='+str(EXPORT),package+'.usx'],300)
  (LOGS/(package+'-export.log')).write_text(export_log,encoding='utf-8')
  loaded={name.lower():Path(path).stem+'.'+name for name,path in re.findall(r'Loading \w+ (\S+) from package ([^\r\n]+)',export_log)}
  for size,name in chosen:
   key='l2env_'+hashlib.sha1((package+'.'+name).lower().encode()).hexdigest()[:14]
   gltf=EXPORT/package/'StaticMesh'/(name+'.gltf')
   if not gltf.exists():continue
   assigned,total=inject_textures(gltf,loaded)
   entry={'key':key,'id':key,'mesh':package+'.'+name,'package':package,'title':name.replace('_',' '),'category':category,'names':[],'types':['StaticMesh ambiental nativo'],'gltf':str(gltf.relative_to(CAT)).replace('\\','/'),'thumbnail':'thumbs/'+key+'.png','status':'ready','textured_materials':assigned,'material_count':total,'batch':'Entorno nativo de Lineage II','native':True,'sourcePackage':package+'.usx','fileSize':size}
   old[key]=entry;created.append(entry)
  audit.append({'package':package+'.usx','available':len(meshes),'selected':len([e for e in created if e['package']==package]),'category':category})
 gallery['models']=[m for m in gallery['models'] if not m.get('key','').startswith('l2env_')]+created
 gallery['model_count']=len(gallery['models']);gallery_path.write_text(json.dumps(gallery,ensure_ascii=False,indent=2),encoding='utf-8')
 builder.cache_file.write_text(json.dumps(builder.texture_cache,indent=2),encoding='utf-8')
 (ROOT/'l2-environment-import.json').write_text(json.dumps({'assets':len(created),'packages':audit,'client':str(CLIENT),'clientModified':False},ensure_ascii=False,indent=2),encoding='utf-8')
 subprocess.run([str(LAB/'tools/python/python.exe') if (LAB/'tools/python/python.exe').exists() else 'python',str(ROOT/'build_data.py')],cwd=ROOT,check=True)
 print(json.dumps({'created':len(created),'packages':audit},ensure_ascii=False))

if __name__=='__main__':main()
