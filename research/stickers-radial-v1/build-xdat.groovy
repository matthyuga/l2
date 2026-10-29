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
def stage=new File(args[0]),source=new File(stage,'current/Interface.xdat'),out=new File(stage,'Interface.xdat'),x=new XDAT()
source.withInputStream{x.read(it)}
def bytes={node->def b=new ByteArrayOutputStream();node.write(b);b.toByteArray()}
assert Arrays.equals(bytes(x),source.bytes):'XDAT source roundtrip mismatch'
def previous=x.windows.collectEntries{[(it.name):bytes(it)]}
assert !x.windows.any{it.name in ['StickerRadialWnd','StickerLauncherWnd']}
def template=x.windows.find{it.name=='TutorialViewerWnd'}
def clone={->def w=new Window();w.read(new ByteArrayInputStream(bytes(template)));w.children=[];w}
def w=clone();w.name='StickerRadialWnd';w.unk102='StickerRadialUI';w.unk100='undefined';w.unk101='undefined';w.unk111=-9999
w.size_absolute_width=384;w.size_absolute_height=414
w.anchor_parent=Alignment.CENTER;w.anchor_this=Alignment.CENTER;w.anchor_ctrl='';w.anchor_x=0;w.anchor_y=0
w.children.add(new Texture(name:'Wheel',file:'NexusStickersV1.Wheel',alpha:255,size:true,size_absolute_values:true,size_absolute_width:384,size_absolute_height:384,anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:0,anchor_y:0))
def button={String name,int px,int py,int size,String stem->new Button(name:name,size:true,size_absolute_values:true,size_absolute_width:size,size_absolute_height:size,anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:px,anchor_y:py,normalTex:'NexusStickersV1.'+stem+'Up',pushedTex:'NexusStickersV1.'+stem+'Down',highlightTex:'NexusStickersV1.'+stem+'Over')}
(0..<8).each{i->double a=Math.PI*2*i/8-Math.PI/2;w.children.add(button('S'+i,Math.round(192+137*Math.cos(a)-42) as int,Math.round(192+137*Math.sin(a)-42) as int,84,'S'+i))}
w.children.add(button('Close',143,143,98,'Center'))
w.children.add(new TextBox(name:'Hint',text:'Elegir: clic   |   Cerrar: Esc / Alt+E',textAlign:TextBox.TextAlign.Center,textColor:javafx.scene.paint.Color.web('#d8c49b'),sysstring:-1,systemMsg:-1,backTex:'undefined',size:true,size_absolute_values:true,size_absolute_width:384,size_absolute_height:22,anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:0,anchor_y:389))
x.windows.add(w)
def launcher=clone();launcher.name='StickerLauncherWnd';launcher.unk102='StickerRadialUI';launcher.unk100='undefined';launcher.unk101='undefined';launcher.unk111=-9999
launcher.size_absolute_width=48;launcher.size_absolute_height=48
launcher.anchor_parent=Alignment.TOP_RIGHT;launcher.anchor_this=Alignment.TOP_RIGHT;launcher.anchor_ctrl='';launcher.anchor_x=-190;launcher.anchor_y=140
def open=button('Open',0,0,48,'Center');open.anchor_ctrl=launcher.name;launcher.children.add(open)
x.windows.add(launcher)
x.windows.each{node->if(previous.containsKey(node.name))assert Arrays.equals(previous[node.name],bytes(node)):'Previous window changed '+node.name}
out.bytes=bytes(x)
def check=new XDAT();out.withInputStream{check.read(it)};assert Arrays.equals(bytes(check),out.bytes)
assert check.windows.size()==previous.size()+2
println 'PASS: centered native radial window, 8 reactions, launcher button; all '+previous.size()+' previous windows byte identical; XDAT exact roundtrip.'
