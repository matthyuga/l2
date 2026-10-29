from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import subprocess,hashlib,json
root=Path(__file__).resolve().parents[4];s=Path(__file__).resolve().parent/'compact-v3';s.mkdir(exist_ok=True)
editor=root/'research/amber-l2/tools/l2editor/L2Editor';classes=editor.parent/'HGLabelArtV3/Classes';classes.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(512,192),(0,0,0,0));d=ImageDraw.Draw(im)
d.rounded_rectangle((14,18,498,172),radius=16,fill=(10,18,28,48),outline=(233,191,121,130),width=2)
for text,y,size in [('HELLGAMES',58,26),('EVENTO',119,48)]:
 f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',size);d.text((256,y),text,font=f,anchor='mm',fill=(245,215,159,255),stroke_width=1,stroke_fill=(10,18,28,150))
# Texture dimensions must be powers of two for this client. Place the artwork
# in a 512x256 atlas and match the particle's two physical axes accordingly.
atlas=Image.new('RGBA',(512,256),(0,0,0,0));atlas.alpha_composite(im,(0,32));atlas.save(s/'compact-label.png');ImageOps.flip(atlas).save(s/'EventLabel.tga')
(classes/'Art.uc').write_text('class Art extends Object;\n'+f'#exec TEXTURE IMPORT NAME=EventLabel FILE="{(s/"EventLabel.tga").as_posix()}" MIPS=OFF\n',encoding='ascii')
(editor/'HGLabelArtV3.ini').write_text((editor/'UT2003.ini').read_text(encoding='latin1')+'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages=HGLabelArtV3\n',encoding='latin1')
assert not (editor/'HGLabelArtV3.u').exists()
r=subprocess.run([str(editor/'UCC.exe'),'make','-Silent','-NoBind','ini=HGLabelArtV3.ini'],cwd=editor,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
(s/'build.log').write_bytes(r.stdout+r.stderr);assert r.returncode==0 and (editor/'HGLabelArtV3.u').exists()
(s/'HGLabelArtV3.raw').write_bytes((editor/'HGLabelArtV3.u').read_bytes())
codec=root/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def run(*a):
 r=subprocess.run([str(codec),*map(str,a)],capture_output=True,timeout=30);assert r.returncode==0
run('-c','encode','-p','111','-o',s/'HGLabelArtV3.u',s/'HGLabelArtV3.raw');run('-o',s/'art.roundtrip.raw',s/'HGLabelArtV3.u');assert (s/'HGLabelArtV3.raw').read_bytes()==(s/'art.roundtrip.raw').read_bytes()
client=root.parent/'l2/system-hud'
run('-o',s/'HellgamesLabelsV1.u',client/'HellgamesLabelsV1.u')
(s/'verification.json').write_text(json.dumps({'installed':False,'before_sha256':hashlib.sha256((client/'HellgamesLabelsV1.u').read_bytes()).hexdigest(),'background_alpha':48,'border_alpha':130,'texture_dimensions':[512,256],'design':'compact, transparent, motes disabled for now','visual_result':None},indent=2))
print('Prepared transparent atlas and native texture package.')
