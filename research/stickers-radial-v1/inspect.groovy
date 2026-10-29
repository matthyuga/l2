import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def dir=new File('E:/l2/system-hud'), ser=new UnrealSerializerFactory(new Environment(dir,['./*.u','../system/*.u','../systextures/*.utx']))
for(String pkg:['Engine.u','NWindow.u','Interface.u'])new UnrealPackage(new File(dir,pkg),true).withCloseable{up->
 println 'PACKAGE '+pkg
 if(pkg=='Engine.u')up.exportTable.findAll{it.fullClassName=='Core.Class'&&it.objectInnerFullName.startsWith('SkillAction')}.each{e->println 'CLASS '+e.objectInnerFullName;println ser.getOrCreateObject(e).properties}
 if(pkg=='NWindow.u')up.exportTable.findAll{it.fullClassName=='Core.Function'&&it.objectInnerFullName.matches('.*(Key|Cursor|Mouse|Window|Show|Hide|Focus|Timer|Execute).*')}.each{println 'API '+it.objectInnerFullName}
 if(pkg=='Interface.u'){
 up.exportTable.findAll{it.fullClassName=='Core.Function'&&it.objectInnerFullName.matches('.*(OnKey.*|OnMouse.*|OnLButton.*|OnRButton.*)')}.each{e->println 'INPUT '+e.objectInnerFullName;def o=ser.getOrCreateObject(e);println o.properties;def ctx=new UnrealRuntimeContext(e,ser);o.bytecode.each{println it.toString(ctx)}}
 for(String n:['UICommonAPI','MagicSkillWnd','HelpWnd','TutorialViewerWnd']){def e=up.exportTable.find{it.objectInnerFullName==n};if(e)println 'CLASS '+n+' '+ser.getOrCreateObject(e).properties}
 }
}
