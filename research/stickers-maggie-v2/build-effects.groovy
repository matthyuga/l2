import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import java.nio.ByteBuffer
import java.nio.ByteOrder
def stage=new File(args[0]),root=stage.parentFile.parentFile,client=new File(root.parentFile,'l2')
def compact=AmberCatalog.&compact
def particles=new File(stage,'NexusStickersV2.u');particles.bytes=new File(stage,'NexusStickersV2.raw.u').bytes
new UnrealPackage(particles,false).withCloseable{up->
 up.addNameEntries(['ForcedMaxParticles','TriggerDisabled','Disabled','AlphaTest','LevelOfWeather'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 byte[] none=compact(up.nameReference('None'))
 up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}.each{e->
  byte[] raw=e.objectRawData;assert Arrays.equals(Arrays.copyOfRange(raw,raw.length-none.length,raw.length),none)
  def out=new ByteArrayOutputStream();out.write(raw,0,raw.length-none.length)
  ['ForcedMaxParticles':true,'TriggerDisabled':false,'Disabled':false,'AlphaTest':false].each{n,value->out.write(compact(up.nameReference(n)));out.write(value?0x83:0x03)}
  out.write(compact(up.nameReference('LevelOfWeather')));out.write(0x22);out.write([0,0,0,0] as byte[])
  out.write(none);e.setObjectRawData(out.toByteArray())
 }
}
// UE2 trail physics keeps the sprite with the target while retaining camera facing.
// Physics is written against the client's own enum, rather than UT2003 ordinals.
def factory=new UnrealSerializerFactory(new Environment(client,['system-hud/*.u','system/*.u','animations/*.usk','systextures/*.utx']))
int physicsTrailer
new UnrealPackage(new File(client,'system-hud/Engine.u'),true).withCloseable{engine->
 def e=engine.exportTable.find{it.fullClassName=='Core.Enum'&&it.objectInnerFullName.endsWith('.EPhysics')}
 assert e:'Client EPhysics missing';def values=factory.getOrCreateObject(e).values
 physicsTrailer=values.indexOf('PHYS_Trailer');assert physicsTrailer>0
}
new UnrealPackage(particles,false).withCloseable{up->
 up.addNameEntries(['Physics'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 // Add instance defaults after the class bytecode/default separator's existing None.
 up.exportTable.findAll{it.fullClassName=='Core.Class'&&it.objectInnerFullName=='A_StickerBase'}.each{e->
  byte[] raw=e.objectRawData,none=compact(up.nameReference('None'))
  assert Arrays.equals(Arrays.copyOfRange(raw,raw.length-none.length,raw.length),none)
  def out=new ByteArrayOutputStream();out.write(raw,0,raw.length-none.length);out.write(compact(up.nameReference('Physics')));out.write(1);out.write(physicsTrailer);out.write(none);e.setObjectRawData(out.toByteArray())
 }
}
def fx=new File(stage,'NexusStickerEffectsV2.usk');fx.bytes=new File(client,'animations/skill.usk').bytes
new UnrealPackage(fx,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 up.addNameEntries(['EffectClass','bSpawnOnTarget','bRelativeToCylinder','bSizeScale','CastingActions','Action','AttachOn','None'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['Engine.SkillAction_LocateEffect':'Core.Class','Engine.SkillVisualEffect':'Core.Class']+(0..<19).collectEntries{[('NexusStickersV2.Sticker'+it):'Core.Class']})
 def prop={String n,int type,byte[] payload->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(n)));out.write(type|0x50);out.write(payload.length);out.write(payload);out.toByteArray()}
 (0..<19).each{i->
  def out=new ByteArrayOutputStream()
  out.write(prop('EffectClass',5,compact(up.importTable.find{it.objectFullName=='NexusStickersV2.Sticker'+i}.objectReference)))
  out.write(prop('AttachOn',1,[5] as byte[]))
  ['bSpawnOnTarget':true,'bRelativeToCylinder':false,'bSizeScale':false].each{n,value->out.write(compact(up.nameReference(n)));out.write(value?0x83:0x03)}
  out.write(compact(up.nameReference('None')))
  up.addExportEntry('Sticker'+i+'Action','Engine.SkillAction_LocateEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
  def items=new ByteArrayOutputStream();items.write(compact(1));items.write(prop('Action',5,compact(up.exportTable.find{it.objectInnerFullName=='Sticker'+i+'Action'}.objectReference)));items.write(compact(up.nameReference('None')))
  def visual=new ByteArrayOutputStream();visual.write(prop('CastingActions',9,items.toByteArray()));visual.write(compact(up.nameReference('None')))
  up.addExportEntry('Sticker'+i,'Engine.SkillVisualEffect',null,visual.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
}
println 'PASS: 19 client-native transient effects; EAM_Trail=5, PHYS_Trailer='+physicsTrailer+'; particle inherited defaults overridden.'
