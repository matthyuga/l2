import ct0.*
import acmi.l2.clientmod.util.IOUtil
ExpandoMetaClass.enableGlobally()
InputStream.metaClass.readInt={->IOUtil.readInt(delegate)}
InputStream.metaClass.readString={->IOUtil.readString(delegate)}
InputStream.metaClass.readFloat={->IOUtil.readFloat(delegate)}
InputStream.metaClass.readBoolean={->IOUtil.readBoolean(delegate)}
OutputStream.metaClass.writeInt={int n->IOUtil.writeInt(delegate,n)}
OutputStream.metaClass.writeString={String n->IOUtil.writeString(delegate,n)}
OutputStream.metaClass.writeFloat={float n->IOUtil.writeFloat(delegate,n)}
OutputStream.metaClass.writeBoolean={Boolean n->IOUtil.writeBoolean(delegate,n)}
def s=new File(args[0]),x=new XDAT();new File(s,'current/Interface.xdat').withInputStream{x.read(it)}
def bytes={o->def b=new ByteArrayOutputStream();o.write(b);b.toByteArray()}
assert Arrays.equals(bytes(x),new File(s,'current/Interface.xdat').bytes)
def previous=x.windows.collectEntries{[(it.name):bytes(it)]},changed=[]
def anchor={o,w,px,py,width,height->o.size=true;o.size_absolute_values=true;o.size_absolute_width=width;o.size_absolute_height=height;o.anchor=true;o.anchor_parent=Alignment.TOP_LEFT;o.anchor_this=Alignment.TOP_LEFT;o.anchor_ctrl=w.name;o.anchor_x=px;o.anchor_y=py;o}
def texture={w,n,tex,px,py,width,height->anchor(new Texture(name:n,file:tex,type:Texture.TextureCtrlType.Normal,alpha:255,u:0,v:0,uSize:width,vSize:height),w,px,py,width,height)}
def text={w,n,value,px,py,width,color->anchor(new TextBox(name:n,text:value,textAlign:TextBox.TextAlign.Left,textColor:javafx.scene.paint.Color.web(color),sysstring:-1,systemMsg:-1,backTex:'undefined'),w,px,py,width,24)}
def button={w,n,px,py,width,height->anchor(new Button(name:n,normalTex:'NexusAmberAngularV3.'+n+'Up',pushedTex:'NexusAmberAngularV3.'+n+'Down',highlightTex:'NexusAmberAngularV3.'+n+'Over'),w,px,py,width,height)}
def pages=[
 [name:'AmberStoryWelcomeWnd',lines:['Hola. ¿Necesitás ayuda?'],choices:true],
 [name:'AmberStoryPlaceWnd',lines:['Tengo algunas cosas que contarte.','¿Por dónde querés empezar?']],
 [name:'AmberStoryGreetingWnd',lines:['¡Entonces me alegra verte!','Volvé cuando quieras hablar.']],
 [name:'AmberStoryEndWnd',lines:['Nos vemos pronto.'],ending:true]
]
pages.each{page->
 def w=x.windows.find{it.name==page.name};assert w
 changed<<w.name;w.unk102='AmberAngularUI';w.size_absolute_width=920;w.size_absolute_height=440
 w.children=[]
 w.children<<texture(w,'Background','NexusAmberAngularV3.BackgroundSemi',295,140,610,280)
 w.children<<texture(w,'Frame','NexusAmberAngularV3.Frame',295,140,610,280)
 w.children<<texture(w,'Nameplate','NexusAmberAngularV3.Nameplate',320,150,280,40)
 w.children<<texture(w,'Portrait','NexusAmberGammaV2.PortraitComp',0,10,320,400)
 w.children<<text(w,'Speaker','AMBER',355,164,225,'#eed4a4')
 page.lines.eachWithIndex{line,i->w.children<<text(w,'Line'+i,line,330,205+i*26,540,'#f2e7d7')}
 w.children<<text(w,'Hint','Conversación de prueba',330,248,510,'#b9a98f')
 w.children<<text(w,'BackgroundLabel','Fondo:',330,380,60,'#cbbd9e')
 w.children<<button(w,'Close',862,152,28,28)
 w.children<<button(w,'Original',680,154,72,26)
 w.children<<button(w,'Compensate',758,154,92,26)
 w.children<<button(w,'Opaque',392,376,80,28)
 w.children<<button(w,'Semi',480,376,80,28)
 w.children<<button(w,'Clear',568,376,122,28)
 if(page.choices){w.children<<button(w,'Explore',330,278,540,34);w.children<<button(w,'Greet',330,320,540,34)}
 else if(page.ending)w.children<<button(w,'Restart',700,320,170,34)
 else w.children<<button(w,'Next',700,320,170,34)
 x.windows.findAll{it.name==page.name}.each{win->
  win.children.each{c->assert c.anchor_x>=0 && c.anchor_y>=0 && c.anchor_x+c.size_absolute_width<=920 && c.anchor_y+c.size_absolute_height<=440:c.name}
 }
}
def launcher=x.windows.find{it.name=='AmberStoryLauncherWnd'};assert launcher
launcher.unk102='AmberAngularUI';changed<<launcher.name
x.windows.each{if(!changed.contains(it.name))assert Arrays.equals(previous[it.name],bytes(it)):'Other window changed: '+it.name}
def target=new File(s,'Interface.xdat');target.bytes=bytes(x)
def check=new XDAT();target.withInputStream{check.read(it)};assert Arrays.equals(bytes(check),target.bytes)
assert check.windows.size()==previous.size()
assert changed.size()==5
println 'PASS: 4 dialogue pages and launcher updated; all other '+(previous.size()-5)+' windows byte identical; all controls within bounds; exact XDAT roundtrip.'
