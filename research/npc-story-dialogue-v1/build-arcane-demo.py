"""Build an isolated native dialogue UI layer from the current client snapshot."""
from pathlib import Path
import hashlib, json, math, shutil, struct, subprocess, zlib
from PIL import Image, ImageDraw, ImageFont

B = Path(__file__).resolve().parent
R = B.parents[1]
S = B / 'client-demo-angular-v3'
C = R.parent / 'l2/system-hud'
P = 'NexusAmberAngularV3'
S.mkdir(exist_ok=True)
A = S / 'assets'
A.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation.json').exists(), 'Already installed; create a new layer to revise'
current = S/'current'
current.mkdir(exist_ok=True)
inputs = {}
for n in ['Interface.u', 'Interface.xdat']:
    src, dst = C/n, current/n
    if dst.exists():
        assert sha(src) == sha(dst), 'Concurrent change: '+n
    else:
        shutil.copy2(src, dst)
    inputs[str(src)] = sha(src)
for n in ['NexusAmberStoryV1.u', 'NexusAmberGammaV2.u']:
    assert (C/n).exists(), 'Required existing portrait package missing'
    inputs[str(C/n)] = sha(C/n)
(S/'input-hashes.json').write_text(json.dumps(inputs, indent=2))

imports = []
font = lambda n: ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', n)
def save(name, im):
    im.save(A/(name+'.png'))
    w, h = [1 << (v-1).bit_length() for v in im.size]
    pad = Image.new('RGBA', (w,h))
    pad.paste(im, (0,0))
    pad.save(A/(name+'.tga'))
    imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{(A/(name+".tga")).as_posix()}" MIPS=OFF ALPHATEXTURE=1')

W,H = 610,280
outline = [(2,26),(25,3),(192,3),(210,15),(400,15),(418,3),(584,3),(607,26),(607,109),(596,123),(607,137),(607,252),(584,277),(418,277),(400,265),(210,265),(192,277),(25,277),(2,252),(2,137),(13,123),(2,109)]
mask=Image.new('L',(W,H));ImageDraw.Draw(mask).polygon(outline,fill=255)
# A procedural ornamental pattern, kept separate from all text and controls.
bg=Image.new('RGBA',(W,H));px=bg.load()
for y in range(H):
    for x in range(W):
        v=int(4*max(0,1-math.hypot((x-W/2)/(W/2),(y-H/2)/(H/2))))
        px[x,y]=(12+v,17+v,20+v,255)
d=ImageDraw.Draw(bg)
for yy in range(22,H,40):
    for xx in range(24,W,40):
        d.line([(xx,yy-10),(xx+10,yy),(xx,yy+10),(xx-10,yy),(xx,yy-10)],fill=(33,38,38,255),width=1)
        d.ellipse((xx-2,yy-2,xx+2,yy+2),outline=(47,47,39,255))
for name,alpha in [('BackgroundOpaque',255),('BackgroundSemi',156),('BackgroundClear',0)]:
    im=bg.copy();im.putalpha(mask.point(lambda v: round(v*alpha/255)));save(name,im)
frame=Image.new('RGBA',(W,H));d=ImageDraw.Draw(frame)
d.line(outline+[outline[0]],fill=(193,153,99,255),width=2)
inner=[(x+(5 if x<W/2 else -5),y+(5 if y<H/2 else -5)) for x,y in outline]
d.line(inner+[inner[0]],fill=(109,87,61,255),width=1)
for x in [25,584]:
    d.polygon([(x,117),(x+5,123),(x,129),(x-5,123)],fill=(222,184,121,255))
for x0,x1 in [(42,180),(430,568)]:
    d.line((x0,24,x1,24),fill=(79,70,52,255));d.line((x0,254,x1,254),fill=(79,70,52,255))
