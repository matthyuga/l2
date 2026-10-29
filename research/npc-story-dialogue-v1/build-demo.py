from pathlib import Path
import subprocess,json,shutil,hashlib,textwrap,zlib,struct
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
ROOT=Path(r'E:\l2-local');BASE=Path(__file__).resolve().parent;S=BASE/'client-demo';S.mkdir(exist_ok=True)
C=Path(r'E:\l2\system-hud');P='NexusAmberStoryV1';JAVA=ROOT/'tools/jdk-25.0.4.1+1/bin/java.exe'
CP=str(ROOT/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(ROOT/'tools/javafx-sdk-21.0.9/lib/*')+';'+str(ROOT/'research/amber-l2/scripts')
def groovy(file):
 p=subprocess.run([str(JAVA),'-cp',CP,'groovy.ui.GroovyMain',str(file),str(S)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
 (S/(file.stem+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stdout+p.stderr;print(p.stdout.strip())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
current=S/'current';current.mkdir(exist_ok=True);inputs={}
for n in ['Interface.u','Interface.xdat']:
 src=C/n;dst=current/n
 if dst.exists():assert sha(src)==sha(dst),'Concurrent change: '+n
 else:shutil.copy2(src,dst)
 inputs[str(src)]=sha(src)
(S/'input-hashes.json').write_text(json.dumps(inputs,indent=2))
A=S/'assets';A.mkdir(exist_ok=True);src=BASE/'external/dark-ui-free-demo';imports=[]
def nine(im,size,b=14):
 out=Image.new('RGBA',size);w,h=im.size;W,H=size
 xs=[0,b,w-b,w];ys=[0,b,h-b,h];dx=[0,b,W-b,W];dy=[0,b,H-b,H]
 for i in range(3):
  for j in range(3):out.paste(im.crop((xs[i],ys[j],xs[i+1],ys[j+1])).resize((dx[i+1]-dx[i],dy[j+1]-dy[j]),Image.Resampling.LANCZOS),(dx[i],dy[j]))
 return out
def save(name,im):
 im.save(A/(name+'.png'));W=1<<(im.width-1).bit_length();H=1<<(im.height-1).bit_length();canvas=Image.new('RGBA',(W,H));canvas.paste(im,(0,0));canvas.save(A/(name+'.tga'))
 imports.append(f'#exec TEXTURE IMPORT NAME={name} FILE="{(A/(name+".tga")).as_posix()}" MIPS=OFF ALPHATEXTURE=1')
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
portrait=Image.open(BASE/'assets/amber-neutral-v1.png').convert('RGBA').resize((320,400),Image.Resampling.LANCZOS);save('Portrait',portrait)
panel=nine(Image.open(src/'Tooltip_Box.png').convert('RGBA'),(480,260));save('Panel',panel)
button_src=Image.open(src/'Standard_Button_orange.png').convert('RGBA')
buttons={'Explore':('Quiero conocer este lugar.',430,34),'Greet':('Solo pasaba a saludar.',430,34),'Next':('Continuar',170,36),'Restart':('Volver al inicio',170,36),'Close':('X',30,28),'Open':('AMBER',70,34)}
for stem,(label,w,h) in buttons.items():
 for state,factor in [('Up',1.),('Over',1.25),('Down',.75)]:
  im=ImageEnhance.Brightness(nine(button_src,(w,h),10)).enhance(factor);d=ImageDraw.Draw(im);d.text((w/2,h/2),label,font=font(13 if stem!='Close' else 15),anchor='mm',fill=(255,239,203),stroke_width=1,stroke_fill=(20,10,5));save(stem+state,im)
E=ROOT/'research/amber-l2/tools/l2editor/L2Editor';classes=E.parent/P/'Classes';classes.mkdir(parents=True,exist_ok=True)
(classes/'StoryAssets.uc').write_text('class StoryAssets extends Object;\n'+'\n'.join(imports)+'\ndefaultproperties {}\n',encoding='ascii')
(E/(P+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={P}\n',encoding='latin1')
compiled=E/(P+'.u')
if compiled.exists():compiled.unlink()
p=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+P+'.ini'],cwd=E,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(S/'ucc.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0 and compiled.exists()
plain=S/(P+'.raw.u');shutil.copy2(compiled,plain)
codec=ROOT/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def crypt(*args):
 p=subprocess.run([str(codec),*map(str,args)],capture_output=True,input=b'\n',timeout=40);assert p.returncode==0,p.stdout+p.stderr
crypt('-c','encode','-p','121','-f',P+'.u','-o',S/(P+'.u'),plain)
crypt('-c','decode','-f',P+'.u','-o',S/(P+'.roundtrip.raw'),S/(P+'.u'));assert (S/(P+'.roundtrip.raw')).read_bytes()==plain.read_bytes()
data=(S/(P+'.u')).read_bytes();assert struct.unpack_from('<I',data,len(data)-8)[0]==zlib.crc32(data[:-20])
# Reuse the serializer and native class/function construction already verified for the sticker window.
old=(ROOT/'research/stickers-radial-v1/build-interface.groovy').read_text();header=old[:old.index(" make('OnLoad',null)")].replace('StickerRadialUI','AmberStoryDemoUI')
header=header.replace("client=new File(stage.parentFile.parentFile.parentFile,'l2/system-hud')","client=new File('E:/l2/system-hud')")
header=header.replace("def signatures=['OnLoad':null,'ToggleWheel':null,'OnEvent':'Event_ID','OnTimer':'TimerID','OnClickButton':'strID']","def signatures=['OnLoad':null,'CloseAll':null,'ShowWelcome':null,'ShowPlace':null,'ShowGreeting':null,'ShowEnd':null,'OnEvent':'Event_ID','OnClickButton':'strID']")
header=header.replace("up.addNameEntries(names.collectEntries", "names.addAll(['CloseAll','ShowWelcome','ShowPlace','ShowGreeting','ShowEnd']);up.addNameEntries(names.collectEntries")
tail="""
 def pages=['AmberStoryWelcomeWnd','AmberStoryPlaceWnd','AmberStoryGreetingWnd','AmberStoryEndWnd']
 make('CloseAll',null){emit,guard,api,p->pages.each{emit(api('HideWindow',[new StringConst(it)]))}}
 make('OnLoad',null){emit,guard,api,p->emit(vcall('RegisterEvent',[new IntConst(150)]));emit(vcall('RegisterEvent',[new IntConst(160)]));emit(vcall('CloseAll'));emit(api('HideWindow',[new StringConst('AmberStoryLauncherWnd')]))}
 ['ShowWelcome':pages[0],'ShowPlace':pages[1],'ShowGreeting':pages[2],'ShowEnd':pages[3]].each{fn,win->
  make(fn,null){emit,guard,api,p->emit(vcall('CloseAll'));emit(api('ShowWindow',[new StringConst(win)]));emit(api('SetFocus',[new StringConst(win)]))}
 }
 make('OnEvent','Event_ID'){emit,guard,api,p->
  guard(new NativeFunctionCall(154,p,new IntConst(150))){emit(vcall('CloseAll'));emit(api('ShowWindow',[new StringConst('AmberStoryLauncherWnd')]))}
  guard(new NativeFunctionCall(154,p,new IntConst(160))){emit(vcall('CloseAll'));emit(api('HideWindow',[new StringConst('AmberStoryLauncherWnd')]))}
 }
 make('OnClickButton','strID'){emit,guard,api,p->
  ['Open':'ShowWelcome','Explore':'ShowPlace','Greet':'ShowGreeting','Next':'ShowEnd','Restart':'ShowWelcome','Close':'CloseAll'].each{button,fn->
   guard(new NativeFunctionCall(122,p,new StringConst(button))){emit(vcall(fn));emit(new Return(new Nothing()))}
  }
 }
 classEntry.setObjectRawData(encode(clazz,classEntry))
 original.each{n,b->assert Arrays.equals(b,byName(n).objectRawData):'Previous export changed: '+n}
 println 'PASS: isolated AmberStoryDemoUI, 8 functions, 6 button routes, no timers/network calls; all previous exports byte identical.'
}
"""
(S/'build-interface.groovy').write_text(header+tail,encoding='utf-8');groovy(S/'build-interface.groovy');groovy(BASE/'build-demo-xdat.groovy')
# Review image of the expected control layout; this is not a game screenshot.
canvas=Image.new('RGBA',(810,440),(24,31,27,255));canvas.alpha_composite(panel,(310,150));canvas.alpha_composite(portrait,(10,10));d=ImageDraw.Draw(canvas);d.text((335,173),'AMBER',font=font(19),fill='#f2d7a6');d.text((335,212),'Hola. ¿Necesitás ayuda?',font=font(15),fill='#f2e7d7');d.text((335,245),'Conversación de prueba',font=font(12),fill='#b9a98f')
for n,x,y in [('ExploreUp',335,295),('GreetUp',335,337),('CloseUp',746,164)]:canvas.alpha_composite(Image.open(A/(n+'.png')),(x,y))
canvas.convert('RGB').save(S/'expected-layout.png')
(S/'build-verification.json').write_text(json.dumps({'texture_package_roundtrip':True,'texture_crc':True,'custom_windows':5,'dialogue_nodes':4,'network_mutations':False,'visual_verification':'pending in L2'},indent=2))
print('BUILT: Amber dialogue client demo; in-game validation pending.')
