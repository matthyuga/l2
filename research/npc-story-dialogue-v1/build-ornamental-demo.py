"""Replace only background mipmap pixels in the existing texture package."""
from pathlib import Path
import hashlib,json,shutil,subprocess,struct,zlib
from PIL import Image,ImageOps,ImageDraw,ImageFont

B=Path(__file__).resolve().parent;R=B.parents[1];V3=B/'client-demo-angular-v3'
S=B/'client-demo-ornamental-v4';S.mkdir(exist_ok=True)
A=S/'assets';A.mkdir(exist_ok=True)
C=R.parent/'l2/system-hud';P='NexusAmberAngularV3.u'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation.json').exists(),'Already applied; create a new layer for revisions'
inputs=json.loads((S/'input-hashes.json').read_text())
for name,h in inputs.items():assert sha(Path(name))==h,'Concurrent change: '+name
source=Image.open(S/'ornamental-generated.png').convert('RGB')
fill=ImageOps.fit(source,(610,280),method=Image.Resampling.LANCZOS)
fill.save(S/'ornamental-fill-610x280.png')
proof=[]
for name in ['BackgroundOpaque','BackgroundSemi']:
    old_png=Image.open(V3/'assets'/(name+'.png')).convert('RGBA')
    new=fill.convert('RGBA');new.putalpha(old_png.getchannel('A'))
    assert new.getchannel('A').tobytes()==old_png.getchannel('A').tobytes()
    new.save(A/(name+'.png'))
    pad=Image.new('RGBA',(1024,512));pad.paste(new,(0,0));pad.save(A/(name+'.tga'))
    old=Image.open(V3/'assets'/(name+'.tga')).convert('RGBA')
    original_pixels=old.tobytes('raw','BGRA')
    original_export=(S/'native-exports'/(name+'.bin')).read_bytes()
    offset=original_export.find(original_pixels)
    assert offset>=0 and original_export.count(original_pixels)==1,'Native pixel format does not match source'
    pixels=pad.tobytes('raw','BGRA')
    assert len(pixels)==len(original_pixels)
    changed=original_export[:offset]+pixels+original_export[offset+len(pixels):]
    assert changed[:offset]==original_export[:offset] and changed[offset+len(pixels):]==original_export[offset+len(pixels):]
    (S/'native-exports'/(name+'.new.bin')).write_bytes(changed)
    proof.append(dict(texture=name,pixel_offset=offset,pixel_bytes=len(pixels),alpha_preserved=True,metadata_preserved=True))
java=R/'tools/jdk-25.0.4.1+1/bin/java.exe'
cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(R/'tools/javafx-sdk-21.0.9/lib/*')
p=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(B/'patch-ornamental-textures.groovy'),str(S),'patch'],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=120)
(S/'native-verification.log').write_text(p.stdout+p.stderr,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr;print(p.stdout.strip())
codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
for args in [('-c','encode','-p','121','-f',P,'-o',str(S/P),str(S/'patched.raw.u')),('-c','decode','-f',P,'-o',str(S/'roundtrip.raw.u'),str(S/P))]:
    p=subprocess.run([str(codec),*args],input=b'\n',capture_output=True,timeout=40);assert p.returncode==0
assert (S/'roundtrip.raw.u').read_bytes()==(S/'patched.raw.u').read_bytes()
data=(S/P).read_bytes();assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])
proof=dict(changed_exports=proof,unchanged=['all other texture exports','BackgroundClear','Interface.u','Interface.xdat','portrait and compensation','server'],texture_crc=True,texture_roundtrip=True,native_verification=True,runtime_validation='pending')
(S/'verification.json').write_text(json.dumps(proof,indent=2))
(S/'output-hashes.json').write_text(json.dumps({P:sha(S/P)},indent=2))

# Render the same expected composition using the new fill, without modifying V3 previews.
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
portrait=Image.open(B/'client-demo-gamma-v2/assets/PortraitComp.png').convert('RGBA')
def preview(mode,w=1024,h=640):
    canvas=Image.new('RGBA',(w,h),(47,58,56,255));d=ImageDraw.Draw(canvas)
    for y in range(0,h,48):
        for x in range(0,w,48):
            if (x//48+y//48)%2:d.rectangle((x,y,x+47,y+47),fill=(57,65,60,255))
    d.text((22,18),'PREVISUALIZACION - NO ES CAPTURA DE L2',font=font(13),fill='#e1dccf')
    x0=(w-920)//2;y0=h-440-40
    def paste(n,x,y):
        p=A/(n+'.png')
        if not p.exists():p=V3/'assets'/(n+'.png')
        canvas.alpha_composite(Image.open(p).convert('RGBA'),(x0+x,y0+y))
    paste('Background'+mode,295,140);paste('Frame',295,140);paste('Nameplate',320,150)
    canvas.alpha_composite(portrait,(x0,y0+10));d=ImageDraw.Draw(canvas)
    for x,y,t,n,color in [(355,164,'AMBER',13,'#eed4a4'),(330,205,'Hola. ¿Necesitás ayuda?',13,'#f2e7d7'),(330,248,'Conversación de prueba',11,'#b9a98f'),(330,382,'Fondo:',11,'#cbbd9e')]:
        d.text((x0+x,y0+y),t,font=font(n),fill=color)
    for n,x,y in [('Explore',330,278),('Greet',330,320),('Close',862,152),('Original',680,154),('Compensate',758,154),('Opaque',392,376),('Semi',480,376),('Clear',568,376)]:paste(n+'Up',x,y)
    d.text((22,h-24),'Fondo: '+mode,font=font(13),fill='white')
    return canvas.convert('RGB')
sheet=Image.new('RGB',(1024,1920))
for i,mode in enumerate(['Opaque','Semi','Clear']):
    im=preview(mode);im.save(S/('preview-'+mode.lower()+'-1024.png'));sheet.paste(im,(0,640*i))
sheet.save(S/'comparacion-fondos.jpg',quality=94)
preview('Semi',1280,720).save(S/'preview-semi-1280.png')
print('PREPARED: ornamental background pixels only; frame, alpha and controls preserved.')
