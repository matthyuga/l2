import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.bytecode.token.*
import acmi.l2.clientmod.unreal.bytecode.BytecodeContext
def stage=new File(args[0])
def buttonOnly=new File(stage,'input-mode.json').exists() && new File(stage,'input-mode.json').text.contains('"button-only"')
def ser=new UnrealSerializerFactory(new Environment(stage,['./*.u','../../../l2/system-hud/*.u','../../../l2/system/*.u','../../../l2/systextures/*.utx']))
new UnrealPackage(new File(stage,'Interface.u'),true).withCloseable {up->
 def byName={n->up.exportTable.find{it.objectInnerFullName==n}}
 def clazz=ser.getOrCreateObject(byName('StickerRadialUI'));assert clazz.superField.entry.objectFullName=='Interface.UICommonAPI'
 def chain=[],field=clazz.child
 while(field){assert !chain.contains(field.entry.objectInnerFullName):'Class field cycle';chain<<field.entry.objectInnerFullName;field=field.next}
 assert chain.size()==6:chain
 assert chain.contains('StickerRadialUI.m_Held')
 def nativeBypass=up.importTable.find{it.objectFullName=='NWindow.UIScript.RequestBypassToServer'}.objectReference
 ['OnLoad','OnEvent','OnTimer','OnClickButton','ToggleWheel'].each{name->
  def e=byName('StickerRadialUI.'+name),fn=ser.getOrCreateObject(e),ctx=new BytecodeContext(new UnrealRuntimeContext(e,ser))
  def offsets=[];int at=0;fn.bytecode.each{offsets<<at;at+=it.getSize(ctx)};offsets<<at
  fn.bytecode.each{if(it instanceof JumpIfNot||it instanceof Jump)assert offsets.contains(it.targetOffset):name+' branch enters instruction'}
  if(name=='OnTimer'){
   if(buttonOnly){
    assert fn.bytecode.size()==1 && fn.bytecode[0] instanceof Return && fn.bytecode[0].value instanceof Nothing
    println 'PASS: OnTimer is return-only; no keyboard/native calls.'
   }else{
   def keyRef=up.importTable.find{it.objectFullName=='NWindow.UIScript.IsKeyDown'}
   assert ser.getOrCreateObject(keyRef).child.entry.fullClassName=='Core.ByteProperty'
   def keys=fn.bytecode.findAll{it instanceof JumpIfNot && it.condition instanceof FinalFunction && it.condition.funcRef==keyRef.objectReference}.collect{it.condition.params[0]}
   assert keys.size()==3 && keys.every{it instanceof ByteConst}
   assert keys.collect{it.value}==[27,18,69]
   println 'PASS: native IsKeyDown byte-enum parameters use ByteConst, never 32-bit IntConstByte.'
   }
  }
  if(name=='OnEvent' && buttonOnly){
   assert !fn.bytecode.any{it.toString(new UnrealRuntimeContext(e,ser)).contains('UITimer(')}
   println 'PASS: no timer registration remains in OnEvent.'
  }
  if(name=='OnClickButton'){
   def calls=fn.bytecode.findAll{it instanceof FinalFunction};assert calls.size()==8
   assert calls.every{it.funcRef==nativeBypass}
   assert calls.collect{it.params[0].value}==(1..8).collect{'voice .sticker '+it}
  }
  println 'FUNCTION '+name;fn.bytecode.each{println '  '+it.toString(new UnrealRuntimeContext(e,ser))}
 }
 // Compare every previous export using a separate package, independent from build serializer caches.
 new UnrealPackage(new File(stage,'current/Interface.u'),true).withCloseable{old->old.exportTable.each{e->assert Arrays.equals(e.objectRawData,byName(e.objectInnerFullName).objectRawData)}}
}
def assetSer=new UnrealSerializerFactory(new Environment(stage,['./*.u','./*.usk','../../../l2/system-hud/*.u','../../../l2/system/*.u','../../../l2/animations/*.usk']))
new UnrealPackage(new File(stage,'NexusStickersV2.u'),true).withCloseable{up->
 def base=assetSer.getOrCreateObject(up.exportTable.find{it.objectInnerFullName=='A_StickerBase'})
 assert base.@properties.find{it.name=='LifeSpan'}.getAt(0)==3.1f
 assert base.@properties.find{it.name=='Physics'}.getAt(0)==10
 (0..<19).each{i->
  def entry=up.exportTable.find{it.objectInnerFullName=='Sticker'+i+'.Icon'};assert entry
  def o=assetSer.getOrCreateObject(entry),props=o.@properties.collectEntries{[(it.name):it.getAt(0)]}
  assert props.ForcedMaxParticles==true && props.TriggerDisabled==false && props.Disabled==false && props.AlphaTest==false && props.LevelOfWeather==0
  assert props.MaxParticles==1 && props.RespawnDeadParticles==false
  println 'PARTICLE '+i+' '+props.findAll{k,v->k in ['MaxParticles','RespawnDeadParticles','LifetimeRange','CoordinateSystem','TriggerDisabled','ForcedMaxParticles']}
 }
}
new UnrealPackage(new File(stage,'NexusStickerEffectsV2.usk'),true).withCloseable{up->
 (0..<19).each{i->
  def a=assetSer.getOrCreateObject(up.exportTable.find{it.objectInnerFullName=='Sticker'+i+'Action'})
  def props=a.@properties.collectEntries{[(it.name):it.getAt(0)]}
  assert props.AttachOn==5 && props.bSpawnOnTarget==true && props.bSizeScale==false
  assert up.objectReference(props.EffectClass).objectFullName=='NexusStickersV2.Sticker'+i
  def visual=assetSer.getOrCreateObject(up.exportTable.find{it.objectInnerFullName=='Sticker'+i})
  assert visual.@properties.find{it.name=='CastingActions'}.getAt(0).size()==1
 }
}
println 'PASS: fresh client-native parsing, class field chain, all VM branches, exact bypass dispatch, 19 finite one-shot emitters and actor trail actions.'
