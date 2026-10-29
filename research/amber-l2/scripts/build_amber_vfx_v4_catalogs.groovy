import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder
def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2')
def stage=new File(root,'exports/contract/combat-vfx-v4');stage.mkdirs()
def compact=AmberCatalog.&compact
def effect=new File(stage,'AmberEffectsV4.usk');effect.bytes=new File(client,'animations/skill.usk').bytes
new UnrealPackage(effect,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 def names=['Rain','FireRain','RainImpact','FireRainImpact','Mark','SkyVolley']+(1..16).collect{'FireShot'+it}
 up.addNameEntries(['EffectClass','bSpawnOnTarget','bUseCharacterRotation','bRelativeToCylinder','bSizeScale','ShotActions','Action','SpecificStage','None','SpawnDelay','offset','Vector'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['Engine.SkillAction_LocateEffect':'Core.Class','Engine.SkillVisualEffect':'Core.Class']+names.collectEntries{[('AmberParticlesV4.'+it):'Core.Class']})
 def prop={String name,int type,byte[] payload->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(type|0x50);if(type==10)out.write(compact(up.nameReference('Vector')));out.write(payload.length);out.write(payload);out.toByteArray()}
 def boolProp={String name,boolean value->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(value?0x83:0x03);out.toByteArray()}
 names.each{name->
  def out=new ByteArrayOutputStream()
  out.write(prop('EffectClass',5,compact(up.importTable.find{it.objectFullName=='AmberParticlesV4.'+name}.objectReference)))
  out.write(boolProp('bRelativeToCylinder',false));out.write(boolProp('bSizeScale',false))
  if(name in ['Rain','FireRain','RainImpact','FireRainImpact','Mark'])out.write(boolProp('bSpawnOnTarget',true))
  if(name.endsWith('Impact'))out.write(prop('SpawnDelay',4,ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putFloat(0.650f).array()))
  if(name.startsWith('FireShot')){
   out.write(boolProp('bUseCharacterRotation',true))
   out.write(prop('offset',10,ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN).putFloat(20f).putFloat(0f).putFloat(45f).array()))
  }
  out.write(compact(up.nameReference('None')))
  up.addExportEntry(name+'Action','Engine.SkillAction_LocateEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
 def visuals=['Rain':['Rain','RainImpact'],'FireRain':['FireRain','FireRainImpact'],'Mark':['Mark'],'SkyVolley':['SkyVolley']]+(1..16).collectEntries{[('FireShot'+it):['FireShot'+it]]}
 visuals.each{name,actions->
  def items=new ByteArrayOutputStream();items.write(compact(actions.size()))
  actions.each{action->items.write(prop('Action',5,compact(up.exportTable.find{it.objectInnerFullName==action+'Action'}.objectReference)));items.write(compact(up.nameReference('None')))}
  def out=new ByteArrayOutputStream();out.write(prop('ShotActions',9,items.toByteArray()));out.write(compact(up.nameReference('None')))
  up.addExportEntry(name,'Engine.SkillVisualEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats'),codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def run={List cmd->def p=new ProcessBuilder(cmd).redirectErrorStream(true).start();def output=p.inputStream.text;assert p.waitFor()==0:output}
def before=new File(stage,'skillgrp.before.raw');run([codec.path,'-o',before.path,new File(client,'system-hud/skillgrp.dat').path])
def cat=new AmberCatalog(before,schemas,'skillgrp.xml','ScionsOfDestiny'),changed=[]
def fx=[19006:'SkyVolley',19007:'Rain',19008:'FireRain',19009:'FireShot',19010:'Mark']
def raw=new File(stage,'skillgrp.raw');raw.bytes=cat.patch{row->
 int id=row.skill_id.intValue()
 if(!fx.containsKey(id))return null
 assert row.description.startsWith('AmberEffectsV3.')||row.description.startsWith('AmberEffectsV4.'):'Unexpected catalog baseline'
 row.description='AmberEffectsV4.'+fx[id]+(id==19009?row.skill_level:'')
 if(id!=19006){row.cast_style=0;row.hit_time=0f;row.is_magic=0;row.animation='';row.extra_eff=0;row.operate_type=0}
 changed<<id;return row
}
def finalCat=new AmberCatalog(raw,schemas,'skillgrp.xml','ScionsOfDestiny')
assert cat.count==finalCat.count
cat.rows.eachWithIndex{old,i->if(!fx.containsKey(old.skill_id.intValue()))assert Arrays.equals(Arrays.copyOfRange(cat.data,old._start,old._end),Arrays.copyOfRange(finalCat.data,finalCat.rows[i]._start,finalCat.rows[i]._end))}
def encoded=new File(stage,'skillgrp.dat');run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path])
def check=new File(stage,'skillgrp.roundtrip.raw');run([codec.path,'-o',check.path,encoded.path]);assert Arrays.equals(raw.bytes,check.bytes)
println 'PASS: V4 shot-phase effects; changed '+changed.size()+' records; soulshot, fire buff and all unrelated records preserved.'
