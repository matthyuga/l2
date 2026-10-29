from pathlib import Path
import subprocess,struct,zlib,json
from PIL import Image
base=Path(__file__).resolve().parent;root=base.parent.parent
build=base/'build';build.mkdir(exist_ok=True)
old=base.parent/'map-fog-giran-v2/assets'
colors=Image.open(old/'CloudTile.png').convert('RGBA').resize((64,64),Image.Resampling.BILINEAR)
alpha=Image.open(old/'GiranClear.png').convert('RGBA').getchannel('A')
field=b'NXFOG4\0\0'+colors.tobytes('raw','BGRA')+alpha.tobytes()
(build/'NexusFogFieldV4.bin').write_bytes(field)
marker=[0xff214365,0xffa31572,0xff7832c1,0xff09b4e2,0xffa1c307,0xff4421d7,0xffc35b19,0xff73a28d]
im=Image.new('RGBA',(16,16),(62,72,80,255))
for x,c in enumerate(marker):im.putpixel((x,0),((c>>16)&255,(c>>8)&255,c&255,(c>>24)&255))
im.putpixel((15,15),(62,72,80,254));im.save(build/'Overlay.tga')
editor=root/'research/amber-l2/tools/l2editor/L2Editor';package='NexusMapFogV4'
classes=editor.parent/package/'Classes';classes.mkdir(parents=True,exist_ok=True)
(classes/'Assets.uc').write_text('class Assets extends Object;\n#exec TEXTURE IMPORT NAME=Overlay FILE="'+(build/'Overlay.tga').as_posix()+'" MIPS=OFF ALPHATEXTURE=1\ndefaultproperties {}\n',encoding='ascii')
(editor/(package+'.ini')).write_text((editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages='+package+'\n',encoding='latin1')
target=editor/(package+'.u')
if target.exists():target.unlink()
p=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini='+package+'.ini'],cwd=editor,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
(build/'ucc.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0 and target.exists()
raw=build/(package+'.raw.u');raw.write_bytes(target.read_bytes())
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def crypt(*args):
 p=subprocess.run([str(codec),*map(str,args)],input=b'\n',capture_output=True,timeout=30);assert p.returncode==0
crypt('-c','encode','-p','121','-f',package+'.u','-o',build/(package+'.u'),raw)
crypt('-c','decode','-f',package+'.u','-o',build/'roundtrip.raw',build/(package+'.u'))
assert (build/'roundtrip.raw').read_bytes()==raw.read_bytes()
data=(build/(package+'.u')).read_bytes();assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])
print('PASS V4 marker assets and field binary; UCC, wrapper roundtrip and CRC.')
