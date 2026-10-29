from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,subprocess,math,shutil,hashlib
S=Path(__file__).resolve().parent;R=S.parents[1];V2=R/'research/stickers-maggie-v2';E=R/'research/amber-l2/tools/l2editor/L2Editor';P='NexusStickersV3'
A=S/'assets';A.mkdir(exist_ok=True);classes=E.parent/P/'Classes';classes.mkdir(parents=True,exist_ok=True)
records=json.loads((V2/'cutouts.json').read_text())['stickers'];imports=[]
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
def save(name,im,flip=False):
 im.save(A/(name+'.png'));path=A/(name+'.tga');(ImageOps.flip(im) if flip else im).save(path)
 imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{path.as_posix()}" MIPS=OFF ALPHATEXTURE=1')
def padded(im,n):
 canvas=Image.new('RGBA',(n,n));canvas.alpha_composite(im,(0,0));return canvas
for i,r in enumerate(records):
 original=Image.open(r['file']).convert('RGBA');original.thumbnail((236,236),Image.Resampling.LANCZOS)
 im=Image.new('RGBA',(256,256));im.alpha_composite(original,((256-original.width)//2,(256-original.height)//2));save('Reaction'+str(i),im,True)
 for state,color in [('Up',(22,30,44,230)),('Over',(63,74,91,255)),('Down',(97,72,35,255))]:
  # Native UE2 buttons sample their target-sized upper-left rectangle; they do
  # not scale the full source bitmap to the control's dimensions.
  tile=Image.new('RGBA',(84,84));d=ImageDraw.Draw(tile);d.ellipse((1,1,82,82),fill=color,outline=(237,191,99,255),width=2)
  small=im.resize((72,72),Image.Resampling.LANCZOS);tile.alpha_composite(small,(6,0))
  d.text((42,76),r['name'].upper(),font=font(9),anchor='mm',fill=(255,237,193),stroke_width=1,stroke_fill=(12,17,27))
  save('S'+str(i)+state,padded(tile,128))
wheel=Image.new('RGBA',(384,384));d=ImageDraw.Draw(wheel)
d.ellipse((3,3,380,380),fill=(9,14,24,216),outline=(209,168,89,240),width=2)
d.ellipse((97,97,287,287),fill=(13,21,33,230),outline=(209,168,89,180),width=1)
for i in range(8):
 a=math.tau*(i+.5)/8-math.pi/2;d.line((192+96*math.cos(a),192+96*math.sin(a),192+187*math.cos(a),192+187*math.sin(a)),fill=(182,147,83,100),width=1)
save('Wheel',padded(wheel,512))
for state,color in [('Up',(23,31,44,250)),('Over',(74,66,45,255)),('Down',(12,18,29,255))]:
 close=Image.new('RGBA',(98,98));d=ImageDraw.Draw(close);d.ellipse((1,1,96,96),fill=color,outline=(224,183,104),width=2);d.text((49,49),'CERRAR',font=font(15),anchor='mm',fill=(255,234,189));save('Center'+state,padded(close,128))
 opened=Image.new('RGBA',(48,48));d=ImageDraw.Draw(opened);d.ellipse((0,0,47,47),fill=color,outline=(224,183,104),width=1)
 small=Image.open(records[0]['file']).convert('RGBA');small.thumbnail((40,37));opened.alpha_composite(small,((48-small.width)//2,1));d.text((24,42),'MENU',font=font(8),anchor='mm',fill=(255,234,189));save('Open'+state,padded(opened,64))
(classes/'A_StickerBase.uc').write_text('class A_StickerBase extends Emitter;\n'+'\n'.join(imports)+'''\ndefaultproperties
{
 AutoDestroy=True
 bNoDelete=False
 bHidden=False
 bDirectional=False
 LifeSpan=3.10
}
''',encoding='ascii')
template=(R/'research/amber-l2/tools/l2editor/NexusStickersV1/Classes/Sticker0.uc').read_text()
for i in range(19):
 text=template.replace('class Sticker0','class Sticker'+str(i)).replace('NexusStickersV1.Reaction0',P+'.Reaction'+str(i)).replace('Min=24,Max=24','Min=34,Max=34').replace('Min=92,Max=92','Min=35,Max=35')
 (classes/f'Sticker{i}.uc').write_text(text,encoding='ascii')
(E/(P+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={P}\n',encoding='latin1')
compiled=E/(P+'.u')
if compiled.exists():compiled.unlink()
p=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+P+'.ini'],cwd=E,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
(S/'ucc-build.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0 and compiled.exists(),(p.stdout+p.stderr).decode(errors='replace')[-3000:]
(S/(P+'.raw.u')).write_bytes(compiled.read_bytes())
current=S/'current';current.mkdir(exist_ok=True);inputs={};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat']:
 src=R.parent/'l2/system-hud'/name;dest=current/name
 if dest.exists():assert sha(src)==sha(dest),'Concurrent edit: '+name
 else:shutil.copy2(src,dest)
 inputs[str(src)]=sha(src)
(S/'input-hashes.json').write_text(json.dumps(inputs,indent=2));shutil.copy2(current/'Interface.u',S/'Interface.u');shutil.copy2(V2/'input-mode.json',S/'input-mode.json')
print('BUILT: 19 neck-attached sprite classes, UI art at exact 84/98/48/384 display sizes, alpha-enabled imports.')
