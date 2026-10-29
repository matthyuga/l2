from pathlib import Path
import hashlib,json,shutil,subprocess,struct,zlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont

B=Path(__file__).resolve().parent;R=B.parents[1];C=R.parent/'l2/system-hud'
S=B/'client-demo-button-styles-v5';A=S/'assets';A.mkdir(exist_ok=True)
P='NexusAmberButtonsV5';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (S/'installation.json').exists(),'Already applied: create a new layer'
(S/'current').mkdir(exist_ok=True);inputs={}
for n in ['Interface.u','Interface.xdat','NexusAmberAngularV3.u','NexusAmberGammaV2.u','NexusAmberStoryV1.u','NWindow.u']:
    src=C/n;dst=S/'current'/n
    if dst.exists():assert sha(dst)==sha(src),'Concurrent change: '+n
    else:shutil.copy2(src,dst)
    inputs[str(src)]=sha(src)
(S/'input-hashes.json').write_text(json.dumps(inputs,indent=2))
imports=[];font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',n)
def save(n,im):
    im.save(A/(n+'.png'));w,h=[1<<(v-1).bit_length() for v in im.size]
    pad=Image.new('RGBA',(w,h));pad.paste(im,(0,0));pad.save(A/(n+'.tga'))
    imports.append(f'#exec TEXTURE IMPORT NAME={n} FILE="{(A/(n+".tga")).as_posix()}" MIPS=OFF ALPHATEXTURE=1')

def bands(active):
    out=[]
    for i in np.flatnonzero(active):
        if not out or i-out[-1][1]>12:out.append([int(i),int(i)])
        else:out[-1][1]=int(i)
    assert len(out)==3,out
    return out
