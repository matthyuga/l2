import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
def stage=new File(args[0]),client=new File(args[1])
def serializer=new UnrealSerializerFactory(new Environment(stage,['./*.u','../../../../l2/system-hud/*.u','../../../../l2/system/*.u']))
new UnrealPackage(new File(stage,'Interface.u'),true).withCloseable{up->
 def byName={n->up.exportTable.find{it.objectInnerFullName==n}}
 ['MagicSkillWnd','SummonedWnd'].each{clazz->
  def entry=byName(clazz+'.OnClickButton'),fn=serializer.getOrCreateObject(entry)
  assert fn.child.entry.objectInnerFullName==clazz+'.OnClickButton.strID'
  def ctx=new BytecodeContext(new UnrealRuntimeContext(entry,serializer));int offset=0
  fn.bytecode.eachWithIndex{token,i->
   if(token instanceof JumpIfNot){
    assert token.condition instanceof NativeFunctionCall&&token.condition.nativeIndex==122
    assert token.condition.params[0].objRef==fn.child.entry.objectReference
    assert token.targetOffset==offset+token.getSize(ctx)+fn.bytecode[i+1].getSize(ctx)+fn.bytecode[i+2].getSize(ctx)
   };offset+=token.getSize(ctx)
  }
  def instructions=fn.bytecode.collect{it.toString(new UnrealRuntimeContext(entry,serializer))}
  assert instructions.any{it.contains('voice .amber toggle')}
  if(clazz=='MagicSkillWnd')assert instructions.findAll{it.contains('voice .habilidades quick')}.size()==7
  else assert serializer.getOrCreateObject(byName(clazz)).child.entry.objectInnerFullName==clazz+'.OnClickButton'
  println clazz+': '+instructions.join(' | ')
 }
}
println 'PASS: fresh package reload, parameter refs, string comparisons and every VM jump target verified.'
