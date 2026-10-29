import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def client=new File(args[0]),f=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
new UnrealPackage(new File(client,'system-hud/Engine.u'),true).withCloseable{up->
 for(String name:['Emitter','SpriteEmitter']){
  println 'DEFAULT '+name
  f.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name}).@properties.each{println it.name+'='+it.value}
 }
}
new UnrealPackage(new File(client,'system-hud/LineageEffect.u'),true).withCloseable{up->
 def entry=up.exportTable.find{it.objectInnerFullName=='it_soul_shot_d_ca'}
 println 'NATIVE '+entry
 def o=f.getOrCreateObject(entry)
 o.@properties.each{println it.name+'='+it.value}
 def emitters=o.@properties.find{it.name=='Emitters'}?.getAt(0)
 emitters?.take(2)?.each{ref->
  println 'PARTICLE '+up.objectReference(ref).objectFullName
  f.getOrCreateObject(up.objectReference(ref)).@properties.each{println it.name+'='+it.value}
 }
 up.exportTable.findAll{it.fullClassName=='Core.Class'&&it.objectInnerFullName==~/(?i).*(arrow|rain|flame|blaze|fire|ring).*/}.take(55).each{println 'CLASS '+it.objectInnerFullName}
}
