import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def f=new UnrealSerializerFactory(Environment.fromIni(new File('E:/l2/system-hud/l2.ini')))
for(String path:['E:/l2/system-hud/LineageNPC.u','E:/l2/animations/L2AmberArcher.ukx','E:/l2/animations/LineageNpcs.ukx'])new UnrealPackage(new File(path),true).withCloseable{up->
 for(String name:['a_traderB_FHuman','a_traderB_FHuman.ScriptText','AmberNPC','a_traderB_FHuman_m00']){
  def e=up.exportTable.find{it.objectInnerFullName==name};if(!e)continue
  def obj=f.getOrCreateObject(e);println "ENTRY $name class=${obj.getClass().name}";println obj.@properties.collect{it.template.entry.objectInnerFullName+'='+it.value}
  println obj.getClass().declaredFields.collect{it.name}
  if(e.fullClassName=='Core.TextBuffer')println obj.text
 }
}
