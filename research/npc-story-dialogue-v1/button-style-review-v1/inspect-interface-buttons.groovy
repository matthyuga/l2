import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def root=new File('E:/l2/system-hud'),ser=new UnrealSerializerFactory(new Environment(root,['./*.u']))
new UnrealPackage(new File(root,'Interface.u'),true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName.contains('GetButtonHandle') && it.fullClassName=='Core.Function'}.each{e->
  def fn=ser.getOrCreateObject(e),f=fn.child;println e.objectInnerFullName
  while(f){println f.entry.objectInnerFullName+':'+f.entry.fullClassName;f=f.next}
  fn.bytecode.each{println it.toString(new UnrealRuntimeContext(e,ser))}
 }
}
