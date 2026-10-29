from pathlib import Path
from PIL import Image
import math,struct
root=Path(__file__).resolve().parents[1]
assets=root/'exports/contract/combat-vfx-v10/assets'
export=root/'exports/vfx-v10-assets-final/AmberParticlesV10'
for n in ['Flame','Smoke','Glow','Area','ArrowMaterial']:
 a=Image.open(assets/(n+'.tga')).convert('RGBA')
 b=Image.open(export/'Texture'/(n+'.tga')).convert('RGBA')
 assert a.size==b.size and a.tobytes()==b.tobytes(),n
 if n!='ArrowMaterial':
  rgb=a.convert('RGB');w,h=rgb.size
  for x,y in [(x,0) for x in range(w)]+[(x,h-1) for x in range(w)]+[(0,y) for y in range(h)]+[(w-1,y) for y in range(h)]:
   assert max(rgb.getpixel((x,y)))<=1,(n,'no luminous rectangle border')
def chunks(name):
 data=(export/'StaticMesh'/(name+'.pskx')).read_bytes();off=0;result={}
 while off+32<=len(data):
  tag,_,size,count=struct.unpack_from('<20siii',data,off);off+=32
  result[tag.rstrip(b'\0')]=(size,count,data[off:off+size*count]);off+=size*count
 return result
for n,axis in [('ArrowDown',2),('ArrowUp',2),('ArrowForward',0)]:
 c=chunks(n);size,count,data=c[b'PNTS0000'];points=list(struct.iter_unpack('<fff',data))
 assert len(points)>=30,'actual three dimensional shaft, point and three fins'
 lengths=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
 assert abs(lengths[axis]-30)<.001 and max(lengths[i] for i in range(3) if i!=axis)<3.3,(n,lengths)
 assert all(lengths[i]>.1 for i in range(3)),'solid geometry rather than crossed flat silhouette'
 if n=='ArrowDown':assert abs(min(p[2] for p in points)+18)<.001
 if n=='ArrowUp':assert abs(max(p[2] for p in points)-18)<.001
 if n=='ArrowForward':assert abs(max(p[0] for p in points)-18)<.001
print('PASS: five textures preserve pixels, additive boundaries are black, three solid slender meshes preserve dimensions and trajectory orientation.')
