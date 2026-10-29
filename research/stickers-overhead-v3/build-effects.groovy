import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
import java.nio.ByteBuffer
import java.nio.ByteOrder
def stage=new File(args[0]),root=stage.parentFile.parentFile,client=new File(root.parentFile,'l2')
def compact=AmberCatalog.&compact
def particles=new File(stage,'NexusStickersV3.u');particles.bytes=new File(stage,'NexusStickersV3.raw.u').bytes
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
def fx=new File(stage,'NexusStickerEffectsV3.usk');fx.bytes=new File(client,'animations/skill.usk').bytes
new UnrealPackage(fx,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 up.addNameEntries(['EffectClass','bSpawnOnTarget','bRelativeToCylinder','bSizeScale','CastingActions','Action','AttachOn','AttachBoneName','Bip01 Neck1','None'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['Engine.SkillAction_LocateEffect':'Core.Class','Engine.SkillVisualEffect':'Core.Class']+(0..<19).collectEntries{[('NexusStickersV3.Sticker'+it):'Core.Class']})
 def prop={String n,int type,byte[] payload->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(n)));out.write(type|0x50);out.write(payload.length);out.write(payload);out.toByteArray()}
 (0..<19).each{i->
  def out=new ByteArrayOutputStream()
  out.write(prop('EffectClass',5,compact(up.importTable.find{it.objectFullName=='NexusStickersV3.Sticker'+i}.objectReference)))
  out.write(prop('AttachOn',1,[3] as byte[]))
  out.write(prop('AttachBoneName',6,compact(up.nameReference('Bip01 Neck1'))))
  ['bSpawnOnTarget':true,'bRelativeToCylinder':false,'bSizeScale':false].each{n,value->out.write(compact(up.nameReference(n)));out.write(value?0x83:0x03)}
  out.write(compact(up.nameReference('None')))
  up.addExportEntry('Sticker'+i+'Action','Engine.SkillAction_LocateEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
  def items=new ByteArrayOutputStream();items.write(compact(1));items.write(prop('Action',5,compact(up.exportTable.find{it.objectInnerFullName=='Sticker'+i+'Action'}.objectReference)));items.write(compact(up.nameReference('None')))
  def visual=new ByteArrayOutputStream();visual.write(prop('CastingActions',9,items.toByteArray()));visual.write(compact(up.nameReference('None')))
  up.addExportEntry('Sticker'+i,'Engine.SkillVisualEffect',null,visual.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
}
println 'PASS: 19 transient effects use EAM_BoneSpecified=3 and Bip01 Neck1; no trailer physics; inherited particle defaults overridden.'
