import ct0.XDAT
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
use(IOUtil){
 def xdat=new XDAT();new File(args[0]).withInputStream{xdat.read(it)}
 def dump;dump={node,depth->
  println '  '*depth+node.class.simpleName+' '+node.name+' '+node.properties.findAll{k,v->!(v instanceof Collection)&&k in ['col','row','maxItemNum','size_absolute_width','size_absolute_height','anchor_x','anchor_y','noItemDrag','superName','script','buttonName','text','fontName','defaultText','parentName']}
  if(node.hasProperty('children'))node.children.each{dump(it,depth+1)}
 }
 xdat.windows.findAll{it.name==~/(?i).*Skill.*/}.each{dump(it,0)}
 def out=new ByteArrayOutputStream();xdat.write(out);println 'ROUNDTRIP='+Arrays.equals(new File(args[0]).bytes,out.toByteArray())
}
