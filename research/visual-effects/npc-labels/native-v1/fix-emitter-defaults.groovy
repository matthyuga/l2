import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def stage=new File(args[0]),fixdir=new File(stage,'fixed');fixdir.mkdirs()
def file=new File(fixdir,'HellgamesLabelsV1.u')
file.bytes=new File(stage,'HellgamesLabelsV1.u').bytes
def compact=AmberCatalog.&compact
new UnrealPackage(file,false).withCloseable{up->
 up.addNameEntries(['TriggerDisabled','Disabled','AlphaTest','LevelOfWeather'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 byte[] none=compact(up.nameReference('None'))
 up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}.each{e->
  byte[] raw=e.objectRawData
  assert Arrays.equals(Arrays.copyOfRange(raw,raw.length-none.length,raw.length),none)
  def out=new ByteArrayOutputStream();out.write(raw,0,raw.length-none.length)
  for(String name:['TriggerDisabled','Disabled','AlphaTest']){out.write(compact(up.nameReference(name)));out.write(0x03)}
  out.write(compact(up.nameReference('LevelOfWeather')));out.write(0x22);out.write([0,0,0,0] as byte[])
  out.write(none);e.setObjectRawData(out.toByteArray())
 }
}
def project=stage.parentFile.parentFile.parentFile.parentFile
def factory=new UnrealSerializerFactory(new Environment(project,['research/visual-effects/npc-labels/native-v1/fixed/*.u','../l2/system-hud/*.u']))
new UnrealPackage(file,true).withCloseable{up->
 up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}.each{e->
  def props=factory.getOrCreateObject(e).@properties.collectEntries{p->[(p.name):p.getAt(0)]}
  assert props.TriggerDisabled==false&&props.Disabled==false&&props.AlphaTest==false&&props.LevelOfWeather==0
  println 'PASS '+e.objectInnerFullName+': TriggerDisabled=false, Disabled=false, AlphaTest=false, LevelOfWeather=0'
 }
}
