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
def source=new File(args[0]),out=new File(args[1]),x=new XDAT()
source.withInputStream{x.read(it)}
def raw=new ByteArrayOutputStream();x.write(raw);assert Arrays.equals(raw.toByteArray(),source.bytes)
def preserved=x.windows.collectEntries{w->def b=new ByteArrayOutputStream();w.write(b);[(w.name):b.toByteArray()]}
def button={w,name,label,px,py,width->
 w.children.add(new Button(name:name,size:true,size_absolute_values:true,size_absolute_width:width,size_absolute_height:23,
  anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:px,anchor_y:py,
  normalTex:'L2UI_ch3.smallbutton2',pushedTex:'L2UI_ch3.smallbutton2_down',highlightTex:'L2UI_ch3.smallbutton2_over'))
 w.children.add(new TextBox(name:name+'Label',text:label,textAlign:TextBox.TextAlign.Center,textColor:javafx.scene.paint.Color.WHITE,
  sysstring:-1,systemMsg:-1,backTex:'undefined',size:true,size_absolute_values:true,size_absolute_width:width-4,size_absolute_height:17,
  anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:px+2,anchor_y:py+4))
}
def w=x.windows.find{it.name=='MagicSkillWnd'}
assert w.children.find{it.name=='ClassesButton'}!=null
w.children.removeAll{it.name in ['ClassesButton','ClassesLabel']}
w.size_absolute_height=434
w.children.add(new TextBox(name:'ClassGroupTitle',text:'Filtrar habilidades por clase',textColor:javafx.scene.paint.Color.GOLD,
 sysstring:-1,systemMsg:-1,backTex:'undefined',size:true,size_absolute_values:true,size_absolute_width:232,size_absolute_height:16,
 anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:12,anchor_y:325))
[['ClassMain','Principal'],['ClassSub1','Sub 1'],['ClassSub2','Sub 2'],['ClassSub3','Sub 3']].eachWithIndex{s,i->button(w,s[0],s[1],12+i*59,345,56)}
[['ClassCommon','Comunes'],['ClassAmber','Amber'],['ClassAll','Todas']].eachWithIndex{s,i->button(w,s[0],s[1],12+i*79,370,76)}
button(w,'ClassesButton','Nombres de clases / indice',12,399,190)
w.children.add(new Button(name:'AmberAssistButton',size:true,size_absolute_values:true,size_absolute_width:32,size_absolute_height:32,
 anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:211,anchor_y:395,
 normalTex:'AmberAssistIconsV1.Assist',pushedTex:'AmberAssistIconsV1.Assist',highlightTex:'AmberAssistIconsV1.Assist'))
def pet=x.windows.find{it.name=='SummonedWnd'};assert !pet.children.any{it.name=='AmberAssistButton'}
pet.size_absolute_height=244
pet.children.add(new Button(name:'AmberAssistButton',size:true,size_absolute_values:true,size_absolute_width:32,size_absolute_height:32,
 anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:pet.name,anchor_x:18,anchor_y:204,
 normalTex:'AmberAssistIconsV1.Assist',pushedTex:'AmberAssistIconsV1.Assist',highlightTex:'AmberAssistIconsV1.Assist'))
pet.children.add(new TextBox(name:'AmberAssistLabel',text:'IA Amber: clic ON / OFF',textColor:javafx.scene.paint.Color.GOLD,
 sysstring:-1,systemMsg:-1,backTex:'undefined',size:true,size_absolute_values:true,size_absolute_width:180,size_absolute_height:18,
 anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:pet.name,anchor_x:57,anchor_y:212))
x.windows.each{node->if(!(node.name in ['MagicSkillWnd','SummonedWnd'])){def b=new ByteArrayOutputStream();node.write(b);assert Arrays.equals(preserved[node.name],b.toByteArray()):node.name}}
out.withOutputStream{x.write(it)}
def v=new XDAT();out.withInputStream{v.read(it)};def rt=new ByteArrayOutputStream();v.write(rt);assert Arrays.equals(rt.toByteArray(),out.bytes)
println 'PASS: 7 direct class filters, named index, two visible AI icons; other windows byte identical; XDAT roundtrip.'
