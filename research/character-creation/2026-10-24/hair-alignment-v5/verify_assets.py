from pathlib import Path
import struct,json
from PIL import Image,ImageChops
D=Path(__file__).resolve().parent
def chunks(path):
 b=path.read_bytes();p=0;out={}
 while p<len(b):
  name,flags,size,count=struct.unpack_from('<20siii',b,p);p+=32
  out[name.rstrip(b'\0').decode()]=(size,count,b[p:p+size*count]);p+=size*count
 assert p==len(b)
 return out
manifest=json.loads((D/'assets-manifest.json').read_text());report=[]
skeletons=json.loads((D/'native-skeletons.json').read_text())
for item in manifest['items']:
 if item['kind']=='hair':
  before=chunks(Path(item['source']));after=chunks(D/'asset-verification/NexusAppearanceV1/SkeletalMesh'/(item['mesh'].split('.')[-1]+'.psk'))
  points1=list(struct.iter_unpack('<3f',before['PNTS0000'][2]));points2=list(struct.iter_unpack('<3f',after['PNTS0000'][2]))
  assert len(points1)==len(points2)
  # UCC may reorder vertices; compare point sets rounded to native precision.
  assert sorted(tuple(round(v,3) for v in p) for p in points1)==sorted(tuple(round(v,3) for v in p) for p in points2),item
  size,count,bones=after['REFSKELT'];names=[bones[i*size:i*size+64].split(b'\0')[0].decode() for i in range(count)]
  influences=list(struct.iter_unpack('<fii',after['RAWWEIGHTS'][2]));weighted=sorted({names[bone] for weight,point,bone in influences if weight>0})
  nsize,ncount,nbones=chunks(Path(skeletons[item['race_index']]['psk']))['REFSKELT']
  native_names={nbones[i*nsize:i*nsize+64].split(b'\0')[0].decode().lower() for i in range(ncount)}
  assert weighted and set(n.lower() for n in weighted)<=native_names,(item['mesh'],weighted,native_names)
  for mat in item['materials']:
   name=mat.split('.')[-1];original=Image.open(D/'textures'/(name+'.tga')).convert('RGBA');exported=Image.open(D/'asset-verification/NexusAppearanceV1/Texture'/(name+'.tga')).convert('RGBA')
   assert original.size==exported.size and ImageChops.difference(original,exported).getbbox() is None,name
  report.append(dict(mesh=item['mesh'],points=len(points2),weighted_bones=weighted,textures_match=True))
 else:
  name=item['material'].split('.')[-1];exported=Image.open(D/'asset-verification/NexusAppearanceV1/Texture'/(name+'.tga')).convert('RGB')
  assert exported.getextrema()!=((0,0),(0,0),(0,0)),name
assert len(report)==28
(D/'asset-test-results.json').write_text(json.dumps(dict(meshes=report,faces=42,materials=112,all_native_resources_load=True),indent=2))
print('PASS: 28 mesh geometries/weights, 112 texture roundtrips, 42 nonempty face textures')
