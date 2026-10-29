import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def stage=new File(args[0]),editor=new File(stage.parentFile.parentFile,'research/amber-l2/tools/l2editor/L2Editor')
java.util.logging.Logger.getLogger('').level=java.util.logging.Level.OFF
def ser=new UnrealSerializerFactory(new Environment(editor,['./*.u']))
new UnrealPackage(new File(stage,'NexusStickersV3.raw.u'),true).withCloseable{up->
 println 'FLAGNAMES '+up.nameTable.findAll{it.name.toLowerCase().contains('alpha')||it.name in ['None','Format','USize','VSize']}.collect{[it.index,it.name]}
 ['Wheel','S0Up','CenterUp','OpenUp','Reaction0'].each{n->def e=up.exportTable.find{it.objectInnerFullName==n},o=ser.getOrCreateObject(e);println n+' '+o.@properties.collectEntries{[(it.name):it.getAt(0)]};println 'RAW '+Arrays.copyOf(e.objectRawData,80).encodeHex();println 'mip '+o.mipMaps[0].properties.findAll{k,v->k!='data'&&k!='class'}}
}
