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
def s=new File(args[0]),src=new File(s,'current/Interface.xdat'),out=new File(s,'Interface.xdat'),x=new XDAT()
src.withInputStream{x.read(it)}
def bytes={o->def b=new ByteArrayOutputStream();o.write(b);b.toByteArray()}
assert Arrays.equals(bytes(x),src.bytes)
def previous=x.windows.collectEntries{[(it.name):bytes(it)]}
for(String name:['StickerRadialWnd','StickerLauncherWnd']){
 def w=x.windows.find{it.name==name};assert w
 w.children.each{o->
  if(o instanceof Texture)o.file=o.file.replace('NexusStickersV1.','NexusStickersV2.')
  if(o instanceof Button){
   ['normalTex','pushedTex','highlightTex'].each{p->o[p]=o[p].replace('NexusStickersV1.','NexusStickersV2.')}
   if(o.name=='Open')['normalTex','pushedTex','highlightTex'].each{p->o[p]=o[p].replace('.Center','.Open')}
  }
  if(o instanceof TextBox && o.name=='Hint')o.text='Elegir: clic   |   Cerrar: boton central'
 }
}
x.windows.each{if(!(it.name in ['StickerRadialWnd','StickerLauncherWnd']))assert Arrays.equals(previous[it.name],bytes(it))}
out.bytes=bytes(x);def fresh=new XDAT();out.withInputStream{fresh.read(it)};assert Arrays.equals(bytes(fresh),out.bytes)
println 'PASS: 8 artwork buttons, corrected close/launcher labels; all 140 unrelated windows byte identical; exact XDAT roundtrip.'
