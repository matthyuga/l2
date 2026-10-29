import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def s=new File(args[0]);def ser=new UnrealSerializerFactory(new Environment(new File('E:/l2/system-hud'),['./*.u']))
new UnrealPackage(new File('E:/l2/system-hud/NexusStickersV3.u'),true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName.matches('Reaction\\d+')}.each{e->def t=ser.getOrCreateObject(e);println e.objectInnerFullName+' '+t.@properties.collectEntries{[(it.name):it.getAt(0)]}+' mips='+t.mipMaps.collect{it.data.length}}
 def e=up.exportTable.find{it.objectInnerFullName=='Sticker0.Icon'};def o=ser.getOrCreateObject(e);println 'Particle properties: '+o.@properties.collectEntries{[(it.name):it.getAt(0)]}
}
