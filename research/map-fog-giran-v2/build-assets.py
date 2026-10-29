from pathlib import Path
import hashlib
import json
import math
import subprocess
import struct
import xml.etree.ElementTree as ET
import zlib
import numpy as np
from PIL import Image, ImageDraw

base=Path(__file__).resolve().parent
root=base.parent.parent
out=base/'assets';out.mkdir(exist_ok=True)
size=512
minimum=(72000,136000);maximum=(96000,160000)
zonefile=root/'server/game/data/zones/custom_town.xml'
zone=next(z for z in ET.parse(zonefile).getroot().findall('zone') if z.get('name')=='Giran Castle Town')
polygon=[(int(n.get('X')),int(n.get('Y'))) for n in zone.findall('node')]
rng=np.random.default_rng(25102026)
yy,xx=np.mgrid[0:size,0:size].astype(np.float64)
cloud=np.zeros((size,size),np.float64)
weight=0
for n,amplitude in [(2,1),(4,.5),(8,.24),(16,.12),(32,.06)]:
    lattice=rng.random((n,n));gx=xx/size*n;gy=yy/size*n
    ix=np.floor(gx).astype(int);iy=np.floor(gy).astype(int)
    fx=gx-ix;fy=gy-iy;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
    cloud+=amplitude*((1-fy)*((1-fx)*lattice[iy%n,ix%n]+fx*lattice[iy%n,(ix+1)%n])+
                       fy*((1-fx)*lattice[(iy+1)%n,ix%n]+fx*lattice[(iy+1)%n,(ix+1)%n]))
    weight+=amplitude
cloud/=weight
tile=np.empty((size,size,4),np.uint8)
for c,shade in enumerate([62,72,80]):tile[:,:,c]=np.clip(shade+(cloud-.5)*48,0,255).astype(np.uint8)
tile[:,:,3]=255
Image.fromarray(tile).save(out/'CloudTile.png');Image.fromarray(tile).save(out/'CloudTile.tga')

wx=minimum[0]+(xx+.5)/size*(maximum[0]-minimum[0])
wy=minimum[1]+(yy+.5)/size*(maximum[1]-minimum[1])
inside=Image.new('L',(size,size),0)
ImageDraw.Draw(inside).polygon([((x-minimum[0])/(maximum[0]-minimum[0])*size,
                                (y-minimum[1])/(maximum[1]-minimum[1])*size) for x,y in polygon],fill=255)
inside=np.asarray(inside)>0
distance=np.full((size,size),float('inf'))
for (ax,ay),(bx,by) in zip(polygon,polygon[1:]+polygon[:1]):
    dx=bx-ax;dy=by-ay
    t=np.clip(((wx-ax)*dx+(wy-ay)*dy)/(dx*dx+dy*dy),0,1)
    distance=np.minimum(distance,np.hypot(wx-(ax+t*dx),wy-(ay+t*dy)))
# Sample the same seamless cloud field used outside the patch, in world-map coordinates.
scale=0.0050048828125
u=((wx+131072)*scale)%size;v=((wy+262144)*scale)%size
ui=np.floor(u).astype(int);vi=np.floor(v).astype(int);fu=u-ui;fv=v-vi
fog=np.empty((size,size,4),np.uint8)
for c in range(3):
    channel=tile[:,:,c].astype(float)
    sampled=(1-fv)*((1-fu)*channel[vi,ui]+fu*channel[vi,(ui+1)%size])+fv*((1-fu)*channel[(vi+1)%size,ui]+fu*channel[(vi+1)%size,(ui+1)%size])
    fog[:,:,c]=np.rint(sampled).astype(np.uint8)
rough=(cloud-.5)*650+130*np.sin(xx*.071+np.cos(yy*.043)*2)
transition=np.clip((distance-350-rough)/1400,0,1)
transition=transition*transition*(3-2*transition)
fog[:,:,3]=np.rint(transition*255).astype(np.uint8)
fog[inside,3]=0
assert np.all(fog[inside,3]==0)
assert np.all(fog[[0,-1],:,3]==255) and np.all(fog[:,[0,-1],3]==255)
assert np.any((fog[:,:,3]>0)&(fog[:,:,3]<255))
Image.fromarray(fog).save(out/'GiranClear.png');Image.fromarray(fog).save(out/'GiranClear.tga')

# Preview only: checkerboard represents the visible map, not an in-game screenshot.
check=np.zeros((size,size,4),np.uint8);check[:,:,:3]=np.where(((xx//32+yy//32)%2)[:,:,None]>0,175,205);check[:,:,3]=255
Image.alpha_composite(Image.fromarray(check),Image.fromarray(fog)).save(out/'coverage-preview.png')
metadata={'texture_size':size,'world_min':minimum,'world_max':maximum,'polygon':polygon,
          'zone_source':str(zonefile),'zone_sha256':hashlib.sha256(zonefile.read_bytes()).hexdigest(),
          'city_pixels_transparent':True,'patch_borders_opaque':True,'soft_edge':True}
(base/'assets.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')

package='NexusMapFogV2'
editor=root/'research/amber-l2/tools/l2editor/L2Editor'
classes=editor.parent/package/'Classes';classes.mkdir(parents=True,exist_ok=True)
imports='\n'.join(f'#exec TEXTURE IMPORT NAME={name} FILE="{(out/(name+".tga")).as_posix()}" MIPS=OFF ALPHATEXTURE=1' for name in ['CloudTile','GiranClear'])
(classes/'FogAssets.uc').write_text('class FogAssets extends Object;\n'+imports+'\ndefaultproperties {}\n',encoding='ascii')
(editor/(package+'.ini')).write_text((editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages='+package+'\n',encoding='latin1')
compiled=editor/(package+'.u')
if compiled.exists():compiled.unlink()
p=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini='+package+'.ini'],cwd=editor,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
(base/'ucc.log').write_bytes(p.stdout+p.stderr)
assert p.returncode==0 and compiled.exists(),p.stdout+p.stderr
build=base/'build';build.mkdir(exist_ok=True)
raw=build/(package+'.raw.u');raw.write_bytes(compiled.read_bytes())
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def crypt(*args):
    p=subprocess.run([str(codec),*map(str,args)],input=b'\n',capture_output=True,timeout=40)
    assert p.returncode==0,p.stdout+p.stderr
crypt('-c','encode','-p','121','-f',package+'.u','-o',build/(package+'.u'),raw)
crypt('-c','decode','-f',package+'.u','-o',build/'roundtrip.raw',build/(package+'.u'))
assert (build/'roundtrip.raw').read_bytes()==raw.read_bytes()
data=(build/(package+'.u')).read_bytes()
assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])
print('PASS cloud textures: city transparent, outer edges opaque, irregular feather; UCC and encrypted package roundtrip/CRC.')
