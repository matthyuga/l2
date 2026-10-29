import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
def stage=new File(args[0]),client=new File(args[1])
def serializer=new UnrealSerializerFactory(new Environment(stage,['./*.u','../../../../l2/system-hud/*.u','../../../../l2/system/*.u','../../../../l2/systextures/*.utx']))
new UnrealPackage(new File(stage,'Interface.u'),true).withCloseable{up->
 def byName={n->up.exportTable.find{it.objectInnerFullName==n}}
 def nativeRef=up.importTable.find{it.objectFullName=='NWindow.UIScript.RequestBypassToServer'}.objectReference
 ['MagicSkillWnd.OnClickButton','SummonedWnd.OnClickButton','MagicSkillWnd.HandleSkillList','MagicSkillWnd.OnClickItem'].each{name->
  def e=byName(name),fn=serializer.getOrCreateObject(e),ctx=new BytecodeContext(new UnrealRuntimeContext(e,serializer))
  def offsets=[];int at=0;fn.bytecode.each{t->offsets<<at;at+=t.getSize(ctx)};offsets<<at
  fn.bytecode.each{t->if(t instanceof JumpIfNot || t instanceof Jump)assert offsets.contains(t.targetOffset):name+' branch enters middle of instruction'}
  if(name.endsWith('OnClickButton')){
   def calls=fn.bytecode.findAll{it instanceof FinalFunction};assert !calls.empty
   assert calls.every{it.funcRef==nativeRef}
   assert !fn.bytecode.any{it instanceof VirtualFunction}
   if(name.startsWith('Magic'))assert calls.any{it.params[0].value=='voice .habilidades next'}
  }
  println name;fn.bytecode.each{println '  '+it.toString(new UnrealRuntimeContext(e,serializer))}
  if(name.endsWith('OnClickItem')){
   int index=fn.bytecode.findIndexOf{it.toString(new UnrealRuntimeContext(e,serializer)).startsWith('UseSkill(')}
   assert fn.bytecode[index-1] instanceof JumpIfNot
   assert fn.bytecode[index-1].targetOffset==offsets[index+1]
  }
 }
 println 'PASS: fresh native final dispatch matches stock callers; every VM branch boundary and zero-ID click guard valid.'
}
