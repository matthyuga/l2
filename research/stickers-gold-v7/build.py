"""Prepare a UI-only gold skin; never execute sticker actions or change effects."""
from pathlib import Path
import hashlib,json,math,shutil,struct,subprocess,zlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
S=Path(__file__).resolve().parent;R=S.parents[1];C=R.parent/'l2/system-hud'
A=S/'assets';A.mkdir(exist_ok=True);(S/'current').mkdir(exist_ok=True)
P='NexusStickerGoldV7';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation.json').exists(),'Already installed: create a new revision'
inputs={}
for n in ['Interface.u','Interface.xdat','NexusStickersV3.u','NexusAmberButtonsV5.u','NexusAmberAngularV3.u','NexusAmberGammaV2.u']:
    src=C/n;dst=S/'current'/n
    if dst.exists():assert sha(src)==sha(dst),'Concurrent change: '+n
    else:shutil.copy2(src,dst)
    inputs[str(src)]=sha(src)
(S/'input-hashes.json').write_text(json.dumps(inputs,indent=2))
imports=[];font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
def save(n,im):
    im.save(A/(n+'.png'));w,h=[1<<(v-1).bit_length() for v in im.size]
    pad=Image.new('RGBA',(w,h));pad.paste(im,(0,0));pad.save(A/(n+'.tga'))
    imports.append(f'#exec TEXTURE IMPORT NAME={n} FILE="{(A/(n+".tga")).as_posix()}" MIPS=OFF ALPHATEXTURE=1')
def tight(im):
    assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
    box=im.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox();assert box
    return im.crop((max(0,box[0]-2),max(0,box[1]-2),min(im.width,box[2]+2),min(im.height,box[3]+2)))
ring=tight(Image.open(S/'sources/ring.png').convert('RGBA')).resize((384,384),Image.Resampling.LANCZOS)
sheet=Image.open(S/'sources/medallions.png').convert('RGBA');frames={}
for i,state in enumerate(['Up','Over','Down']):frames[state]=tight(sheet.crop((round(sheet.width*i/3),0,round(sheet.width*(i+1)/3),sheet.height)))
# Reuse the already approved D Oro blank plate art for titles and names.
v5=R/'research/npc-story-dialogue-v1/client-demo-button-styles-v5'
cells=json.loads((v5/'crops.json').read_text())['D'];gold=Image.open(v5/'sources/D.png').convert('RGBA')
plates={}
for row in cells:
    cell=gold.crop(row['cell']);plates[row['kind'],row['state']]=cell.crop(row['bbox'])
