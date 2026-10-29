"""Read the 16-bit native height texture and serialized terrain layers."""
import pathlib,sys,json,struct,numpy as np
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/veilmar'
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package,Reader
map_pkg=Package(D/'assets/maps/17_24.unr');terrain=next(e for e in map_pkg.exports if map_pkg.ref(e['cl'])=='Engine.TerrainInfo');props=map_pkg.props(terrain)
(D/'terrain-props.json').write_text(json.dumps(props,indent=2))
layers=[]
for key,value in props.items():
 if not key.startswith('Layers'):continue
 fake=dict(offset=value['raw_offset'],size=value['size'],flags=0,name=key)
 try:layer=map_pkg.props(fake)
 except Exception as ex:layer=dict(error=str(ex),raw=map_pkg.b[fake['offset']:fake['offset']+30].hex())
 layers.append(dict(index=len(layers),**layer))
 if 'TerrainMatrix' in layer:
  info=layer['TerrainMatrix'];mat=map_pkg.props(dict(offset=info['raw_offset'],size=info['size'],flags=0,name='matrix'))
  rows=[]
  for key in ['XPlane','YPlane','ZPlane','WPlane']:
   info=mat[key];plane=map_pkg.props(dict(offset=info['raw_offset'],size=info['size'],flags=0,name=key));rows.append([plane.get(c,0) for c in ['X','Y','Z','W']])
  layers[-1]['texture_matrix']=rows
(D/'terrain-layers.json').write_text(json.dumps(layers,indent=2));print('LAYERS',layers,flush=True)
p=Package(D/'assets/textures/Veilmar_T.utx');e=next(e for e in p.exports if p.ref(i:=p.exports.index(e)+1)==props['TerrainMap'].split('.',1)[1])
tp=p.props(e);r=Reader(p.b,p.last_props_end)
# UMaterial::Serialize Lineage2 v123/license30 from UEViewer UnMaterial2.h.
assert p.version==123 and p.license==30
r.read(4+6+12+8*128+8+12)
def string():
 n=r.compact();return r.read(abs(n)*(2 if n<0 else 1))
for _ in range(16):string()
string();mips=r.compact();assert mips>=1
skip=r.num('i');count=r.compact();raw=r.read(count);w=r.num('i');h=r.num('i');ub=r.num('B');vb=r.num('B')
assert w==tp['USize'] and h==tp['VSize'] and count==w*h*2 and ub==vb==8
height=np.frombuffer(raw,dtype='<u2').reshape(h,w)
np.save(D/'height.npy',height);Image.fromarray(height).save(D/'height16.png')
print('HEIGHT',w,h,int(height.min()),int(height.max()),'mips',mips,flush=True)
for name in ['QuadVisibilityBitmap','EdgeTurnBitmap']:
 info=props[name];rr=Reader(map_pkg.b,info['raw_offset']);n=rr.compact();assert n==2048
 data=rr.read(n*4);bits=np.unpackbits(np.frombuffer(data,dtype=np.uint8),bitorder='little').reshape(256,256)
 np.save(D/(name+'.npy'),bits);print(name,int(bits.sum()),flush=True)
