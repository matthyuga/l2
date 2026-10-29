"""Build original geometric reaction art and isolated UE2 emitters; never install."""
from pathlib import Path
import subprocess, math, json
from PIL import Image, ImageDraw, ImageFont, ImageOps

STAGE=Path(__file__).resolve().parent
ROOT=STAGE.parents[1]
EDITOR=ROOT/'research/amber-l2/tools/l2editor/L2Editor'
PKG='NexusStickersV1'
CLASSES=EDITOR.parent/PKG/'Classes'
CLASSES.mkdir(parents=True,exist_ok=True)
ASSETS=STAGE/'assets';ASSETS.mkdir(exist_ok=True)
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
labels=['RISA','GG','CORAZON','ENOJO','LLANTO','SORPRESA','DUDA','SALUDO']
imports=[]
icons=[]

def save(name,im,flip=False):
    im.save(ASSETS/(name+'.png'))
    path=ASSETS/(name+'.tga')
    (ImageOps.flip(im) if flip else im).save(path)
    imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{path.as_posix()}" MIPS=OFF')

def text(d,xy,s,n,fill):d.text(xy,s,font=font(n),anchor='mm',fill=fill,stroke_width=1,stroke_fill=(12,17,27,255))
for i,label in enumerate(labels):
    im=Image.new('RGBA',(256,256));d=ImageDraw.Draw(im)
    dark=(22,27,40,255)
    d.ellipse((25,29,233,237),fill=(0,0,0,110))
    face=(250,194,66,255) if i!=3 else (243,99,73,255)
    d.ellipse((20,18,234,232),fill=dark)
    d.ellipse((28,26,226,224),fill=face,outline=(255,231,150,255),width=5)
    if i==0:
        d.arc((57,70,107,113),190,350,fill=dark,width=11);d.arc((149,70,199,113),190,350,fill=dark,width=11)
        d.pieslice((65,98,190,201),0,180,fill=dark);d.rounded_rectangle((80,150,176,162),4,fill='white')
    elif i==1:
        d.rounded_rectangle((44,70,213,116),14,fill=dark);d.line((40,80,216,80),fill=dark,width=9)
        text(d,(128,161),'GG',65,(255,255,255,255))
    elif i==2:
        for x in (80,177):
            d.ellipse((x-27,69,x,97),fill=(228,49,96));d.ellipse((x-2,69,x+25,97),fill=(228,49,96));d.polygon([(x-26,84),(x+24,84),(x,118)],fill=(228,49,96))
        d.arc((72,117,185,188),0,180,fill=dark,width=9)
    elif i==3:
        d.line((56,70,105,89),fill=dark,width=12);d.line((151,89,201,70),fill=dark,width=12)
        d.ellipse((78,96,94,115),fill=dark);d.ellipse((162,96,178,115),fill=dark)
        d.arc((75,151,183,209),185,355,fill=dark,width=10)
    elif i==4:
        d.arc((59,73,109,112),185,350,fill=dark,width=9);d.arc((145,73,195,112),185,350,fill=dark,width=9)
        for x in (79,177):d.rounded_rectangle((x-8,110,x+10,183),8,fill=(87,192,255),outline=(220,247,255),width=2)
        d.ellipse((110,150,147,187),fill=dark)
    elif i==5:
        for x in (84,172):d.ellipse((x-13,77,x+13,111),fill=dark)
        d.ellipse((104,136,152,192),fill=dark)
    elif i==6:
        d.line((59,91,104,81),fill=dark,width=10);d.ellipse((165,89,183,112),fill=dark)
        d.line((95,169,160,161),fill=dark,width=9);text(d,(201,45),'?',63,(255,255,255,255))
    else:
        for x in (82,165):d.arc((x-17,80,x+22,117),185,350,fill=dark,width=8)
        d.arc((80,116,176,179),0,180,fill=dark,width=9)
        d.rounded_rectangle((190,114,232,206),16,fill=(255,218,135),outline=dark,width=5)
        for x,y in [(194,103),(205,95),(216,100),(227,111)]:d.line((x,y,x,153),fill=(255,218,135),width=11)
    # World glyphs follow the known upright SpriteEmitter texture orientation.
    save('Reaction'+str(i),im,True);icons.append(im)
    for state,color in [('Up',(22,30,44,230)),('Over',(63,74,91,255)),('Down',(97,72,35,255))]:
        tile=Image.new('RGBA',(128,128));p=ImageDraw.Draw(tile)
        p.ellipse((2,2,126,126),fill=color,outline=(237,191,99,255),width=3)
        tile.alpha_composite(im.resize((99,99),Image.Resampling.LANCZOS),(14,6))
        text(p,(64,112),label,13,(255,237,193,255));save('S'+str(i)+state,tile)

