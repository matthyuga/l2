import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def dir=new File(args[0]);def ser=new UnrealSerializerFactory(new Environment(dir,['./*.u','../system/*.u','../systextures/*.utx']))
new UnrealPackage(new File(dir,'Interface.u'),true).withCloseable{up->
 up.exportTable.findAll{e->e.fullClassName=='Core.Function'&&(e.objectInnerFullName.startsWith('MagicSkillWnd.')||e.objectInnerFullName=='SummonedWnd.OnClickButton'||e.objectInnerFullName.toLowerCase().contains('requestbypass'))}.each{e->
  def obj=ser.getOrCreateObject(e);println 'FUNCTION '+e.objectInnerFullName+' flags='+obj.functionFlags+' children='+obj.child?.entry?.objectInnerFullName
  def ctx=new UnrealRuntimeContext(e,ser);obj.bytecode.each{println '  '+it.toString(ctx)}
 }
}
