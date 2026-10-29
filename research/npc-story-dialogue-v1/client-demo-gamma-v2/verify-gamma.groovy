import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
def s=new File(args[0])
def ser=new UnrealSerializerFactory(new Environment(s,['./*.u','E:/l2/system-hud/*.u','E:/l2/system/*.u']))
new UnrealPackage(new File(s,'Interface.u'),true).withCloseable{up->
 def entry={n->up.exportTable.find{it.objectInnerFullName==n}}
 def clazz=ser.getOrCreateObject(entry('AmberStoryDemoUI'));assert clazz.superField.entry.objectFullName=='Interface.UICommonAPI'
 def chain=[],field=clazz.child
 while(field){assert !chain.contains(field.entry.objectInnerFullName);chain<<field.entry.objectInnerFullName;field=field.next}
 assert chain.size()==11:chain
 def names=['OnLoad','CloseAll','ShowWelcome','ShowPlace','ShowGreeting','ShowEnd','UseOriginal','UseCompensation','OnEvent','OnClickButton']
 def funcs=names.collectEntries{n->[(n):ser.getOrCreateObject(entry('AmberStoryDemoUI.'+n))]}
 funcs.each{name,fn->
  def ctx=new BytecodeContext(new UnrealRuntimeContext(fn.entry,ser)),offsets=[];int at=0
  fn.bytecode.each{offsets<<at;at+=it.getSize(ctx)};offsets<<at
  fn.bytecode.each{if(it instanceof JumpIfNot || it instanceof Jump)assert offsets.contains(it.targetOffset)}
  assert !fn.bytecode.any{it instanceof FinalFunction}
  fn.bytecode.each{t->def str=t.toString(new UnrealRuntimeContext(fn.entry,ser));assert !str.contains('UITimer') && !str.contains('RequestBypass') && !str.contains('IsKeyDown')}
 }
 new UnrealPackage(new File(s,'current/Interface.u'),true).withCloseable{old->old.exportTable.findAll{!it.objectInnerFullName.startsWith('AmberStoryDemoUI')}.each{e->assert Arrays.equals(e.objectRawData,entry(e.objectInnerFullName).objectRawData)}}
 def visible=[] as Set;def trace=[];def selectedTextures=[:]
 Closure run,eval
 eval={t,locals->
  if(t instanceof StringConst || t instanceof IntConst)return t.value
  if(t instanceof LocalVariable)return locals[t.objRef]
  if(t instanceof NativeFunctionCall){assert t.nativeIndex in [122,154];return eval(t.params[0],locals)==eval(t.params[1],locals)}
  if(t instanceof ClassContext)return eval(t.member,locals)
  if(t instanceof VirtualFunction){
   def name=up.nameReference(t.nameRef);def args=t.params.collect{eval(it,locals)}
   if(funcs.containsKey(name)){run(name,null);return null}
   assert name in ['ShowWindow','HideWindow','SetFocus','RegisterEvent','SetTexture'];if(name=='SetTexture'){selectedTextures[args[0]]=args[1];return null}
   trace<<[name,args]
   if(name=='ShowWindow')visible<<args[0]
   if(name=='HideWindow')visible.remove(args[0])
   return null
  }
  assert false:'Unexpected token '+t
 }
 run={name,param->
  def fn=funcs[name],ctx=new BytecodeContext(new UnrealRuntimeContext(fn.entry,ser));def offsets=[:];int at=0
  fn.bytecode.eachWithIndex{t,i->offsets[at]=i;at+=t.getSize(ctx)}
  def locals=[:];if(fn.child)locals[fn.child.entry.objectReference]=param
  int pc=0,steps=0
  while(pc<fn.bytecode.length){assert steps++<100;def t=fn.bytecode[pc++]
   if(t instanceof Return)break
   if(t instanceof JumpIfNot){if(!eval(t.condition,locals))pc=offsets[t.targetOffset];continue}
   eval(t,locals)
  }
 }
 run('OnLoad',null);assert visible.empty
 run('OnEvent',150);assert visible==['AmberStoryLauncherWnd'] as Set
 def routes=[Open:'AmberStoryWelcomeWnd',Explore:'AmberStoryPlaceWnd',Greet:'AmberStoryGreetingWnd',Next:'AmberStoryEndWnd',Restart:'AmberStoryWelcomeWnd']
 routes.each{button,win->run('OnClickButton',button);assert visible==['AmberStoryLauncherWnd',win] as Set}
 run('OnClickButton','Close');assert visible==['AmberStoryLauncherWnd'] as Set
 run('OnClickButton','Original');assert selectedTextures.size()==4 && selectedTextures.values().every{it=='NexusAmberStoryV1.Portrait'};run('OnClickButton','Compensate');assert selectedTextures.size()==4 && selectedTextures.values().every{it=='NexusAmberGammaV2.PortraitComp'};run('OnClickButton','invalid');assert visible==['AmberStoryLauncherWnd'] as Set
 run('OnClickButton','Open');run('OnEvent',160);assert visible.empty
 println 'PASS: parsed VM routes open/both responses/continue/restart/close/unknown/logout; valid branches; no timers, keyboard polling or network calls; all previous exports preserved.'
}
new UnrealPackage(new File(s,'NexusAmberGammaV2.u'),true).withCloseable{up->
 def textures=up.exportTable.findAll{it.fullClassName=='Engine.Texture'}
 assert textures.size()==7:textures.size()
 ['PortraitComp','OriginalUp','CompensateUp'].each{n->assert textures.any{it.objectInnerFullName==n}}
 println 'PASS: native texture package contains compensated portrait and 2 button sets; no emitter or gameplay class.'
}
println 'PASS: Amber inverse-gamma demo ready for guarded installation; visual validation in L2 pending.'
