from pathlib import Path
import json,hashlib,subprocess,shutil,zlib,struct,csv
from PIL import Image,ImageDraw,ImageFont
S=Path(__file__).resolve().parent;R=S.parents[1];C=R.parent/'l2/system-hud';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=C/'NexusStickersV3.u'
current=S/'current';current.mkdir(exist_ok=True)
if (current/source.name).exists():assert sha(current/source.name)==sha(source),'Concurrent change'
else:shutil.copy2(source,current/source.name)
curve=json.loads((R/'research/npc-story-dialogue-v1/client-demo-gamma-v2/compensation.json').read_text());lut=curve['inverse_8bit'];(S/'inverse-lut.bin').write_bytes(bytes(lut))
codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def crypt(*args):
 p=subprocess.run([str(codec),*map(str,args)],input=b'\n',capture_output=True,timeout=40);assert p.returncode==0,p.stdout+p.stderr
crypt('-c','decode','-f',source.name,'-o',S/'NexusStickersV3.before.raw.u',source)
java=R/'tools/jdk-25.0.4.1+1/bin/java.exe';cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')
p=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(S/'patch-textures.groovy'),str(S)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120);(S/'verification.txt').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,(p.stdout+p.stderr)[-1800:]
before=(S/'NexusStickersV3.before.raw.u').read_bytes();after=(S/'NexusStickersV3.patched.raw.u').read_bytes();assert len(before)==len(after)
blocks=list(csv.DictReader((S/'pixel-blocks.csv').open()));assert len(blocks)==19
permitted=bytearray(len(before));changed=0
for row in blocks:
 a=int(row['offset']);n=int(row['length']);assert n==256*256*4
 for i in range(n):
  if i%4!=3:permitted[a+i]=1
  else:assert before[a+i]==after[a+i]
for i,(a,b) in enumerate(zip(before,after)):
 if a!=b:assert permitted[i];changed+=1
assert changed>0
crypt('-c','encode','-p','121','-f',source.name,'-o',S/source.name,S/'NexusStickersV3.patched.raw.u');crypt('-c','decode','-f',source.name,'-o',S/'roundtrip.raw',S/source.name);assert (S/'roundtrip.raw').read_bytes()==after
b=(S/source.name).read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
proof={'target':str(source),'before_sha256':sha(source),'after_sha256':sha(S/source.name),'changed_rgb_bytes':changed,'textures':19,'all_other_raw_bytes_identical':True,'alpha_preserved':True,'wrapper_roundtrip':True,'wrapper_crc':True,'menu_textures_unchanged':True,'sprite_emitter_code_unchanged':True,'global_gamma_unchanged':True,'visual_verification':'pending in L2'};(S/'verification.json').write_text(json.dumps(proof,indent=2))
for name in ['NexusStickerEffectsV3.usk']:
 proof[name+'_sha256']=sha(R.parent/'l2/animations'/name)
(S/'verification.json').write_text(json.dumps(proof,indent=2))
# Reference/expected display comparison for the first three stickers.
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',13);sheet=Image.new('RGBA',(810,850),(31,33,31,255));d=ImageDraw.Draw(sheet)
for j,label in enumerate(['Referencia','Con gamma L2','Compensado + gamma L2']):d.text((j*270+10,10),label,font=font,fill='white')
display=[round(v/257) for v in curve['forward_16bit']]
def remap(im,l):
 r,g,b,a=im.split();return Image.merge('RGBA',(r.point(l),g.point(l),b.point(l),a))
for i in range(3):
 im=Image.open(R/f'research/stickers-overhead-v3/assets/Reaction{i}.png').convert('RGBA')
 for j,v in enumerate([im,remap(im,display),remap(remap(im,lut),display)]):sheet.alpha_composite(v,(j*270,40+i*270))
sheet.convert('RGB').save(S/'expected-comparison.png')
print(p.stdout.strip());print('BUILT:19 sticker world textures with inverse gamma; all other raw bytes preserved; no installed changes.')
