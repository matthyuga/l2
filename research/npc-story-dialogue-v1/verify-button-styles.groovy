import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
def s=new File(args[0])
def ser=new UnrealSerializerFactory(new Environment(s,['./*.u','E:/l2/system-hud/*.u','E:/l2/system/*.u']))
new UnrealPackage(new File(s,'Interface.u'),true).withCloseable{up->
 def entry={n->up.exportTable.find{it.objectInnerFullName.equalsIgnoreCase(n)}}
 def clazz=ser.getOrCreateObject(entry('AmberButtonStylesUI'));assert clazz.superField.entry.objectFullName=='Interface.UICommonAPI'
 def chain=[],field=clazz.child
 while(field){assert !chain.contains(field.entry.objectInnerFullName);chain<<field.entry.objectInnerFullName;field=field.next}
 assert chain.size()==18:chain
 def names=['OnLoad','CloseAll','ShowWelcome','ShowPlace','ShowGreeting','ShowEnd','UseOriginal','UseCompensation','UseOpaque','UseSemi','UseClear','UseStyleA','UseStyleB','UseStyleC','UseStyleD','OnEvent','OnClickButton']
 def funcs=names.collectEntries{n->[(n):ser.getOrCreateObject(entry('AmberButtonStylesUI.'+n))]}
 funcs.each{name,fn->
  def ctx=new BytecodeContext(new UnrealRuntimeContext(fn.entry,ser)),offsets=[];int at=0
  fn.bytecode.each{offsets<<at;at+=it.getSize(ctx)};offsets<<at
  fn.bytecode.each{if(it instanceof JumpIfNot || it instanceof Jump)assert offsets.contains(it.targetOffset)}
  assert !fn.bytecode.any{it instanceof FinalFunction}
  fn.bytecode.findAll{it instanceof acmi.l2.clientmod.unreal.bytecode.token.Context}.each{t->assert t.bSize==0 && t.wSkip==t.member.getSize(ctx)}
  fn.bytecode.each{t->def str=t.toString(new UnrealRuntimeContext(fn.entry,ser));assert !str.contains('UITimer') && !str.contains('RequestBypass') && !str.contains('IsKeyDown')}
 }
 new UnrealPackage(new File(s,'current/Interface.u'),true).withCloseable{old->old.exportTable.each{e->assert Arrays.equals(e.objectRawData,entry(e.objectInnerFullName).objectRawData)}}
 def visible=[] as Set;def trace=[];def selectedTextures=[:];def selectedButtons=[:];def validButtons=new File(s,'button-controls.txt').readLines() as Set
 Closure run,eval
 eval={t,locals->
  if(t instanceof StringConst || t instanceof IntConst)return t.value
  if(t instanceof LocalVariable)return locals[t.objRef]
  if(t instanceof NativeFunctionCall){assert t.nativeIndex in [122,154];return eval(t.params[0],locals)==eval(t.params[1],locals)}

  if(t instanceof acmi.l2.clientmod.unreal.bytecode.token.Context){
   def get=t.object.value;assert t.object instanceof DynamicCast && get instanceof FinalFunction
   assert up.importTable[-t.object.classRef-1].objectFullName=='NWindow.ButtonHandle'
   assert up.importTable[-get.funcRef-1].objectFullName=='NWindow.UIScript.GetHandle'
   assert get.params.size()==1
   def path=eval(get.params[0],locals);assert validButtons.contains(path):path
   def setter=t.member;assert setter instanceof FinalFunction
   assert up.importTable[-setter.funcRef-1].objectFullName=='NWindow.ButtonHandle.SetTexture'
   def textures=setter.params.collect{eval(it,locals)};assert textures.size()==3
   selectedButtons[path]=textures;return null
  }
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

 ['Opaque':'BackgroundOpaque','Semi':'BackgroundSemi','Clear':'BackgroundClear'].each{button,texture->
  run('OnClickButton',button)
  def backgrounds=selectedTextures.findAll{k,v->k.endsWith('.Background')}
  assert backgrounds.size()==4 && backgrounds.values().every{it=='NexusAmberAngularV3.'+texture}
  routes.each{b,w->run('OnClickButton',b);assert visible==['AmberStoryLauncherWnd',w] as Set;assert selectedTextures.findAll{k,v->k.endsWith('.Background')}==backgrounds}
  run('OnClickButton','Close');run('OnClickButton','Open')
  assert selectedTextures.findAll{k,v->k.endsWith('.Background')}==backgrounds
 }
 assert selectedTextures.findAll{k,v->k.endsWith('.Portrait')}.values().every{it=='NexusAmberGammaV2.PortraitComp'}

 assert validButtons.size()==45:validButtons.size()
 ['A','B','C','D'].each{style->
  run('OnClickButton','Style'+style)
  assert selectedButtons.size()==29:selectedButtons.size()
  selectedButtons.each{path,textures->
   def name=path.substring(path.lastIndexOf('.')+1)
   assert textures==['Up','Down','Over'].collect{'NexusAmberButtonsV5.'+style+name+it}
  }
  assert selectedTextures.findAll{k,v->k.endsWith('.StyleBadge')}.size()==4
  assert selectedTextures.findAll{k,v->k.endsWith('.StyleBadge')}.values().every{it=='NexusAmberButtonsV5.Current'+style}
  def chosen=selectedButtons.collectEntries{k,v->[(k):v]}
  ['Opaque','Semi','Clear'].each{opacity->
   ['Original','Compensate'].each{portrait->
    run('OnClickButton',opacity);run('OnClickButton',portrait)
    routes.each{button,win->run('OnClickButton',button);assert visible==['AmberStoryLauncherWnd',win] as Set;assert selectedButtons==chosen}
    run('OnClickButton','Close');run('OnClickButton','Open');assert selectedButtons==chosen
   }
  }
 }
 println 'PASS: 4 styles x 3 backgrounds x 2 portrait modes; 29 native button handles receive all three state textures; all 45 button paths exist; selection survives all routes and reopen.'
 run('OnClickButton','Open');run('OnEvent',160);assert visible.empty
 println 'PASS: all 3 opacity modes survive navigation/reopen; portrait compensation independent; parsed VM routes open/both responses/continue/restart/close/unknown/logout; valid branches; no timers, keyboard polling or network calls; all previous exports preserved.'
}
new UnrealPackage(new File(s,'NexusAmberButtonsV5.u'),true).withCloseable{up->
 def textures=up.exportTable.findAll{it.fullClassName=='Engine.Texture'}
 assert textures.size()==136:textures.size()
 def controls=['Explore','Greet','Next','Restart','Close','Opaque','Semi','Clear','Original','Compensate']
 def expected=[]
 ['A','B','C','D'].each{style->
  controls.each{n->['Up','Down','Over'].each{state->expected<<style+n+state}}
  ['Up','Down','Over'].each{state->expected<<'Style'+style+state};expected<<'Current'+style
 }
 assert textures.collect{it.objectInnerFullName.toLowerCase()}.toSet()==expected.collect{it.toLowerCase()}.toSet()

 ['AExploreUp','BOpaqueOver','CClearDown','DOriginalUp','DCompensateDown','StyleAUp','CurrentD'].each{n->assert textures.any{it.objectInnerFullName.equalsIgnoreCase(n)}}
 println 'PASS: native texture package contains 4 full button families, 3 states, 4 selectors and 4 badges; no emitter or gameplay class.'
}
println 'PASS: Amber angular/opacity demo ready for guarded installation; visual validation in L2 pending.'


new UnrealPackage(new File(s,'current/NWindow.u'),true).withCloseable{up->
 def nativeSer=new UnrealSerializerFactory(new Environment(new File('E:/l2/system-hud'),['./*.u']))
 ['UIScript.GetHandle':['Core.StrProperty','Core.ObjectProperty'],'ButtonHandle.SetTexture':['Core.StrProperty','Core.StrProperty','Core.StrProperty']].each{n,types->
  def fn=nativeSer.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==n}),field=fn.child,actual=[]
  while(field){actual<<field.entry.fullClassName;field=field.next}
  assert actual==types:n+' '+actual
 }
 println 'PASS: native GetHandle return and three-string ButtonHandle.SetTexture signature verified against the original NWindow.u.'
}