save('Frame',frame)
plate=Image.new('RGBA',(280,40));d=ImageDraw.Draw(plate)
d.polygon([(0,20),(17,5),(263,5),(279,20),(263,35),(17,35)],fill=(16,21,24,240),outline=(179,144,92,255))
d.line([(25,9),(255,9)],fill=(90,76,53,255));d.line([(25,31),(255,31)],fill=(90,76,53,255))
for x in [14,265]: d.polygon([(x,16),(x+4,20),(x,24),(x-4,20)],fill=(224,184,115,255))
save('Nameplate',plate)
buttons={'Explore':('Quiero conocer este lugar.',540,34),'Greet':('Solo pasaba a saludar.',540,34),'Next':('Continuar',170,34),'Restart':('Volver al inicio',170,34),'Close':('X',28,28),'Opaque':('Opaco',80,28),'Semi':('Semi',80,28),'Clear':('Transparente',122,28),'Original':('Original',72,26),'Compensate':('Compensar',92,26)}
for name,(label,w,h) in buttons.items():
    for state,fill,edge in [('Up',(22,29,32,245),(145,117,78,255)),('Over',(42,46,43,255),(237,201,140,255)),('Down',(12,18,21,255),(190,151,92,255))]:
        im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im)
        d.polygon([(0,7),(7,0),(w-8,0),(w-1,7),(w-1,h-8),(w-8,h-1),(7,h-1),(0,h-8)],fill=fill,outline=edge)
        d.line((11,h-4,w-12,h-4),fill=(70,65,50,255))
        d.text((w/2,h/2+(1 if state=='Down' else 0)),label,font=font(12 if name not in ['Original','Compensate'] else 10),anchor='mm',fill=(244,230,202,255))
        save(name+state,im)

# Build native texture package through the existing offline UE2 pipeline.
E=R/'research/amber-l2/tools/l2editor/L2Editor'
classes=E.parent/P/'Classes';classes.mkdir(parents=True,exist_ok=True)
(classes/'Assets.uc').write_text('class Assets extends Object;\n'+'\n'.join(imports)+'\ndefaultproperties {}\n',encoding='ascii')
(E/(P+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={P}\n',encoding='latin1')
compiled=E/(P+'.u')
if compiled.exists(): compiled.unlink()
p=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+P+'.ini'],cwd=E,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
(S/'ucc.log').write_bytes(p.stdout+p.stderr)
assert p.returncode==0 and compiled.exists(), 'See ucc.log'
raw=S/(P+'.raw.u');shutil.copy2(compiled,raw)
codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
for args in [('-c','encode','-p','121','-f',P+'.u','-o',str(S/(P+'.u')),str(raw)),('-c','decode','-f',P+'.u','-o',str(S/'roundtrip.raw'),str(S/(P+'.u')))]:
    p=subprocess.run([str(codec),*args],input=b'\n',capture_output=True,timeout=40);assert p.returncode==0
assert raw.read_bytes()==(S/'roundtrip.raw').read_bytes()
data=(S/(P+'.u')).read_bytes();assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])

# Add a fresh UI class, preserving every existing serialized export.
builder=(B/'client-demo/build-interface.groovy').read_text(encoding='utf8').replace('AmberStoryDemoUI','AmberAngularUI')
builder=builder.replace("'ShowEnd':null,'OnEvent'","'ShowEnd':null,'UseOriginal':null,'UseCompensation':null,'UseOpaque':null,'UseSemi':null,'UseClear':null,'OnEvent'")
builder=builder.replace("'ShowEnd']);up.addNameEntries","'ShowEnd','UseOriginal','UseCompensation','UseOpaque','UseSemi','UseClear','SetTexture']);up.addNameEntries")
builder=builder.replace("'NWindow.UIAPI_WINDOW':'Core.Class'","'NWindow.UIAPI_WINDOW':'Core.Class','NWindow.UIAPI_TEXTURECTRL':'Core.Class'")
builder=builder.replace("int resultType=0->","int resultType=0,String apiClass='NWindow.UIAPI_WINDOW'->").replace("nativeRef('NWindow.UIAPI_WINDOW')),call.getSize","nativeRef(apiClass)),call.getSize")
insert="""
 ['UseOriginal':'NexusAmberStoryV1.Portrait','UseCompensation':'NexusAmberGammaV2.PortraitComp'].each{fn,tex->
  make(fn,null){emit,guard,api,p->pages.each{win->emit(api('SetTexture',[new StringConst(win+'.Portrait'),new StringConst(tex)],0,'NWindow.UIAPI_TEXTURECTRL'))}}
 }
 ['UseOpaque':'BackgroundOpaque','UseSemi':'BackgroundSemi','UseClear':'BackgroundClear'].each{fn,tex->
  make(fn,null){emit,guard,api,p->pages.each{win->emit(api('SetTexture',[new StringConst(win+'.Background'),new StringConst('NexusAmberAngularV3.'+tex)],0,'NWindow.UIAPI_TEXTURECTRL'))}}
 }
"""
builder=builder.replace(" make('OnClickButton','strID')",insert+" make('OnClickButton','strID')")
builder=builder.replace("'Close':'CloseAll'].each","'Close':'CloseAll','Original':'UseOriginal','Compensate':'UseCompensation','Opaque':'UseOpaque','Semi':'UseSemi','Clear':'UseClear'].each")
builder=builder.replace('8 functions, 6 button routes','13 functions, 11 button routes')
(S/'build-interface.groovy').write_text(builder,encoding='utf8')
java=R/'tools/jdk-25.0.4.1+1/bin/java.exe';cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(R/'tools/javafx-sdk-21.0.9/lib/*')
for script in [S/'build-interface.groovy',B/'build-angular-xdat.groovy',B/'verify-angular.groovy']:
    p=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(script),str(S)],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=300)
    (S/(script.stem+'.log')).write_text(p.stdout+p.stderr,encoding='utf8')
    assert p.returncode==0,p.stdout+p.stderr
    print(p.stdout.strip())

