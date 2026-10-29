import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
def client=new File(args[0]),ser=new UnrealSerializerFactory(new Environment(client,['./*.u','../system/*.u','../systextures/*.utx']))
new UnrealPackage(new File(client,'Interface.u'),true).withCloseable{up->
 int count=0
 for(def e:up.exportTable.findAll{it.fullClassName=='Core.Function'}){
  try{
   def f=ser.getOrCreateObject(e),ctx=new UnrealRuntimeContext(e,ser)
   def text=f.bytecode.collect{it.toString(ctx)}
   if(text.any{it.contains('.ClassID = 0')} && text.any{it.contains('.static.AddItem(')}){
    println e.objectInnerFullName;text.each{println it};if(++count>=3)break
   }
  }catch(Exception ex){}
 }
 println 'Examples='+count
}
