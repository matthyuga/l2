from pathlib import Path
import json,math,subprocess,hashlib,shutil,zlib,struct
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
B=Path(__file__).resolve().parent;R=B.parents[1];V1=B/'client-demo';S=B/'client-demo-gamma-v2';S.mkdir(exist_ok=True);A=S/'assets';A.mkdir(exist_ok=True);C=R.parent/'l2/system-hud';P='NexusAmberGammaV2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((V1/'installation.json').read_text())
for row in m['files']:assert sha(Path(row['target']))==row['after_sha256'],'Client changed after V1; review before rebuilding'
current=S/'current';current.mkdir(exist_ok=True)
for n in ['Interface.u','Interface.xdat']:shutil.copy2(C/n,current/n)
(S/'input-hashes.json').write_text(json.dumps({str(C/n):sha(C/n) for n in ['Interface.u','Interface.xdat']},indent=2))
# Invert the client curve actually captured by REA, channel by channel.
def curve(x):return min(65535,max(0,round((x/255)**(1/.8)*1.2*65535+(.8-.5)*32768-.7*32768+16384)))
forward=[curve(i) for i in range(256)];inverse=[min(range(256),key=lambda x:abs(forward[x]-y*257)) for y in range(256)]
source=Image.open(B/'assets/amber-neutral-v1.png').convert('RGBA');ch=source.split();comp=Image.merge('RGBA',tuple(c.point(inverse) for c in ch[:3])+(ch[3],));assert comp.getchannel('A').tobytes()==source.getchannel('A').tobytes()
comp.save(S/'amber-neutral-compensated-v2.png')
imports=[]
def save(n,im):
 im.save(A/(n+'.png'));w=1<<(im.width-1).bit_length();h=1<<(im.height-1).bit_length();pad=Image.new('RGBA',(w,h));pad.paste(im,(0,0));pad.save(A/(n+'.tga'));imports.append(f'#exec TEXTURE IMPORT NAME={n} FILE="{(A/(n+".tga")).as_posix()}" MIPS=OFF ALPHATEXTURE=1')
# Resize first and then invert: the correction targets the pixels sampled by the UI.
orig=source.resize((320,400),Image.Resampling.LANCZOS);rgb=orig.split();small=Image.merge('RGBA',tuple(c.point(inverse) for c in rgb[:3])+(rgb[3],));save('PortraitComp',small)
src=Image.open(B/'external/dark-ui-free-demo/Standard_Button_orange.png').convert('RGBA')
def nine(im,W,H,b=10):
 w,h=im.size;o=Image.new('RGBA',(W,H));xx=[0,b,w-b,w];yy=[0,b,h-b,h];dx=[0,b,W-b,W];dy=[0,b,H-b,H]
 for i in range(3):
  for j in range(3):o.paste(im.crop((xx[i],yy[j],xx[i+1],yy[j+1])).resize((dx[i+1]-dx[i],dy[j+1]-dy[j]),Image.Resampling.LANCZOS),(dx[i],dy[j]))
 return o
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',11)
for n,label,w in [('Original','Original',82),('Compensate','Compensar',92)]:
 for state,factor in [('Up',1.),('Over',1.25),('Down',.75)]:
  im=ImageEnhance.Brightness(nine(src,w,28)).enhance(factor);ImageDraw.Draw(im).text((w/2,14),label,font=font,anchor='mm',fill=(255,239,203),stroke_width=1,stroke_fill=(20,10,5));save(n+state,im)
E=R/'research/amber-l2/tools/l2editor/L2Editor';classes=E.parent/P/'Classes';classes.mkdir(parents=True,exist_ok=True);(classes/'Assets.uc').write_text('class Assets extends Object;\n'+'\n'.join(imports)+'\ndefaultproperties {}\n',encoding='ascii')
(E/(P+'.ini')).write_text((E/'UT2003.ini').read_text(encoding='latin1')+f'\n[Editor.EditorEngine]\nEditPackages=Core\nEditPackages=Engine\nEditPackages={P}\n',encoding='latin1')
if (E/(P+'.u')).exists():(E/(P+'.u')).unlink()
r=subprocess.run([str(E/'UCC.exe'),'make','-Silent','-NoBind','ini='+P+'.ini'],cwd=E,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW);(S/'ucc.log').write_bytes(r.stdout+r.stderr);assert r.returncode==0
raw=S/(P+'.raw.u');shutil.copy2(E/(P+'.u'),raw);codec=R/'tools/open-l2encdec-1.3.9/l2encdec_win.exe'
def crypt(*args):
 r=subprocess.run([str(codec),*map(str,args)],input=b'\n',capture_output=True,timeout=30);assert r.returncode==0
