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
def source=new File(args[0]),out=new File(args[1]),x=new XDAT();source.withInputStream{x.read(it)}
def raw=new ByteArrayOutputStream();x.write(raw);assert Arrays.equals(raw.toByteArray(),source.bytes)
def preserved=x.windows.collectEntries{w->def b=new ByteArrayOutputStream();w.write(b);[(w.name):b.toByteArray()]}
def w=x.windows.find{it.name=='MagicSkillWnd'}
assert w.children.any{it.name=='ClassAll'} && !w.children.any{it.name=='ClassNext'}
w.children.removeAll{it instanceof TextBox && it.name in ['ClassMainLabel','ClassSub1Label','ClassSub2Label','ClassSub3Label','ClassCommonLabel','ClassAmberLabel','ClassAllLabel','ClassesButtonLabel']}
w.children.findAll{it instanceof Button && it.name.startsWith('Class')}.each{b->
 b.normalTex='SkillGroupsV3.'+b.name+'Up';b.pushedTex='SkillGroupsV3.'+b.name+'Down';b.highlightTex='SkillGroupsV3.'+b.name+'Over'
}
def index=w.children.find{it.name=='ClassesButton'};index.anchor_y=427;index.size_absolute_width=190
w.children.add(new Button(name:'ClassNext',size:true,size_absolute_values:true,size_absolute_width:232,size_absolute_height:23,
 anchor:true,anchor_parent:Alignment.TOP_LEFT,anchor_this:Alignment.TOP_LEFT,anchor_ctrl:w.name,anchor_x:12,anchor_y:397,
 normalTex:'SkillGroupsV3.ClassNextUp',pushedTex:'SkillGroupsV3.ClassNextDown',highlightTex:'SkillGroupsV3.ClassNextOver'))
w.children.find{it.name=='AmberAssistButton'}.anchor_y=423
w.size_absolute_height=460
['ASkill','PSkill'].each{name->
 def item=w.children.find{it.name==name}.children.find{it instanceof ItemWindow}
 println name+' old grid '+[item.iconWidth,item.iconHeight,item.gapX,item.gapY,item.offsetX,item.offsetY]
 item.iconWidth=32;item.iconHeight=32;item.gapX=0;item.gapY=2;item.offsetX=12
 assert item.col==6 && item.maxItemNum>=2048
}
x.windows.each{node->if(node.name!='MagicSkillWnd'){def b=new ByteArrayOutputStream();node.write(b);assert Arrays.equals(preserved[node.name],b.toByteArray()):node.name}}
out.withOutputStream{x.write(it)}
def v=new XDAT();out.withInputStream{v.read(it)};def rt=new ByteArrayOutputStream();v.write(rt);assert Arrays.equals(rt.toByteArray(),out.bytes)
println 'PASS: native labelled buttons have no text overlay, Next class, contiguous 6-column separators, other windows identical.'
