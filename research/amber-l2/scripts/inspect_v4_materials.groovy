import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile
def factory=new UnrealSerializerFactory(new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v4/*.u','../l2/system-hud/*.u','../l2/system/*.u']))
new UnrealPackage(new File(root,'exports/contract/combat-vfx-v4/AmberParticlesV4.u'),true).withCloseable{up->
 for(String name:['AreaRing','AreaDisk','ArrowShot','ArrowSky']){
  def e=up.exportTable.find{it.objectInnerFullName==name},o=factory.getOrCreateObject(e)
  println name+' '+e.fullClassName+' fields='+o.class.fields*.name
  o.@properties.each{println it.name+'='+it.value}
  def material=o.@properties.find{it.name=='Materials'}.getAt(0)[0].find{it.name=='Material'}.getAt(0)
  println 'material='+material+' '+up.objectReference(material).objectFullName
  println 'rawPrefix='+e.objectRawData.toList().take(100).collect{String.format('%02x',it&255)}.join(' ')
 }
 up.exportTable.findAll{it.fullClassName=='Engine.Texture'}.each{println it.objectInnerFullName+' '+it.objectReference}
}
