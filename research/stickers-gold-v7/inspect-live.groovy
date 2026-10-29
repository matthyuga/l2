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
def x=new XDAT();new File('E:/l2/system-hud/Interface.xdat').withInputStream{x.read(it)}
['StickerRadialWnd','StickerLauncherWnd','ChatWnd','AmberStoryWelcomeWnd'].each{n->def w=x.windows.find{it.name==n};if(w){
 println n+' '+w.properties.findAll{k,v->k!='children' && k!='class'}
 if(n.startsWith('Sticker'))w.children.each{println it.properties}
}}