crypt('-c','encode','-p','121','-f',P+'.u','-o',S/(P+'.u'),raw);crypt('-c','decode','-f',P+'.u','-o',S/'roundtrip.raw',S/(P+'.u'));assert raw.read_bytes()==(S/'roundtrip.raw').read_bytes()
b=(S/(P+'.u')).read_bytes();assert struct.unpack_from('<I',b,len(b)-8)[0]==zlib.crc32(b[:-20])
builder=(V1/'build-interface.groovy').read_text()
builder=builder.replace("new File(stage,'current/Interface.u')","new File('"+(V1/'current/Interface.u').as_posix()+"')")
builder=builder.replace("'ShowEnd':null,'OnEvent'","'ShowEnd':null,'UseOriginal':null,'UseCompensation':null,'OnEvent'")
builder=builder.replace("'ShowEnd']);up.addNameEntries","'ShowEnd','UseOriginal','UseCompensation','SetTexture']);up.addNameEntries")
builder=builder.replace("'NWindow.UIAPI_WINDOW':'Core.Class'","'NWindow.UIAPI_WINDOW':'Core.Class','NWindow.UIAPI_TEXTURECTRL':'Core.Class'")
builder=builder.replace("int resultType=0->","int resultType=0,String apiClass='NWindow.UIAPI_WINDOW'->").replace("nativeRef('NWindow.UIAPI_WINDOW')),call.getSize","nativeRef(apiClass)),call.getSize")
insert="""
 ['UseOriginal':'NexusAmberStoryV1.Portrait','UseCompensation':'NexusAmberGammaV2.PortraitComp'].each{fn,tex->
  make(fn,null){emit,guard,api,p->pages.each{win->emit(api('SetTexture',[new StringConst(win+'.Portrait'),new StringConst(tex)],0,'NWindow.UIAPI_TEXTURECTRL'))}}
 }
"""
builder=builder.replace(" make('OnClickButton','strID')",insert+" make('OnClickButton','strID')").replace("'Close':'CloseAll'].each","'Close':'CloseAll','Original':'UseOriginal','Compensate':'UseCompensation'].each")
builder=builder.replace('8 functions, 6 button routes','10 functions, 8 button routes')
(S/'build-interface.groovy').write_text(builder,encoding='utf-8')
java=R/'tools/jdk-25.0.4.1+1/bin/java.exe';cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(R/'tools/javafx-sdk-21.0.9/lib/*')
for script in [S/'build-interface.groovy',B/'build-gamma-xdat.groovy']:
 r=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(script),str(S)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120);(S/(script.stem+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;print(r.stdout.strip())
proof={'captured_curve_reference':'../../display-gamma-v1/rea-runtime-user-test.json','forward_16bit':forward,'inverse_8bit':inverse,'alpha_preserved':True,'neutral_config_installed':False,'scope':'Only Amber portrait in demo; no rectangle overlay or global gamma changes','black_floor_16bit':forward[0],'max_reproduction_error_8bit':max(abs(forward[inverse[y]]/257-y) for y in range(256)),'new_texture_package_roundtrip':True,'status':'prepared; game test pending'}
(S/'compensation.json').write_text(json.dumps(proof,indent=2))
# Expected output comparison, with the captured display curve simulated once.
def display(im):
 c=im.split();return Image.merge('RGBA',tuple(z.point([round(v/257) for v in forward]) for z in c[:3])+(c[3],))
sheet=Image.new('RGBA',(1000,450),(30,32,30,255));d=ImageDraw.Draw(sheet)
for im,x,label in [(orig,5,'Referencia'),(display(orig),340,'Con gamma L2'),(display(small),675,'Compensado + gamma L2')]:
 sheet.alpha_composite(im,(x,40));d.text((x+10,12),label,font=font,fill='white')
sheet.convert('RGB').save(S/'expected-compensation.png')
print('PREPARED: local inverse-gamma portrait with Original/Compensar buttons; no live settings changed.')