def plate(w,h,state='Up',kind='compact'):
    src=plates[kind,state];sw=round(src.width*h/src.height);src=src.resize((sw,h),Image.Resampling.LANCZOS)
    cap=min(max(4,round(sw*(.13 if kind=='long' else .22))),w//3,(sw-1)//2)
    out=Image.new('RGBA',(w,h));out.paste(src.crop((0,0,cap,h)),(0,0));out.paste(src.crop((cap,0,sw-cap,h)).resize((w-2*cap,h),Image.Resampling.LANCZOS),(cap,0));out.paste(src.crop((sw-cap,0,sw,h)),(w-cap,0));return out
pattern=Image.open(R/'research/npc-story-dialogue-v1/client-demo-ornamental-v4/ornamental-generated.png').convert('RGBA')
def fill(size,alpha=225,inset=9):
    im=ImageOps.fit(pattern,(size,size),method=Image.Resampling.LANCZOS);mask=Image.new('L',(size,size));ImageDraw.Draw(mask).ellipse((inset,inset,size-inset-1,size-inset-1),fill=alpha);im.putalpha(mask);return im
wheel=fill(384,200,16);d=ImageDraw.Draw(wheel)
d.ellipse((97,97,287,287),outline=(148,109,51,160),width=1)
for i in range(8):
    a=math.tau*(i+.5)/8-math.pi/2
    d.line((192+95*math.cos(a),192+95*math.sin(a),192+174*math.cos(a),192+174*math.sin(a)),fill=(170,128,63,190),width=1)
wheel.alpha_composite(ring);save('Wheel',wheel)
records=json.loads((R/'research/stickers-maggie-v2/cutouts.json').read_text())['stickers'][:8]
artifacts=[]
for i,record in enumerate(records):
    path=Path(record['file']);original=Image.open(path).convert('RGBA');small=original.copy();small.thumbnail((63,61),Image.Resampling.LANCZOS)
    artifacts.append(dict(slot='S'+str(i),label=record['name'].upper(),original=str(path),original_sha256=sha(path)))
    for state in ['Up','Over','Down']:
        tile=Image.new('RGBA',(84,84));tile.alpha_composite(fill(74,235,9),(5,0));tile.alpha_composite(frames[state].resize((74,74),Image.Resampling.LANCZOS),(5,0))
        tile.alpha_composite(small,((84-small.width)//2,3+(61-small.height)//2))
        tile.alpha_composite(plate(80,18,state),(2,66));ImageDraw.Draw(tile).text((42,75),record['name'].upper(),font=font(9),anchor='mm',fill='#fff0cd',stroke_width=1,stroke_fill='#1d140b')
        save('S'+str(i)+state,tile)
for state in ['Up','Over','Down']:
    center=fill(98,240,12);center.alpha_composite(frames[state].resize((98,98),Image.Resampling.LANCZOS));ImageDraw.Draw(center).text((49,49),'CERRAR',font=font(14),anchor='mm',fill='#ffedbd',stroke_width=1,stroke_fill='#1d140b');save('Center'+state,center)
    op=fill(48,230,6);op.alpha_composite(frames[state].resize((48,48),Image.Resampling.LANCZOS));icon=Image.open(Path(records[0]['file'])).convert('RGBA');icon.thumbnail((31,29),Image.Resampling.LANCZOS);op.alpha_composite(icon,((48-icon.width)//2,5));ImageDraw.Draw(op).text((24,37),'MENU',font=font(7),anchor='mm',fill='#ffedbd');save('Open'+state,op)
title=plate(168,24,kind='long');ImageDraw.Draw(title).text((84,12),'STICKERS',font=font(12),anchor='mm',fill='#fff0cd',stroke_width=1,stroke_fill='#1d140b');save('Title',title)
save('HintPlate',plate(216,24,kind='long'))
(S/'artwork.json').write_text(json.dumps(artifacts,indent=2))
E=R/'research/amber-l2/tools/l2editor/L2Editor';classes=E.parent/P/'Classes';classes.mkdir(parents=True,exist_ok=True)
(classes/'Assets.uc').write_text('class Assets extends Object;\n'+'\n'.join(imports)+'\ndefaultproperties {}\n',encoding='ascii')
(E/(P+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={P}\n',encoding='latin1')
compiled=E/(P+'.u')
if compiled.exists():compiled.unlink()
p=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+P+'.ini'],cwd=E,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(S/'ucc.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0 and compiled.exists()
raw=S/(P+'.raw.u');shutil.copy2(compiled,raw);codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
for args in [('-c','encode','-p','121','-f',P+'.u','-o',str(S/(P+'.u')),str(raw)),('-c','decode','-f',P+'.u','-o',str(S/'roundtrip.raw'),str(S/(P+'.u')))]:
    p=subprocess.run([str(codec),*args],input=b'\n',capture_output=True,timeout=40);assert p.returncode==0
assert raw.read_bytes()==(S/'roundtrip.raw').read_bytes();data=(S/(P+'.u')).read_bytes();assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])
java=R/'tools/jdk-25.0.4.1+1/bin/java.exe';cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(R/'tools/javafx-sdk-21.0.9/lib/*')
for script in [S/'build-xdat.groovy',S/'verify.groovy']:
    p=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(script),str(S)],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=120)
    (S/(script.stem+'.log')).write_text(p.stdout+p.stderr,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr;print(p.stdout.strip())
(S/'output-hashes.json').write_text(json.dumps({n:sha(S/n) for n in [P+'.u','Interface.xdat']},indent=2))
(S/'verification.json').write_text(json.dumps(dict(texture_crc=True,texture_roundtrip=True,textures=len(imports),unchanged_interface_script=True,unchanged_effects=True,changed_windows=2,original_artwork=artifacts,in_game_validation='pending'),indent=2))
canvas=Image.new('RGBA',(520,510),(43,50,46,255));x0=68;y0=28
canvas.alpha_composite(wheel,(x0,y0+24));canvas.alpha_composite(title,(x0+108,y0));canvas.alpha_composite(Image.open(A/'HintPlate.png'),(x0+84,y0+411))
for i in range(8):
    a=math.tau*i/8-math.pi/2;x=round(192+137*math.cos(a)-42);y=round(192+137*math.sin(a)-42)+24
    canvas.alpha_composite(Image.open(A/('S'+str(i)+'Up.png')),(x0+x,y0+y))
canvas.alpha_composite(Image.open(A/'CenterUp.png'),(x0+143,y0+167));d=ImageDraw.Draw(canvas);d.text((x0+192,y0+425),'Elegir: clic · Cerrar: centro',font=font(10),anchor='mm',fill='#f3d8a3');d.text((260,488),'PREVISUALIZACION - NO ES CAPTURA DE L2',font=font(10),anchor='mm',fill='white');canvas.convert('RGB').save(S/'preview-native.png')
print('PREPARED: UI-only gold sticker wheel; scripts, original sticker artwork and effects retained.')
