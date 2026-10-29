from pathlib import Path
from PIL import Image
import json,struct,collections,math
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'exports/mmd-variants-fix4-20261023'
def chunks(path):
 raw=path.read_bytes();pos=0;out={}
 while pos<len(raw):
  name,_,size,count=struct.unpack_from('<20siii',raw,pos);pos+=32;assert size>=0 and count>=0 and pos+size*count<=len(raw)
  out[name.rstrip(b'\0')]=(size,count,raw[pos:pos+size*count]);pos+=size*count
 assert pos==len(raw);return out
checks=[]
for label,pkg in [('v10','AmberMMD10'),('v14','AmberMMD14')]:
 source=chunks(OUT/label/'AmberNPC.psk');native=chunks(OUT/'native-roundtrip'/pkg/'SkeletalMesh/AmberNPC.psk')
 build=json.loads((OUT/label/'build.json').read_text())
 for name in [b'FACE0000',b'REFSKELT',b'MATT0000']:
  assert source[name][1]==native[name][1],(pkg,name,source[name][1],native[name][1])
 assert native[b'REFSKELT'][1]==76 and native[b'MATT0000'][1]==4
 def positions(c):return {tuple(round(v,3) for v in p) for p in struct.iter_unpack('<fff',c[b'PNTS0000'][2])}
 assert positions(source)==positions(native),(pkg,'native geometry coordinates changed')
 # UCC welds coincident point records while retaining separate UV wedges.
 # Compare actual oriented triangles, UVs and material assignments, not point ids.
 def triangles(c):
  points=list(struct.iter_unpack('<fff',c[b'PNTS0000'][2]));size,count,data=c[b'VTXW0000'];wedges=[]
  for i in range(count):
   point,_,u,v,mat,_,_=struct.unpack_from('<HHffBBH',data,i*size);wedges.append(tuple(round(x,4) for x in (*points[point],u,v)))
  size,count,data=c[b'FACE0000'];out=collections.Counter()
  for i in range(count):
   a,b,d,mat,_,_=struct.unpack_from('<HHHBBI',data,i*size);corners=(wedges[a],wedges[b],wedges[d]);key=min(corners,corners[1:]+corners[:1],corners[2:]+corners[:2]);out[(mat,key)]+=1
  return out
 assert triangles(source)==triangles(native),(pkg,'triangle UV/material/winding roundtrip')
 def bones(c):
  size,count,data=c[b'REFSKELT'];return [(data[i*size:i*size+64].split(b'\0')[0].decode(),struct.unpack_from('<i',data,i*size+72)[0]) for i in range(count)]
 assert bones(source)==bones(native),'skeleton names/order/parents preserved'
 size,count,data=native[b'RAWWEIGHTS'];sums=collections.defaultdict(float)
 for i in range(count):
  weight,point,bone=struct.unpack_from('<fii',data,i*size);assert 0<=point<native[b'PNTS0000'][1] and 0<=bone<76 and 0<=weight<=1.001;sums[point]+=weight
 assert len(sums)==native[b'PNTS0000'][1] and all(abs(v-1)<0.003 for v in sums.values()),'every native vertex has normalized influences'
 for path in (OUT/label/'textures').glob('*.tga'):
  exported=OUT/'native-roundtrip'/pkg/'Texture'/path.name
  a=Image.open(path).convert('RGBA');b=Image.open(exported).convert('RGBA');assert a.size==b.size and a.tobytes()==b.tobytes(),(pkg,path.name,'texture pixel roundtrip')
 checks.append(dict(package=pkg,vertices=native[b'PNTS0000'][1],triangles=native[b'FACE0000'][1],materials=4,bones=76,all_vertices_weighted_and_normalized=True,texture_pixel_roundtrip_count=6,geometry_coordinates_roundtrip=True))
 print('PASS',pkg,'native L2 export geometry,76 skeleton bones,4 materials, all vertex weights,6 textures exact')
(OUT/'asset-verification.json').write_text(json.dumps(checks,indent=2))