def resize_button(src,w,h,kind):
    if kind=='square':return src.resize((w,h),Image.Resampling.LANCZOS)
    sw=round(src.width*h/src.height)
    src=src.resize((sw,h),Image.Resampling.LANCZOS)
    cap=min(max(4,round(sw*(.13 if kind=='long' else .22))),w//3,(sw-1)//2)
    result=Image.new('RGBA',(w,h));result.paste(src.crop((0,0,cap,h)),(0,0))
    result.paste(src.crop((cap,0,sw-cap,h)).resize((w-2*cap,h),Image.Resampling.LANCZOS),(cap,0))
    result.paste(src.crop((sw-cap,0,sw,h)),(w-cap,0));return result

spec={'Explore':('Quiero conocer este lugar.',540,42,'long',13),'Greet':('Solo pasaba a saludar.',540,42,'long',13),'Next':('Continuar',170,34,'compact',12),'Restart':('Volver al inicio',170,34,'compact',12),'Close':('X',28,28,'square',14),'Opaque':('Opaco',80,28,'compact',11),'Semi':('Semi',80,28,'compact',11),'Clear':('Transparente',122,28,'compact',11),'Original':('Original',72,26,'compact',10),'Compensate':('Compensar',92,26,'compact',10)}
sources={};crop_info={}
for style in 'ABCD':
    sheet=Image.open(S/'sources'/(style+'.png')).convert('RGBA');alpha=np.asarray(sheet.getchannel('A'))
    assert alpha.min()==0 and alpha.max()==255 and (alpha==0).mean()>.3,'Expected real transparency'
    cols=bands((alpha>160).sum(axis=0)>10);rows=bands((alpha>160).sum(axis=1)>10)
    xx=[0]+[(cols[i][1]+cols[i+1][0])//2 for i in range(2)]+[sheet.width]
    yy=[0]+[(rows[i][1]+rows[i+1][0])//2 for i in range(2)]+[sheet.height]
    crop_info[style]=[];sources[style]={}
    for ri,state in enumerate(['Up','Over','Down']):
        for ci,kind in enumerate(['long','compact','square']):
            cell=sheet.crop((xx[ci],yy[ri],xx[ci+1],yy[ri+1]));bbox=cell.getchannel('A').point(lambda v:255 if v>64 else 0).getbbox();assert bbox
            # Packing crop only; keep all generated alpha inside the tight cell.
            bbox=(max(0,bbox[0]-2),max(0,bbox[1]-2),min(cell.width,bbox[2]+2),min(cell.height,bbox[3]+2))
            src=cell.crop(bbox);sources[style][kind,state]=src
            crop_info[style].append(dict(state=state,kind=kind,cell=[xx[ci],yy[ri],xx[ci+1],yy[ri+1]],bbox=list(bbox)))
    for name,(label,w,h,kind,size) in spec.items():
        for state in ['Up','Over','Down']:
            im=resize_button(sources[style][kind,state],w,h,kind);d=ImageDraw.Draw(im)
            d.text((w/2,h/2+(1 if state=='Down' else 0)),label,font=font(size),anchor='mm',fill=(39,28,19,255) if style=='B' else (250,239,215,255),stroke_width=0 if style=='B' else 1,stroke_fill=(15,12,16,235))
            save(style+name+state,im)
    for state in ['Up','Over','Down']:
        im=resize_button(sources[style]['compact',state],100,28,'compact');d=ImageDraw.Draw(im)
        d.text((50,14),{'A':'A Metal','B':'B Papel','C':'C Cristal','D':'D Oro'}[style],font=font(11),anchor='mm',fill='#251b11' if style=='B' else '#faefd7')
        save('Style'+style+state,im)
    badge=Image.new('RGBA',(68,24),(15,20,23,220));d=ImageDraw.Draw(badge);d.text((34,12),'Actual: '+style,font=font(10),anchor='mm',fill='#eed4a4');save('Current'+style,badge)
(S/'crops.json').write_text(json.dumps(crop_info,indent=2))

# Reuse the verified native compiler for the generated, cropped and labelled sprites.
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

# Append a fresh script class; existing serialized classes remain byte identical.
builder=(B/'client-demo-angular-v3/build-interface.groovy').read_text(encoding='utf8').replace('AmberAngularUI','AmberButtonStylesUI')
builder=builder.replace("'UseClear':null,'OnEvent'","'UseClear':null,'UseStyleA':null,'UseStyleB':null,'UseStyleC':null,'UseStyleD':null,'OnEvent'")
builder=builder.replace("'UseClear','SetTexture'","'UseClear','UseStyleA','UseStyleB','UseStyleC','UseStyleD','SetTexture'")
builder=builder.replace("'NWindow.UIAPI_TEXTURECTRL':'Core.Class'","'NWindow.UIAPI_TEXTURECTRL':'Core.Class','NWindow.ButtonHandle':'Core.Class','NWindow.ButtonHandle.SetTexture':'Core.Function','NWindow.UIScript.GetHandle':'Core.Function'")
needle="  body(emit,guard,api,param==null?null:new LocalVariable(param.entry.objectReference))"
replacement="""
  def buttonApi={String path,List tex->
   def handle=new DynamicCast(nativeRef('NWindow.ButtonHandle'),new FinalFunction(nativeRef('NWindow.UIScript.GetHandle'),new StringConst(path)))
   def call=new FinalFunction(nativeRef('NWindow.ButtonHandle.SetTexture'),tex.collect{new StringConst(it)} as Token[])
   new acmi.l2.clientmod.unreal.bytecode.token.Context(handle,call.getSize(context),0,call)
  }
  body(emit,guard,api,param==null?null:new LocalVariable(param.entry.objectReference),buttonApi)
"""
assert needle in builder;builder=builder.replace(needle,replacement).replace('{emit,guard,api,p->','{emit,guard,api,p,buttonApi->')
insert="""
 ['A','B','C','D'].each{style->
  make('UseStyle'+style,null){emit,guard,api,p,buttonApi->
   pages.eachWithIndex{win,i->
    def controls=['Close','Original','Compensate','Opaque','Semi','Clear']
    if(i==0){controls.addAll(['Explore','Greet'])}else{controls.add(i==3 ? 'Restart' : 'Next')}
    controls.each{n->emit(buttonApi(win+'.'+n,['Up','Down','Over'].collect{'NexusAmberButtonsV5.'+style+n+it}))}
    emit(api('SetTexture',[new StringConst(win+'.StyleBadge'),new StringConst('NexusAmberButtonsV5.Current'+style)],0,'NWindow.UIAPI_TEXTURECTRL'))
   }
  }
 }
"""
builder=builder.replace(" make('OnClickButton','strID')",insert+" make('OnClickButton','strID')")
builder=builder.replace("'Clear':'UseClear'].each","'Clear':'UseClear','StyleA':'UseStyleA','StyleB':'UseStyleB','StyleC':'UseStyleC','StyleD':'UseStyleD'].each")
builder=builder.replace('13 functions, 11 button routes','17 functions, 15 button routes')
(S/'build-interface.groovy').write_text(builder,encoding='utf8')

java=R/'tools/jdk-25.0.4.1+1/bin/java.exe';cp=str(R/'tools/XDAT_NEW/xdat_editor/dist/*')+';'+str(R/'tools/javafx-sdk-21.0.9/lib/*')
for script in [S/'build-interface.groovy',B/'build-button-styles-xdat.groovy',B/'verify-button-styles.groovy']:
    p=subprocess.run([str(java),'-cp',cp,'groovy.ui.GroovyMain',str(script),str(S)],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=300)
    (S/(script.stem+'.log')).write_text(p.stdout+p.stderr,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr;print(p.stdout.strip())

(S/'output-hashes.json').write_text(json.dumps({n:sha(S/n) for n in [P+'.u','Interface.u','Interface.xdat']},indent=2))
(S/'build-verification.json').write_text(json.dumps(dict(texture_package_roundtrip=True,texture_crc=True,textures=len(imports),styles=list('ABCD'),default_style='A',background_and_portrait_controls_preserved=True,runtime_validation='pending'),indent=2))
print('BUILT: four native button families with selector and three button states.')
