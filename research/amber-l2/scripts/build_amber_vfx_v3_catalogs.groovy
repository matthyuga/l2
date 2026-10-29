import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder

def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2')
def stage=new File(root,'exports/contract/combat-vfx-v3');stage.mkdirs()
def compact=AmberCatalog.&compact
def effect=new File(stage,'AmberEffectsV3.usk');effect.bytes=new File(client,'animations/skill.usk').bytes
new UnrealPackage(effect,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 def names=['Rain','FireRain','RainImpact','FireRainImpact','Mark','SkyVolley','ShotCharge','FireIgnite']+(1..16).collect{'FireShot'+it}
 up.addNameEntries(['EffectClass','bSpawnOnTarget','bUseCharacterRotation','bRelativeToCylinder','bSizeScale','CastingActions','ShotActions','Action','SpecificStage','None','AttachOn','SpawnDelay','offset','Vector'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['Engine.SkillAction_LocateEffect':'Core.Class','Engine.SkillVisualEffect':'Core.Class']+names.collectEntries{[('AmberParticlesV3.'+it):'Core.Class']})
 def prop={String name,int type,byte[] payload->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(type|0x50);if(type==10)out.write(compact(up.nameReference('Vector')));out.write(payload.length);out.write(payload);out.toByteArray()}
 def boolProp={String name,boolean value->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(value?0x83:0x03);out.toByteArray()}
 def number={float value->ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putFloat(value).array()}
 names.each{name->
  def out=new ByteArrayOutputStream()
  out.write(prop('EffectClass',5,compact(up.importTable.find{it.objectFullName=='AmberParticlesV3.'+name}.objectReference)))
  out.write(boolProp('bRelativeToCylinder',false));out.write(boolProp('bSizeScale',false))
  if(name in ['Rain','FireRain','RainImpact','FireRainImpact','Mark'])out.write(boolProp('bSpawnOnTarget',true))
  if(name.endsWith('Impact'))out.write(prop('SpawnDelay',4,number(.650f)))
  if(name in ['ShotCharge','FireIgnite'])out.write(prop('AttachOn',1,[2] as byte[])) // EAM_LH: uses AmberArcher.LeftHandBone.
  if(name.startsWith('FireShot')){
   out.write(boolProp('bUseCharacterRotation',true))
   out.write(prop('offset',10,ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN).putFloat(20f).putFloat(0f).putFloat(45f).array()))
  }
  out.write(compact(up.nameReference('None')))
  up.addExportEntry(name+'Action','Engine.SkillAction_LocateEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
 def visuals=['Rain':['Rain','RainImpact'],'FireRain':['FireRain','FireRainImpact'],'Mark':['Mark'],'SkyVolley':['SkyVolley'],'ShotCharge':['ShotCharge'],'FireIgnite':['FireIgnite']]+(1..16).collectEntries{[('FireShot'+it):['FireShot'+it]]}
 visuals.each{name,actions->
  def items=new ByteArrayOutputStream();items.write(compact(actions.size()))
  actions.each{action->items.write(prop('Action',5,compact(up.exportTable.find{it.objectInnerFullName==action+'Action'}.objectReference)));items.write(compact(up.nameReference('None')))}
  def out=new ByteArrayOutputStream();out.write(prop('CastingActions',9,items.toByteArray()));out.write(compact(up.nameReference('None')))
  up.addExportEntry(name,'Engine.SkillVisualEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
}
if(args.length>1&&args[1]=='effectsOnly'){println 'PASS: effects rebuilt with vertical tracer origin.';return}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats'),codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def run={List cmd->def p=new ProcessBuilder(cmd).redirectErrorStream(true).start();def output=p.inputStream.text;assert p.waitFor()==0:output}
for(def spec:[['skillgrp','skillgrp.dat','skillgrp.xml'],['skillname','skillname-e.dat','skillname.xml']]){
 // Rebuild from saved V2, rather than adding levels to an already installed V3.
 def baseline=new File(project,'backups/amber-vfx-v3-2026-10-10/client/system-hud/'+spec[1])
 assert baseline.exists():'Missing saved V2 baseline; do not rebuild over unknown catalogs.'
 def before=new File(stage,spec[0]+'.before.raw');run([codec.path,'-o',before.path,baseline.path])
 def cat=new AmberCatalog(before,schemas,spec[2],'ScionsOfDestiny'),touched=[]
 byte[] changed=cat.patch{row->
  int id=row.skill_id.intValue()
  if(spec[0]=='skillgrp'){
   def fx=[19002:'FireIgnite',19006:'SkyVolley',19007:'Rain',19008:'FireRain',19009:'FireShot1',19010:'Mark',19013:'ShotCharge']
   if(fx.containsKey(id)){
    row.description='AmberEffectsV3.'+fx[id]
    if(id!=19006){row.cast_style=0;row.hit_time=0f;row.is_magic=0;row.animation='';row.extra_eff=0}
    // Public fire order remains a skill with native reuse; hidden visuals are instantaneous actions.
    if(id!=19002&&id!=19006)row.operate_type=0
    touched<<id;return row
   }
  }
  null
 }
 def mid=new File(stage,spec[0]+'.patched.raw');mid.bytes=changed
 def parsed=new AmberCatalog(mid,schemas,spec[2],'ScionsOfDestiny'),extras=[]
 for(int level=2;level<=16;level++){
  assert !cat.rows.any{it.skill_id.intValue()==19009&&it.skill_level.intValue()==level}
  def row=new LinkedHashMap(parsed.rows.find{it.skill_id.intValue()==19009&&it.skill_level.intValue()==1});row.skill_level=level
  if(spec[0]=='skillgrp')row.description='AmberEffectsV3.FireShot'+level
  extras<<row
 }
 def out=new ByteArrayOutputStream();out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(cat.count+extras.size()).array());out.write(changed,4,parsed.end-4);extras.each{out.write(cat.encode(it))};out.write(changed,parsed.end,changed.length-parsed.end)
 def raw=new File(stage,spec[0]+'.raw');raw.bytes=out.toByteArray()
 def fresh=new AmberCatalog(raw,schemas,spec[2],'ScionsOfDestiny');assert fresh.count==cat.count+15
 def index=fresh.rows.collectEntries{[(it.skill_id+':'+it.skill_level):it]}
 cat.rows.each{old->if(!(old.skill_id.intValue() in touched)){
  def now=index[old.skill_id+':'+old.skill_level]
  assert Arrays.equals(Arrays.copyOfRange(cat.data,old._start,old._end),Arrays.copyOfRange(fresh.data,now._start,now._end))
 }}
 def encoded=new File(stage,spec[1]);run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path]);def roundtrip=new File(stage,spec[0]+'.roundtrip.raw');run([codec.path,'-o',roundtrip.path,encoded.path]);assert Arrays.equals(raw.bytes,roundtrip.bytes)
 println spec[0]+': PASS; changed='+touched+', added 15 cosmetic tracer levels; unrelated rows unchanged.'
}
println 'PASS: casting-phase VFX, left-hand bow attachments and delayed ground impact actions built.'
