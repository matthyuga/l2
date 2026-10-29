import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def dir=new File('E:/l2-local/research/stickers-radial-v1')
new UnrealPackage(new File(dir,'Interface.u'),true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName.startsWith('StickerRadialUI')}.reverse().each{e->
  println e.objectInnerFullName+' type='+e.fullClassName+' super='+e.objectSuperClass+' flags='+e.objectFlags+' size='+e.objectRawData.length+' hex='+Arrays.copyOf(e.objectRawData,Math.min(100,e.objectRawData.length)).encodeHex()
  try{def f=new UnrealSerializerFactory(new Environment(dir,['./*.u','../../../l2/system-hud/*.u','../../../l2/system/*.u']));def o=f.getOrCreateObject(e);println 'READ '+o.properties}catch(Throwable ex){println 'FAILED '+e.objectInnerFullName+' '+ex}
 }
}
