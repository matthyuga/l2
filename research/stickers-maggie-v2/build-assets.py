from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,subprocess,math,shutil
S=Path(__file__).resolve().parent;R=S.parents[1];V1=R/'research/stickers-radial-v1'
E=R/'research/amber-l2/tools/l2editor/L2Editor';P='NexusStickersV2'
A=S/'assets';A.mkdir(exist_ok=True);classes=E.parent/P/'Classes';classes.mkdir(parents=True,exist_ok=True)
records=json.loads((S/'cutouts.json').read_text())['stickers'];imports=[]
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
def save(name,im,flip=False):
    im.save(A/(name+'.png'));path=A/(name+'.tga');(ImageOps.flip(im) if flip else im).save(path)
    imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{path.as_posix()}" MIPS=OFF')
for i,r in enumerate(records):
    original=Image.open(r['file']).convert('RGBA');original.thumbnail((236,236),Image.Resampling.LANCZOS)
    im=Image.new('RGBA',(256,256));im.alpha_composite(original,((256-original.width)//2,(256-original.height)//2));save('Reaction'+str(i),im,True)
    for state,color in [('Up',(22,30,44,230)),('Over',(63,74,91,255)),('Down',(97,72,35,255))]:
        tile=Image.new('RGBA',(128,128));d=ImageDraw.Draw(tile);d.ellipse((2,2,126,126),fill=color,outline=(237,191,99,255),width=3)
        small=im.resize((108,108),Image.Resampling.LANCZOS);tile.alpha_composite(small,(10,0))
        d.text((64,115),r['name'].upper(),font=font(12),anchor='mm',fill=(255,237,193),stroke_width=1,stroke_fill=(12,17,27))
        save('S'+str(i)+state,tile)
save('Wheel',Image.open(V1/'assets/Wheel.png').convert('RGBA'))
for state,c in [('Up',(23,31,44,250)),('Over',(74,66,45,255)),('Down',(12,18,29,255))]:
    for stem,label in [('Center','CERRAR'),('Open','STICKERS')]:
        im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im);d.ellipse((4,4,124,124),fill=c,outline=(224,183,104),width=3)
        if stem=='Open':
            small=Image.open(records[0]['file']).convert('RGBA');small.thumbnail((94,91));im.alpha_composite(small,((128-small.width)//2,6))
            d.text((64,107),label,font=font(15),anchor='mm',fill=(255,234,189))
        else:d.text((64,64),label,font=font(20),anchor='mm',fill=(255,234,189))
        save(stem+state,im)
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
    text=template.replace('class Sticker0','class Sticker'+str(i)).replace('NexusStickersV1.Reaction0',P+'.Reaction'+str(i)).replace('Min=24,Max=24','Min=34,Max=34')
    (classes/f'Sticker{i}.uc').write_text(text,encoding='ascii')
(E/(P+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={P}\n',encoding='latin1')
out=E/(P+'.u')
if out.exists():out.unlink()
r=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+P+'.ini'],cwd=E,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
(S/'ucc-build.log').write_bytes(r.stdout+r.stderr);assert r.returncode==0 and out.exists(),(r.stdout+r.stderr).decode(errors='replace')[-3000:]
(S/(P+'.raw.u')).write_bytes(out.read_bytes())
(S/'asset-spec.json').write_text(json.dumps({'package':P,'labels':[r['name'] for r in records],'count':19,'world_half_size':34,'duration_seconds':3,'emitter_seconds':3.1},indent=2))
current=S/'current';current.mkdir(exist_ok=True)
sha=lambda p:__import__('hashlib').sha256(p.read_bytes()).hexdigest()
inputs={}
for name in ['Interface.u','Interface.xdat','skillgrp.dat','skillname-e.dat']:
    src=R.parent/'l2/system-hud'/name;dest=current/name
    if dest.exists():assert sha(dest)==sha(src),'Concurrent source edit '+name
    else:shutil.copy2(src,dest)
    inputs[str(src)]=sha(src)
shutil.copy2(current/'Interface.u',S/'Interface.u');shutil.copy2(V1/'input-mode.json',S/'input-mode.json')
(S/'input-hashes.json').write_text(json.dumps(inputs,indent=2))
fx=(V1/'build-effects.groovy').read_text().replace('NexusStickersV1','NexusStickersV2').replace('NexusStickerEffectsV1','NexusStickerEffectsV2').replace('0..<8','0..<19').replace('PASS: 8 client-native','PASS: 19 client-native')
(S/'build-effects.groovy').write_text(fx)
print('PASS: 19 extracted artwork textures and one-shot emitters compiled; live client snapshot guarded.')
