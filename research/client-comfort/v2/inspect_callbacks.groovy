import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import acmi.l2.clientmod.unreal.UnrealRuntimeContext

def client=new File(args[0])
def serializer=new UnrealSerializerFactory(Environment.fromIni(new File(client,'l2.ini')))
new UnrealPackage(new File(client,'Interface.u'),true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName==~/(?i)(PetWnd|PetSkillWnd|PetInfoWnd|PetActionWnd|SummonWnd|SummonInfoWnd|SummonedWnd).*/}.each{e->
  println "ENTRY ${e.objectInnerFullName} ${e.fullClassName}"
  if(e.fullClassName=='Core.Function'){
   try{def obj=serializer.getOrCreateObject(e);def ctx=new UnrealRuntimeContext(e,serializer)
    obj.bytecode.each{println '  '+it.toString(ctx)}
   }catch(Exception ex){println 'DECODE FAILED '+ex.message}
  }
 }
}
