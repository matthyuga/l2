import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def client=new File(args[0]);def serializer=new UnrealSerializerFactory(Environment.fromIni(new File(client,'l2.ini')))
for(String file:['Interface.u','NWindow.u','Engine.u'])new UnrealPackage(new File(client,file),true).withCloseable{up->
 println file
 if(file=='Interface.u'){
  def e=up.exportTable.find{it.objectInnerFullName=='MagicSkillWnd.ScriptText'}
  try{println serializer.getOrCreateObject(e).text}catch(Exception ex){println ex.message}
 }
 up.exportTable.findAll{it.objectInnerFullName==~/(?i)(UIAPI_ITEMWINDOW\..*|LineagePlayerController\.(.*Zoom.*|.*Camera.*)|.*SkillList.*)/}.each{println "API ${it.objectInnerFullName} ${it.fullClassName}"}
}
