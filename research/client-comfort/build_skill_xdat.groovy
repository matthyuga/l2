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
def source=new File(args[0]),out=new File(args[1]);def xdat=new XDAT()
source.withInputStream{xdat.read(it)}
def baseline=new ByteArrayOutputStream();xdat.write(baseline)
assert Arrays.equals(source.bytes,baseline.toByteArray()):'XDAT schema roundtrip mismatch'
def preserved=xdat.windows.collectEntries{w->def raw=new ByteArrayOutputStream();w.write(raw);[(w.name):raw.toByteArray()]}
def window=xdat.windows.find{it.name=='MagicSkillWnd'}
assert window!=null&&window.children.find{it.name=='ClassesButton'}==null
['ASkill','PSkill'].each{name->
 def child=window.children.find{it.name==name};def items=child.children.find{it instanceof ItemWindow}
 assert items.maxItemNum==80:'Unexpected skill capacity; review before patching.'
 items.maxItemNum=2048
}
// Keep the familiar draggable grids and tabs; add a class-index button below them.
window.size_absolute_height+=31
def button=new Button(name:'ClassesButton',size:true,size_absolute_values:true,size_absolute_width:232,size_absolute_height:24,
 anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:'MagicSkillWnd',anchor_x:12,anchor_y:325,
 normalTex:'L2UI_ch3.smallbutton2',pushedTex:'L2UI_ch3.smallbutton2_down',highlightTex:'L2UI_ch3.smallbutton2_over')
window.children.add(button)
def label=new TextBox(name:'ClassesLabel',text:'Clases / Amber',textAlign:TextBox.TextAlign.Center,textColor:javafx.scene.paint.Color.WHITE,
 sysstring:-1,systemMsg:-1,backTex:'undefined',size:true,size_absolute_values:true,size_absolute_width:210,size_absolute_height:18,
 anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:'MagicSkillWnd',anchor_x:23,anchor_y:330)
window.children.add(label)
xdat.windows.each{w->if(w.name!='MagicSkillWnd'){def raw=new ByteArrayOutputStream();w.write(raw);assert Arrays.equals(preserved[w.name],raw.toByteArray()):'Unrelated window changed: '+w.name}}
out.withOutputStream{xdat.write(it)}
def verified=new XDAT();out.withInputStream{verified.read(it)}
def roundtrip=new ByteArrayOutputStream();verified.write(roundtrip)
assert Arrays.equals(out.bytes,roundtrip.toByteArray())
println 'PASS: active/passive capacity 80 -> 2048 each; native class button added; all unrelated windows byte identical.'
