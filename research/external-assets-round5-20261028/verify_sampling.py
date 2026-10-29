import pathlib,json,sys,hashlib,struct
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent/'rig-database-20261028'))
from build_database import GLB,canonical,digest
baseline=GLB(ROOT/'achates-batches/00/model.glb');new=GLB(ROOT/'achates-exact-range/model.glb');static=GLB(ROOT/'achates-static-preview/model.glb')
def geometry(obj):
 g=obj.g;meshes=[]
 for m in g['meshes']:
  primitives=[]
  for p in m['primitives']:
   prim={k:v for k,v in p.items() if k not in ['attributes','indices']};prim['attributes']={k:digest(obj.accessor(v)['raw']) for k,v in p['attributes'].items()}
   if 'indices' in p:prim['indices']=digest(obj.accessor(p['indices'])['raw'])
   primitives.append(prim)
  meshes.append({'name':m.get('name'),'primitives':primitives})
 skins=[]
 for s in g.get('skins',[]):
  skin={k:v for k,v in s.items() if k!='inverseBindMatrices'}
  if 'inverseBindMatrices' in s:skin['inverseBindMatrices']=digest(obj.accessor(s['inverseBindMatrices'])['raw'])
  skins.append(skin)
 images=[digest(obj.bin[g['bufferViews'][i['bufferView']].get('byteOffset',0):g['bufferViews'][i['bufferView']].get('byteOffset',0)+g['bufferViews'][i['bufferView']]['byteLength']]) for i in g.get('images',[])]
 return {'nodes':g['nodes'],'skins':skins,'meshes':meshes,'materials':g.get('materials',[]),'textures':g.get('textures',[]),'images':images}
assert geometry(baseline)==geometry(new),'Rig/geometry/materials differ from normal export'
assert geometry(static)==geometry(new),'Rig/geometry/materials differ from static full-source export'
def channels(obj,clip):
 out={}
 for c in clip['channels']:
  s=clip['samplers'][c['sampler']];ident=(c['target']['node'],c['target']['path']);out[ident]={'input':obj.accessor(s['input'])['raw'],'output':obj.accessor(s['output'])['raw'],'interpolation':s.get('interpolation','LINEAR')}
 return out
by={a['name']:a for a in new.g['animations']};checks=[];total=0
for clip in baseline.g['animations']:
 original=channels(baseline,clip);derived=channels(new,by[clip['name']]);assert original.keys()==derived.keys(),clip['name'];exact=0;near=0;maxerror=0
 for ident,a in original.items():
  b=derived[ident];assert a['interpolation']==b['interpolation'];assert a['input']==b['input'],(clip['name'],ident,'input times changed');assert len(a['output'])==len(b['output'])
  if a['output']==b['output']:exact+=1
  else:
   av=struct.unpack('<'+'f'*(len(a['output'])//4),a['output']);bv=struct.unpack('<'+'f'*(len(b['output'])//4),b['output']);error=max(abs(x-y) for x,y in zip(av,bv));assert error<=1e-5,(clip['name'],ident,error);maxerror=max(maxerror,error);near+=1
  total+=1
 checks.append({'clip':clip['name'],'channels':len(original),'input_times_byte_identical':True,'output_channels_byte_identical':exact,'output_channels_within_1e_5':near,'max_output_absolute_error':maxerror})
assert len(new.g['animations'])==122
report={'authority':'decoded-GLB-channel-bytes','normal_export_sha256':digest(baseline.raw),'optimized_export_sha256':digest(new.raw),'static_export_sha256':digest(static.raw),'geometry_rig_materials_equal':True,'full_original_source_retained':True,'optimized_clip_count':122,'normal_export_shared_clips':len(checks),'shared_channels_checked':total,'clips':checks,'limitations':['Shared-clip comparison is against unmodified Blender export, not a complete every-frame source-FBX skin deformation test.']}
(ROOT/'sampling-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('SAMPLING_VERIFIED',len(checks),'clips',total,'channels, geometry/rig/materials identical')
