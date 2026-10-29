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
def previous=x.windows.collectEntries{[(it.name):bytes(it)]},changed=['StickerRadialWnd','StickerLauncherWnd']
def w=x.windows.find{it.name=='StickerRadialWnd'},launcher=x.windows.find{it.name=='StickerLauncherWnd'},chat=x.windows.find{it.name=='ChatWnd'}
assert w && launcher && chat && w.unk102=='StickerRadialUI' && launcher.unk102=='StickerRadialUI'
assert w.size_absolute_width==384 && w.size_absolute_height==414
def originalButtons=w.children.findAll{it instanceof Button}.collectEntries{[(it.name):[x:it.anchor_x,y:it.anchor_y,width:it.size_absolute_width,height:it.size_absolute_height]]}
assert originalButtons.size()==9
int originalHeight=w.size_absolute_height,originalY=w.anchor_y
w.size_absolute_height+=24;w.anchor_y-=12
w.children.each{it.anchor_y+=24}
def wheel=w.children.find{it.name=='Wheel'};assert wheel instanceof Texture
wheel.file='NexusStickerGoldV7.Wheel'
w.children.findAll{it instanceof Button}.each{b->
 def stem=b.name=='Close'?'Center':b.name
 b.normalTex='NexusStickerGoldV7.'+stem+'Up';b.pushedTex='NexusStickerGoldV7.'+stem+'Down';b.highlightTex='NexusStickerGoldV7.'+stem+'Over'
 def old=originalButtons[b.name]
 assert b.anchor_x==old.x && b.size_absolute_width==old.width && b.size_absolute_height==old.height
 assert w.anchor_y-w.size_absolute_height/2+b.anchor_y==originalY-originalHeight/2+old.y:'Screen anchor changed: '+b.name
}
def tex={n,px,py,width,height->new Texture(name:n,file:'NexusStickerGoldV7.'+n,type:Texture.TextureCtrlType.Normal,alpha:255,u:0,v:0,uSize:width,vSize:height,size:true,size_absolute_values:true,size_absolute_width:width,size_absolute_height:height,anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:px,anchor_y:py)}
w.children.add(1,tex('Title',108,0,168,24));w.children.add(2,tex('HintPlate',84,411,216,24))
def hint=w.children.find{it.name=='Hint'};assert hint instanceof TextBox
hint.text='Elegir: clic · Cerrar: centro'
changed.each{n->def win=x.windows.find{it.name==n};win.unk107=chat.unk107;win.unk109=chat.unk109}
def open=launcher.children.find{it.name=='Open'};assert open instanceof Button
open.normalTex='NexusStickerGoldV7.OpenUp';open.pushedTex='NexusStickerGoldV7.OpenDown';open.highlightTex='NexusStickerGoldV7.OpenOver'
w.children.each{assert it.anchor_x>=0 && it.anchor_y>=0 && it.anchor_x+it.size_absolute_width<=384 && it.anchor_y+it.size_absolute_height<=438:it.name}
def buttons=w.children.findAll{it instanceof Button}
buttons.eachWithIndex{a,i->buttons.drop(i+1).each{b->assert !(a.anchor_x < b.anchor_x+b.size_absolute_width && a.anchor_x+a.size_absolute_width > b.anchor_x && a.anchor_y < b.anchor_y+b.size_absolute_height && a.anchor_y+a.size_absolute_height > b.anchor_y):'Button overlap'}}
x.windows.each{if(!changed.contains(it.name))assert Arrays.equals(previous[it.name],bytes(it)):'Other window changed: '+it.name}
new File(s,'Interface.xdat').bytes=bytes(x)
def fresh=new XDAT();new File(s,'Interface.xdat').withInputStream{fresh.read(it)};assert Arrays.equals(bytes(fresh),bytes(x));assert fresh.windows.size()==previous.size()
println 'PASS: only 2 sticker windows changed; '+(previous.size()-2)+' other windows byte identical; all 9 radial hitbox screen anchors/sizes preserved, no overlap; exact XDAT roundtrip.'
