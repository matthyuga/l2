"""Recover native height16, visibility, triangulation and original terrain layers."""
from pathlib import Path
import sys,json,subprocess,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent/(sys.argv[1] if len(sys.argv)>1 else 'r4_arena');CAT=ROOT/'research/model-catalog'
sys.path.insert(0,str(ROOT/'research/airships'));from read_map import Package,Reader
sys.path.insert(0,str(CAT));import build_gallery as b
task=json.loads((D/'task.json').read_text(encoding='utf-8')) if (D/'task.json').exists() else {}
assets=Path(task['assets']) if task else D/'assets';mp=Package(Path(task['mapfile']) if task else next(assets.rglob('*.unr')));te=next(e for e in mp.exports if mp.ref(e['cl'])=='Engine.TerrainInfo');props=mp.props(te)
(D/'terrain-props.json').write_text(json.dumps(props,indent=2))
layers=[]
for key,value in props.items():
 if not key.startswith('Layers'):continue
 layer=mp.props(dict(offset=value['raw_offset'],size=value['size'],flags=0,name=key));layer['index']=len(layers)
 if 'TerrainMatrix' in layer:
  v=layer['TerrainMatrix'];matrix=mp.props(dict(offset=v['raw_offset'],size=v['size'],flags=0,name='matrix'));rows=[]
  for key in ['XPlane','YPlane','ZPlane','WPlane']:
   v=matrix[key];plane=mp.props(dict(offset=v['raw_offset'],size=v['size'],flags=0,name=key));rows.append([plane.get(c,0) for c in ['X','Y','Z','W']])
  layer['texture_matrix']=rows
 layers.append(layer)
(D/'terrain-layers.json').write_text(json.dumps(layers,indent=2))
heightref=props['TerrainMap'];pkg,ref=heightref.split('.',1)
if any(mp.ref(i+1)==heightref for i in range(len(mp.exports))):tp=mp;ref=heightref
else:tp=Package(next(p for p in assets.rglob('*.utx') if p.stem.lower()==pkg.lower()))
e=next(e for i,e in enumerate(tp.exports) if tp.ref(i+1)==ref);texprops=tp.props(e);r=Reader(tp.b,tp.last_props_end)
print('HEIGHT_PACKAGE',tp.version,tp.license,texprops.get('USize'),texprops.get('VSize'),flush=True)
# Locate the native height16 mip by its validated byte count and dimensions.
# This avoids assuming one shader header layout across client chronicles.
expected_w=texprops['USize'];expected_h=texprops['VSize'];expected_count=expected_w*expected_h*2
payload_start=r.p;payload_end=e['offset']+e['size'];found=None
for offset in range(payload_start,min(payload_start+8192,payload_end)):
 try:
  probe=Reader(tp.b,offset);count=probe.compact()
  if count!=expected_count:continue
  raw_start=probe.p;tail=Reader(tp.b,raw_start+count);w=tail.num('i');h=tail.num('i');ub=tail.num('B');vb=tail.num('B')
  if w==expected_w and h==expected_h and w==h==256 and ub==vb==8 and tail.p<=payload_end:
   found=(tp.b[raw_start:raw_start+count],w,h);break
 except (AssertionError,IndexError):continue
assert found is not None,'No validated height16 mip found'
raw,w,h=found
height=np.frombuffer(raw,dtype='<u2').reshape(h,w);np.save(D/'height.npy',height)
for name in ['QuadVisibilityBitmap','EdgeTurnBitmap']:
 v=props[name];rr=Reader(mp.b,v['raw_offset']);n=rr.compact();assert n==2048;bits=np.unpackbits(np.frombuffer(rr.read(n*4),dtype=np.uint8),bitorder='little').reshape(256,256);np.save(D/(name+'.npy'),bits)
b.EXPORT=CAT/'exports/scenario-parts'/D.name;b.LOGS=D/'logs';b.texture_cache={};b.OPTIONS=['-game=l2','-path='+str(assets)]
index={p.stem.lower():p for p in assets.rglob('*') if p.suffix.lower() in ['.utx','.usx','.ukx']}
native=json.loads((ROOT/'research/npc-batch2/native-package-index.json').read_text(encoding='utf-8'))
def run(args):
 args=list(args);i=next(i for i,a in enumerate(args) if not a.startswith('-'));pkg=args[i];target=index.get(pkg.lower());path=assets
 if target:args[i]=str(target)
 elif pkg.lower() in native:args[i]=native[pkg.lower()];path=ROOT.parent/'l2'
 r=subprocess.run([str(b.UMODEL),*args,'-game=l2','-path='+str(path)],capture_output=True,text=True,errors='replace',timeout=60)
 if r.returncode:raise RuntimeError(r.stdout[-500:])
 return r.stdout+'\n'+r.stderr
original_run=run
def run_with_internal(args):
 args=list(args);i=next(i for i,a in enumerate(args) if not a.startswith('-'))
 if i+1<len(args):
  ref=args[i]+'.'+args[i+1]
  if any(mp.ref(n+1).lower()==ref.lower() for n in range(len(mp.exports))):args[i]=str(mp.path);args[i+1]=ref
 return original_run(args)
b.run=run_with_internal
SIZE=2048;grid=(np.arange(SIZE,dtype=np.float32)+.5)/SIZE*255;gx,gy=np.meshgrid(grid,grid);wx=(props['MapX']-20)*32768+gx*props['TerrainScale'][0];wy=(props['MapY']-18)*32768+gy*props['TerrainScale'][1];result=np.zeros((SIZE,SIZE,3),dtype=np.float32);audit=[]
for layer in layers:
 if layer.get('Texture')=='None' and layer.get('AlphaMap')=='None':continue
 tex=b.texture(layer['Texture']);mask=b.texture(layer['AlphaMap']);assert tex and mask,layer
 rgb=np.asarray(Image.open(CAT/tex['file']).convert('RGB'),dtype=np.float32)/255;mat=np.array(layer['texture_matrix']);u=wx*mat[0,0]+wy*mat[1,0]+mat[3,0];v=wx*mat[0,1]+wy*mat[1,1]+mat[3,1];xi=np.floor((u%1)*rgb.shape[1]).astype(np.int32)%rgb.shape[1];yi=np.floor((v%1)*rgb.shape[0]).astype(np.int32)%rgb.shape[0];sampled=rgb[yi,xi]
 alpha=np.asarray(Image.open(CAT/mask['file']).convert('RGB').resize((SIZE,SIZE),Image.Resampling.BILINEAR),dtype=np.float32)[:,:,0:1]/255
 result=sampled if layer['index']==0 else result*(1-alpha)+sampled*alpha
 audit.append(dict(index=layer['index'],texture=tex['file'],mask=mask['file']));print('LAYER',layer['index'],layer['Texture'],flush=True)
Image.fromarray(np.clip(result*255,0,255).astype('uint8')).save(D/'terrain-color.png');(D/'terrain-audit.json').write_text(json.dumps(dict(layers=audit,dimensions=[w,h],height_min=int(height.min()),height_max=int(height.max())),indent=2))