# Expected layout, not a screenshot: the patterned backdrop makes alpha changes visible.
portrait=Image.open(B/'client-demo-gamma-v2/assets/PortraitComp.png').convert('RGBA')
def preview(mode,w=1024,h=640):
    canvas=Image.new('RGBA',(w,h),(47,58,56,255));d=ImageDraw.Draw(canvas)
    for y in range(0,h,48):
        for x in range(0,w,48):
            if (x//48+y//48)%2:d.rectangle((x,y,x+47,y+47),fill=(57,65,60,255))
    d.text((22,18),'PREVISUALIZACION DE COMPOSICION - NO ES CAPTURA DE L2',font=font(13),fill='#e1dccf')
    x0=(w-920)//2;y0=h-440-40
    def paste(n,x,y):canvas.alpha_composite(Image.open(A/(n+'.png')).convert('RGBA'),(x0+x,y0+y))
    paste('Background'+mode,295,140);paste('Frame',295,140);paste('Nameplate',320,150)
    canvas.alpha_composite(portrait,(x0,y0+10))
    d=ImageDraw.Draw(canvas)
    d.text((x0+355,y0+164),'AMBER',font=font(13),fill='#eed4a4')
    d.text((x0+330,y0+205),'Hola. ¿Necesitás ayuda?',font=font(13),fill='#f2e7d7')
    d.text((x0+330,y0+248),'Conversación de prueba',font=font(11),fill='#b9a98f')
    d.text((x0+330,y0+382),'Fondo:',font=font(11),fill='#cbbd9e')
    for n,x,y in [('Explore',330,278),('Greet',330,320),('Close',862,152),('Original',680,154),('Compensate',758,154),('Opaque',392,376),('Semi',480,376),('Clear',568,376)]:paste(n+'Up',x,y)
    d.text((22,h-24),'Fondo: '+{'Opaque':'opaco','Semi':'semitransparente','Clear':'transparente'}[mode],font=font(13),fill='white')
    return canvas.convert('RGB')
sheet=Image.new('RGB',(1024,640*3))
for i,mode in enumerate(['Opaque','Semi','Clear']):
    im=preview(mode);im.save(S/('preview-'+mode.lower()+'-1024.png'));sheet.paste(im,(0,i*640))
sheet.save(S/'comparacion-fondos.jpg',quality=93)
preview('Semi',1280,720).save(S/'preview-semi-1280.png')
proof={'texture_roundtrip':True,'texture_crc':True,'textures':len(imports),'ui_class':'AmberAngularUI','background_modes':{'opaque':255,'semi':156,'clear':0},'default_background':'semi','portrait_compensation_preserved':True,'settings_persistence':'page navigation and reopen during client session; reset on client restart','runtime_visual_validation':'pending','server_changed':False}
(S/'build-verification.json').write_text(json.dumps(proof,indent=2))
(S/'output-hashes.json').write_text(json.dumps({n:sha(S/n) for n in ['NexusAmberAngularV3.u','Interface.u','Interface.xdat']},indent=2))
print('BUILT: angular dialogue, 3 backgrounds, existing portrait compensation preserved.')
