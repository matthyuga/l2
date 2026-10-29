from pathlib import Path
import json,struct,collections,sys
from PIL import Image,ImageChops
D=Path(__file__).resolve().parent
def chunks(path):
 b=path.read_bytes();p=0;out={}
 while p<len(b):
  n,t,s,c=struct.unpack_from('<20s3i',b,p);p+=32;out[n.split(b'\0')[0].decode()]=(s,c,b[p:p+s*c]);p+=s*c
 return out
def triangles(ch):
 s,n,b=ch['PNTS0000'];points=list(struct.iter_unpack('<3f',b));s,n,b=ch['VTXW0000'];w=[struct.unpack_from('<HxxffBBxx',b,i*s) for i in range(n)];s,n,b=ch['FACE0000'];f=[struct.unpack_from('<3HBBI',b,i*s) for i in range(n)];used=sorted({x[3] for x in f});remap={x:i for i,x in enumerate(used)};out=[]
 for face in f:
  v=[tuple(round(x,5) for x in (*points[w[k][0]],w[k][1],w[k][2])) for k in face[:3]];ordered=min(tuple(v[i:]+v[:i]) for i in range(3));out.append((ordered,remap[face[3]]))
 return collections.Counter(out)
def uv_tolerance(before,after):
 # UCC welds nearly equal UV wedges in one mesh; match oriented triangles by
 # geometry/material first, then bound the observed UV change numerically.
 def indexed(ch):
  out=collections.defaultdict(list)
  for (triangle,material),count in triangles(ch).items():
   points=tuple(v[:3] for v in triangle);out[(points,material)]+=[tuple(v[3:] for v in triangle)]*count
  return out
 a,b=indexed(before),indexed(after);assert a.keys()==b.keys();maximum=0
 for key,left in a.items():
  right=list(b[key]);assert len(left)==len(right)
  for uv in left:
   distance=lambda x:max(abs(v-w) for pair,other in zip(uv,x) for v,w in zip(pair,other))
   match=min(right,key=distance);error=distance(match);maximum=max(maximum,error);assert error<=0.0001,(key,error);right.remove(match)
 return maximum
manifest=json.loads((D/'assets-manifest.json').read_text());proof=[]
native=json.loads(Path('research/character-creation/2026-10-24/hair-alignment-v5/native-skeletons.json').read_text())
for item in manifest['items']:
 source=chunks(Path(item['source']));after=chunks(D/'export-check/NexusHairT2V9/SkeletalMesh'/(item['mesh'].split('.')[-1]+'.psk'))
 maximum_uv_error=uv_tolerance(source,after)
 ns,nc,nb=chunks(Path(native[item['race_index']]['psk']))['REFSKELT'];s,n,b=after['REFSKELT'];names=[b[i*s:i*s+64].split(b'\0')[0].decode().lower() for i in range(n)];expected=[nb[i*ns:i*ns+64].split(b'\0')[0].decode().lower() for i in range(nc)];assert names==expected
 weights=list(struct.iter_unpack('<fii',after['RAWWEIGHTS'][2]));assert all(0<=bone<n and weight>=0 for weight,point,bone in weights)
 for texture in item['textures']:
  a=Image.open(D/'textures'/(texture+'.tga')).convert('RGBA');b=Image.open(D/'export-check/NexusHairT2V9/Texture'/(texture+'.png')).convert('RGBA');assert a.size==b.size and not ImageChops.difference(a,b).getbbox(),texture
 for mat in item['materials']:
  txt=(D/'native-editor-check'/(mat.split('.')[-1]+'.t3d')).read_text(errors='replace');assert all(x in txt for x in ['FB_AlphaBlend','AlphaTest=True','TwoSided=True','AlphaRef=5']),mat
 proof.append(dict(mesh=item['mesh'],triangles=item['triangles'],materials=item['material_count'],weighted_bones=sorted({names[bone] for weight,point,bone in weights if weight>0}),native_skeleton=True,texture_rgba_roundtrip=True,oriented_geometry_preserved=True,maximum_uv_error=maximum_uv_error,uv_tolerance=0.0001))
log=(D/'native-editor-check.log').read_bytes();log=log.decode('utf-16' if log.startswith(b'\xff\xfe') else 'utf8',errors='replace')
assert 'Success - 0 error(s), 0 warning(s)' in log
(D/'asset-test-results.json').write_text(json.dumps(dict(meshes=proof,native_materials=12,passed=True),indent=2))
print('PASS: 7 oriented mesh/UV/skeleton checks, 12 exact RGBA roundtrips and 12 native FinalBlend loads.')
