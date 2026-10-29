import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def f=new UnrealSerializerFactory(Environment.fromIni(new File('E:/l2/system-hud/l2.ini')))
new UnrealPackage(new File('E:/l2/system-hud/Engine.u'),true).withCloseable{up->
 for(String name:['ParticleEmitter','SpriteEmitter']){
 def e=up.exportTable.find{it.objectInnerFullName==name};def o=f.getOrCreateObject(e);println name
 o.@properties.each{println it.name+'='+it.value}
 }
 up.exportTable.findAll{it.objectInnerFullName==~/.*\.(UniformSize|UseRegularSizeScale|UseDirectionAs|StartSizeRange|UseSizeScale)/}.each{println it.objectInnerFullName+' '+it.fullClassName}
}