wheel=Image.new('RGBA',(512,512));d=ImageDraw.Draw(wheel)
d.ellipse((8,8,504,504),fill=(9,14,24,216),outline=(209,168,89,240),width=3)
d.ellipse((125,125,387,387),fill=(13,21,33,230),outline=(209,168,89,180),width=2)
for i in range(8):
    a=math.tau*(i+.5)/8-math.pi/2
    d.line((256+132*math.cos(a),256+132*math.sin(a),256+246*math.cos(a),256+246*math.sin(a)),fill=(182,147,83,100),width=2)
save('Wheel',wheel)
for state,c in [('Up',(23,31,44,250)),('Over',(74,66,45,255)),('Down',(12,18,29,255))]:
    im=Image.new('RGBA',(128,128));d=ImageDraw.Draw(im);d.ellipse((4,4,124,124),fill=c,outline=(224,183,104),width=3)
    text(d,(64,52),'STICKERS',18,(255,234,189));text(d,(64,79),'ALT+E',15,(173,187,202));save('Center'+state,im)

source='class A_StickerBase extends Emitter;\n'+'\n'.join(imports)+'''
defaultproperties
{
 AutoDestroy=True
 bNoDelete=False
 bHidden=False
 bDirectional=False
 LifeSpan=3.10
}
'''
(CLASSES/'A_StickerBase.uc').write_text(source,encoding='ascii')
for i in range(8):
    (CLASSES/f'Sticker{i}.uc').write_text(f'''class Sticker{i} extends A_StickerBase;
defaultproperties
{{
 Begin Object Class=SpriteEmitter Name=Icon
  Texture=Texture'{PKG}.Reaction{i}'
  DrawStyle=PTDS_AlphaBlend
  CoordinateSystem=PTCS_Relative
  UseDirectionAs=PTDU_None
  UseCollision=False
  UniformSize=True
  AutomaticInitialSpawning=False
  InitialParticlesPerSecond=10000.0
  MaxParticles=1
  RespawnDeadParticles=False
  SecondsBeforeInactive=0.0
  StartLocationRange=(Z=(Min=92,Max=92))
  StartSizeRange=(X=(Min=24,Max=24),Y=(Min=24,Max=24),Z=(Min=24,Max=24))
  FadeIn=True
  FadeInEndTime=0.10
  FadeOut=True
  FadeOutStartTime=2.65
  LifetimeRange=(Min=3.0,Max=3.0)
 End Object
 Emitters(0)=SpriteEmitter'Icon'
}}
''',encoding='ascii')
ini=(EDITOR/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={PKG}\n'
(EDITOR/(PKG+'.ini')).write_text(ini,encoding='latin1')
out=EDITOR/(PKG+'.u')
if out.exists():out.unlink()
r=subprocess.run([str(EDITOR/'UCC.exe'),'make','-Silent','-NoBind','ini='+PKG+'.ini'],cwd=EDITOR,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
(STAGE/'ucc-build.log').write_bytes(r.stdout+r.stderr)
assert r.returncode==0 and out.exists(),(r.stdout+r.stderr).decode(errors='replace')[-3000:]
(STAGE/(PKG+'.raw.u')).write_bytes(out.read_bytes())
preview=Image.new('RGB',(800,450),(13,20,31))
for i,im in enumerate(icons):
    x=20+(i%4)*195;y=10+(i//4)*220;preview.paste(im.resize((170,170)),(x,y),im.resize((170,170)))
    ImageDraw.Draw(preview).text((x+85,y+186),labels[i],font=font(20),anchor='mm',fill=(244,214,159))
preview.save(STAGE/'stickers-preview.png')
(STAGE/'asset-spec.json').write_text(json.dumps({'package':PKG,'labels':labels,'duration_seconds':3,'emitter_seconds':3.1,'textures':len(imports)},indent=2))
print('PASS: original eight reactions, radial textures and temporary sprite emitters compiled.')
