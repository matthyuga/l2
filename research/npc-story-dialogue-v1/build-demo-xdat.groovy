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
def s=new File(args[0]),x=new XDAT(),source=new File(s,'current/Interface.xdat')
source.withInputStream{x.read(it)}
def bytes={node->def o=new ByteArrayOutputStream();node.write(o);o.toByteArray()}
assert Arrays.equals(bytes(x),source.bytes)
def previous=x.windows.collectEntries{[(it.name):bytes(it)]}
assert !x.windows.any{it.name.startsWith('AmberStory')}
def template=x.windows.find{it.name=='TutorialViewerWnd'}
def clone={String name->
 def w=new Window();w.read(new ByteArrayInputStream(bytes(template)));w.children=[]
 w.name=name;w.unk102='AmberStoryDemoUI';w.unk111=-9999
 // Use the chrome switches of the native chat container; retain all other window fields.
 def chat=x.windows.find{it.name=='ChatWnd'};w.unk107=chat.unk107;w.unk109=chat.unk109
 w.size_absolute_width=810;w.size_absolute_height=440;w.anchor_parent=Alignment.BOTTOM_CENTER;w.anchor_this=Alignment.BOTTOM_CENTER;w.anchor_ctrl='';w.anchor_x=0;w.anchor_y=-40
 w
}
def anchor={o,w,int px,int py,int width,int height->o.size=true;o.size_absolute_values=true;o.size_absolute_width=width;o.size_absolute_height=height;o.anchor=true;o.anchor_parent=Alignment.TOP_LEFT;o.anchor_this=Alignment.TOP_LEFT;o.anchor_ctrl=w.name;o.anchor_x=px;o.anchor_y=py;o}
def texture={w,n,tex,px,py,width,height->anchor(new Texture(name:n,file:'NexusAmberStoryV1.'+tex,type:Texture.TextureCtrlType.Normal,alpha:255,u:0,v:0,uSize:width,vSize:height),w,px,py,width,height)}
def text={w,n,value,px,py,width,color->anchor(new TextBox(name:n,text:value,textAlign:TextBox.TextAlign.Left,textColor:javafx.scene.paint.Color.web(color),sysstring:-1,systemMsg:-1,backTex:'undefined'),w,px,py,width,24)}
def button={w,n,px,py,width,height->anchor(new Button(name:n,normalTex:'NexusAmberStoryV1.'+n+'Up',pushedTex:'NexusAmberStoryV1.'+n+'Down',highlightTex:'NexusAmberStoryV1.'+n+'Over'),w,px,py,width,height)}
def pages=[
 [name:'AmberStoryWelcomeWnd',lines:['Hola. ¿Necesitás ayuda?'],choices:true],
 [name:'AmberStoryPlaceWnd',lines:['Tengo algunas cosas que contarte.','¿Por dónde querés empezar?']],
 [name:'AmberStoryGreetingWnd',lines:['¡Entonces me alegra verte!','Volvé cuando quieras hablar.']],
 [name:'AmberStoryEndWnd',lines:['Nos vemos pronto.'],ending:true]
]
pages.each{page->
 def w=clone(page.name)
 w.children<<texture(w,'Panel','Panel',310,150,480,260)
 w.children<<texture(w,'Portrait','Portrait',10,10,320,400)
 w.children<<text(w,'Speaker','AMBER',335,174,370,'#f2d7a6')
 page.lines.eachWithIndex{line,i->w.children<<text(w,'Line'+i,line,335,212+i*26,405,'#f2e7d7')}
 w.children<<text(w,'Hint','Conversación de prueba',335,267,400,'#b9a98f')
 w.children<<button(w,'Close',746,164,30,28)
 if(page.choices){w.children<<button(w,'Explore',335,295,430,34);w.children<<button(w,'Greet',335,337,430,34)}
 else if(page.ending)w.children<<button(w,'Restart',590,337,170,36)
 else w.children<<button(w,'Next',590,337,170,36)
 x.windows<<w
}
def launcher=clone('AmberStoryLauncherWnd');launcher.size_absolute_width=70;launcher.size_absolute_height=34
launcher.anchor_parent=Alignment.TOP_RIGHT;launcher.anchor_this=Alignment.TOP_RIGHT;launcher.anchor_x=-245;launcher.anchor_y=145
launcher.children<<button(launcher,'Open',0,0,70,34);x.windows<<launcher
x.windows.each{if(previous.containsKey(it.name))assert Arrays.equals(previous[it.name],bytes(it)):'Previous window changed: '+it.name}
new File(s,'Interface.xdat').bytes=bytes(x)
def fresh=new XDAT();new File(s,'Interface.xdat').withInputStream{fresh.read(it)};assert Arrays.equals(bytes(fresh),bytes(x))
assert fresh.windows.size()==previous.size()+5
println 'PASS: 4 dialogue pages and 1 launcher; all '+previous.size()+' previous windows byte identical; exact XDAT roundtrip.'
