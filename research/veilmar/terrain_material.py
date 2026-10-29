"""Bake the original terrain layer textures and masks for the glTF preview."""
import pathlib,sys,json,numpy as np
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[2];D=ROOT/'research/veilmar';CAT=ROOT/'research/model-catalog'
sys.path.insert(0,str(CAT));import build_gallery as b
b.OPTIONS=['-game=l2','-path='+str(D/'assets')]
layers=json.loads((D/'terrain-layers.json').read_text());SIZE=2048
grid=(np.arange(SIZE,dtype=np.float32)+.5)/SIZE*255
gx,gy=np.meshgrid(grid,grid);wx=-98304+gx*128;wy=196608+gy*128
result=np.zeros((SIZE,SIZE,3),dtype=np.float32);audit=[]
for layer in layers:
 tex=b.texture(layer['Texture']);mask=b.texture(layer['AlphaMap'])
 assert tex and mask,layer
 rgb=np.asarray(Image.open(CAT/tex['file']).convert('RGB'),dtype=np.float32)/255
 mat=np.array(layer['texture_matrix']);u=wx*mat[0,0]+wy*mat[1,0]+mat[3,0];v=wx*mat[0,1]+wy*mat[1,1]+mat[3,1]
 xi=np.floor((u%1)*rgb.shape[1]).astype(np.int32)%rgb.shape[1];yi=np.floor((v%1)*rgb.shape[0]).astype(np.int32)%rgb.shape[0]
 sampled=rgb[yi,xi]
 alpha=np.asarray(Image.open(CAT/mask['file']).convert('RGB').resize((SIZE,SIZE),Image.Resampling.BILINEAR),dtype=np.float32)[:,:,0:1]/255
 if layer['index']==0:result=sampled
 else:result=result*(1-alpha)+sampled*alpha
 audit.append(dict(index=layer['index'],texture=tex['file'],mask=mask['file'],matrix=layer['texture_matrix']))
 print('TERRAIN_LAYER',layer['index'],layer['Texture'],flush=True)
folder=CAT/'exports/scene-veilmar';folder.mkdir(exist_ok=True)
Image.fromarray(np.clip(result*255,0,255).astype('uint8')).save(folder/'terrain-color.png')
(D/'terrain-material-audit.json').write_text(json.dumps(audit,indent=2));b.cache_file.write_text(json.dumps(b.texture_cache,indent=2),encoding='utf-8')
