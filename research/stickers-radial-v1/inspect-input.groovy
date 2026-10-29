import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def dir=new File('E:/l2/system-hud'),ser=new UnrealSerializerFactory(new Environment(dir,['./*.u','../system/*.u','../systextures/*.utx']))
new UnrealPackage(new File(dir,'NWindow.u'),true).withCloseable {up->
 up.exportTable.findAll{it.fullClassName=='Core.Function'&&it.objectInnerFullName.matches('.*(Pos|Point|Over|Under|Hit|Focus|Tick|GetWindowHandle).*')}.each{e->println e.objectInnerFullName+' '+ser.getOrCreateObject(e).properties}
 up.exportTable.findAll{it.objectInnerFullName in ['UIEventManager.ScriptText','UIAPI_BUTTON.ScriptText']}.each{println ser.getOrCreateObject(it).text}
}
