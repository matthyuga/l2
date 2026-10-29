import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def dir=new File(args[0]);def ser=new UnrealSerializerFactory(new Environment(dir,['./*.u','../system/*.u','../systextures/*.utx']))
for(String name:['NWindow.u','Interface.u','Core.u'])new UnrealPackage(new File(dir,name),true).withCloseable{up->
 up.exportTable.findAll{e->e.objectInnerFullName.contains('RequestBypassToServer')||e.objectInnerFullName=='UIScript.OnClickButton'||e.objectInnerFullName=='Core.Object.EqualEqual_StrStr'||e.objectInnerFullName=='MagicSkillWnd'}.each{e->def obj=ser.getOrCreateObject(e);println e.objectInnerFullName+' '+obj.properties.findAll{k,v->k in ['functionFlags','nativeIndex','superField','child','next']};if(obj.hasProperty('bytecode'))obj.bytecode.each{println it.class.simpleName+' '+it.toString(new UnrealRuntimeContext(e,ser))}}
 if(name=='Interface.u'){int count=0;up.exportTable.findAll{it.fullClassName=='Core.Function'}.each{e->try{def obj=ser.getOrCreateObject(e),ctx=new UnrealRuntimeContext(e,ser);if(obj.bytecode.any{it.toString(ctx).contains('RequestBypassToServer')}){println 'CALLER '+e.objectInnerFullName;obj.bytecode.each{println '  '+it.class.simpleName+' '+it.toString(ctx)};count++;if(count>=8)throw new Stop()}}catch(Stop s){throw s}catch(Exception ex){}}}
}
class Stop extends RuntimeException{}