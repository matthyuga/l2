"""Export the actual Veilmar map's referenced meshes for isolated inspection."""
import pathlib,sys,json,hashlib,re,shutil
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/veilmar';CAT=ROOT/'research/model-catalog'
sys.path.insert(0,str(CAT));import build_gallery as b
b.OPTIONS=['-game=l2','-path='+str(D/'assets')]
original=b.run;b.run=lambda args:original([x.replace('.ukx','.usx') for x in args])
actors=json.loads((D/'actors.json').read_text());dest=D/'scene-meshes.json'
meshes=json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else {}
for ref in sorted({a['StaticMesh'] for a in actors}):
 if ref in meshes:continue
 m=dict(key='veilmar_part_'+hashlib.sha1(ref.encode()).hexdigest()[:10],mesh=ref,npcs=[])
 try:
  original_mesh=m['mesh'];pkg,obj=original_mesh.split('.',1);m['mesh']=pkg+'.'+obj.split('.')[-1]
  b.prepare(m);m['mesh']=original_mesh
  p=CAT/m['gltf'];data=json.loads(p.read_text());log=(b.LOGS/(m['key']+'.log')).read_text()
  refs={name.lower():pathlib.Path(pkg).stem+'.'+name for name,pkg in re.findall(r'Loading \w+ (\S+) from package (\S+)',log)}
  for mat in data.get('materials',[]):
   if mat.get('alphaMode')!='MASK':continue
   matref=refs.get(mat.get('name','').lower())
   if not matref:continue
   info=b.run(['-dump',*matref.split('.',1)])
   if 'ClassName: Shader' in info and 'Opacity = None' in info and 'OutputBlending = OB_Normal' in info and 'AlphaRef = 0' in info:
    mat.pop('alphaMode',None);mat.pop('alphaCutoff',None)
  p.write_text(json.dumps(data),encoding='utf-8');meshes[ref]=m
  print('PREPARED',len(meshes),ref,m['textured_materials'],m['material_count'],flush=True)
 except Exception as e:print('FAILED',ref,str(e)[-250:],flush=True)
 dest.write_text(json.dumps(meshes,indent=2),encoding='utf-8');b.cache_file.write_text(json.dumps(b.texture_cache,indent=2),encoding='utf-8')
