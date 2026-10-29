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
def previous=x.windows.collectEntries{[(it.name):bytes(it)]};def changed=[]
x.windows.findAll{it.name.startsWith('AmberStory') && it.name!='AmberStoryLauncherWnd'}.each{w->
 changed<<w.name;w.children.find{it.name=='Portrait'}.file='NexusAmberGammaV2.PortraitComp'
 [['Original',557,82],['Compensate',646,92]].each{args->
  def n=args[0];w.children<<new Button(name:n,size:true,size_absolute_values:true,size_absolute_width:args[2],size_absolute_height:28,anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:args[1],anchor_y:168,normalTex:'NexusAmberGammaV2.'+n+'Up',highlightTex:'NexusAmberGammaV2.'+n+'Over',pushedTex:'NexusAmberGammaV2.'+n+'Down')
 }
}
assert changed.size()==4
x.windows.each{if(!changed.contains(it.name))assert Arrays.equals(previous[it.name],bytes(it))}
def target=new File(s,'Interface.xdat');target.bytes=bytes(x);def check=new XDAT();target.withInputStream{check.read(it)};assert Arrays.equals(bytes(check),target.bytes)
println 'PASS: 4 portrait paths and 8 comparison buttons updated; all other '+(previous.size()-4)+' windows byte identical; exact XDAT roundtrip.'
