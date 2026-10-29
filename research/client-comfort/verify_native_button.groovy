import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*

def stage=new File(args[0]);def client=new File(args[1])
def serializer=new UnrealSerializerFactory(new Environment(stage,['./*.u','../../../l2/system-hud/*.u','../../../l2/system/*.u']))
new UnrealPackage(new File(stage,'Interface.u'),true).withCloseable{up->
 def entry=up.exportTable.find{it.objectInnerFullName=='MagicSkillWnd.OnClickButton'}
 assert entry!=null
 def fn=serializer.getOrCreateObject(entry)
 assert fn.friendlyName=='OnClickButton'
 assert fn.child.entry.objectInnerFullName=='MagicSkillWnd.OnClickButton.strID'
 def ctx=new UnrealRuntimeContext(entry,serializer)
 def instructions=fn.bytecode.collect{it.toString(ctx)}
 assert instructions.join('\n').contains('RequestBypassToServer')
 assert instructions.join('\n').contains('voice .habilidades')
 def cls=serializer.getOrCreateObject(up.exportTable.find{it.objectInnerFullName=='MagicSkillWnd'})
 assert cls.child.entry.objectInnerFullName=='MagicSkillWnd.OnClickButton'
 println 'PASS: fresh package reload resolves new class callback, string parameter and server command.'
 instructions.each{println it}
}
