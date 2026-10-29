import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
for(File eng:[new File('E:/l2/system-hud/Engine.u'),new File('E:/l2-local/research/amber-l2/tools/l2editor/L2Editor/Engine.u')]){
 println 'ENGINE '+eng
 def f=new UnrealSerializerFactory(new Environment(eng.parentFile,['*.u']))
 new UnrealPackage(eng,true).withCloseable{up->
  up.exportTable.findAll{it.fullClassName=='Core.Enum'&&it.objectInnerFullName==~/(?i).*(ParticleDrawStyle|CoordinateSystem|DirectionUsage).*/}.each{e->println e.objectInnerFullName+' '+f.getOrCreateObject(e).values}
 }
}
