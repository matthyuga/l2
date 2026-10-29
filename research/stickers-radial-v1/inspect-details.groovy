import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.core.TextBuffer
def dir=new File('E:/l2/system-hud'),ser=new UnrealSerializerFactory(new Environment(dir,['./*.u','../system/*.u','../systextures/*.utx']))
for(String pkg : ['Engine.u','NWindow.u','Interface.u']) {
 new UnrealPackage(new File(dir,pkg),true).withCloseable { up ->
  def names=[]
  if(pkg=='Engine.u') names=['SkillAction.ScriptText','SkillAction_LocateEffect.ScriptText','SkillVisualEffect.ScriptText']
  if(pkg=='NWindow.u') names=['UIScript.OnKeyDown','UIScript.OnKeyUp','UIScript.IsKeyDown','UIScript.OnTimer','UIScript.ScriptText','UIAPI_WINDOW.ScriptText','WindowHandle.ScriptText']
  if(pkg=='Interface.u') names=['TutorialViewerWnd.OnLoad','TutorialViewerWnd.OnEvent','UICommonAPI.ScriptText','ShortcutWnd.ScriptText']
  names.each { n ->
   def e=up.exportTable.find{it.objectInnerFullName==n}
   if(e) {
    def o=ser.getOrCreateObject(e)
    println '\nOBJECT '+pkg+' '+n
    if(o instanceof TextBuffer) { println o.text }
    else {
     println o.properties
     def ctx=new UnrealRuntimeContext(e,ser)
     o.bytecode.each { println it.toString(ctx) }
    }
   }
  }
 }
}
