import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder
def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2'),stage=new File(root,'exports/contract/combat-vfx-v5');stage.mkdirs()
def glyphs=(0..<4).collectMany{color->(0..<10).collectMany{slot->(0..<10).collect{digit->[id:19200+color*100+slot*10+digit,name:'Dmg_'+color+'_'+slot+'_'+digit+'_Fx']}}}
def particleNames=['Rain','FireRain','RainImpact','FireRainImpact','Mark','SkyVolley']+(1..16).collect{'FireShot'+it}
def classes=particleNames.collectEntries{[(it):'AmberParticlesV5.'+it]}+['NativeFire':'LineageEffect.el_flame_strike_ca']+glyphs.collectEntries{[(it.name):'DamageGlyphsV1.'+it.name]}
def effect=new File(stage,'AmberEffectsV5.usk');effect.bytes=new File(client,'animations/skill.usk').bytes
new UnrealPackage(effect,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 up.addNameEntries(['EffectClass','bSpawnOnTarget','bUseCharacterRotation','bRelativeToCylinder','bSizeScale','CastingActions','Action','None','AttachOn','SpawnDelay','offset','Vector'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['Engine.SkillAction_LocateEffect':'Core.Class','Engine.SkillVisualEffect':'Core.Class']+classes.values().collectEntries{[(it):'Core.Class']})
 def compact=AmberCatalog.&compact
 def prop={String name,int type,byte[] payload->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(type|0x50);if(type==10)out.write(compact(up.nameReference('Vector')));out.write(payload.length);out.write(payload);out.toByteArray()}
 def boolProp={String name,boolean value->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(value?0x83:0x03);out.toByteArray()}
 classes.each{name,cls->
  boolean glyph=name.startsWith('Dmg_')
  def out=new ByteArrayOutputStream();out.write(prop('EffectClass',5,compact(up.importTable.find{it.objectFullName==cls}.objectReference)))
  out.write(boolProp('bRelativeToCylinder',glyph||name=='NativeFire'));out.write(boolProp('bSizeScale',false))
  if(glyph||(name in ['Rain','FireRain','RainImpact','FireRainImpact','Mark','NativeFire']))out.write(boolProp('bSpawnOnTarget',true))
  if(name.endsWith('Impact'))out.write(prop('SpawnDelay',4,ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putFloat(0.650f).array()))
  if(glyph){out.write(prop('AttachOn',1,[5] as byte[]));out.write(prop('offset',10,ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN).putFloat(0.0f).putFloat(0.0f).putFloat(1.5f).array()))}
  if(name=='NativeFire')out.write(prop('AttachOn',1,[5] as byte[]))
  if(name.startsWith('FireShot')){out.write(boolProp('bUseCharacterRotation',true));out.write(prop('offset',10,ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN).putFloat(20.0f).putFloat(0.0f).putFloat(45.0f).array()))}
  out.write(compact(up.nameReference('None')))
  up.addExportEntry(name+'Action','Engine.SkillAction_LocateEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
 def visuals=[:]
 classes.keySet().each { name ->
  if (!name.endsWith('Impact')) {
   if (name == 'Rain' || name == 'FireRain') {
    visuals.put(name, [name, name + 'Impact'])
   } else {
    visuals.put(name, [name])
   }
  }
 }
 visuals.each{name,actions->
  def items=new ByteArrayOutputStream();items.write(compact(actions.size()))
  actions.each{action->items.write(prop('Action',5,compact(up.exportTable.find{it.objectInnerFullName==action+'Action'}.objectReference)));items.write(compact(up.nameReference('None')))}
  def out=new ByteArrayOutputStream();out.write(prop('CastingActions',9,items.toByteArray()));out.write(compact(up.nameReference('None')))
  up.addExportEntry(name,'Engine.SkillVisualEffect',null,out.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats'),codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def run={List cmd->def p=new ProcessBuilder(cmd).redirectErrorStream(true).start();def output=p.inputStream.text;assert p.waitFor()==0:output}
def extrasSpec=[[id:19012,name:'SkyVolley'],[id:19014,name:'NativeFire']]+glyphs
for(def spec:[['skillgrp','skillgrp.dat','skillgrp.xml'],['skillname','skillname-e.dat','skillname.xml']]){
 def before=new File(stage,spec[0]+'.before.raw');run([codec.path,'-o',before.path,new File(client,'system-hud/'+spec[1]).path])
 def cat=new AmberCatalog(before,schemas,spec[2],'ScionsOfDestiny'),extra=[]
 def nativeItem=spec[0]=='skillgrp'?cat.rows.find{it.skill_id==2033&&it.skill_level==1}:null
 def instantFields=['operate_type','mp_consume','cast_range','cast_style','hit_time','is_magic','animation','extra_eff','rumble_self','rumble_target']
 byte[] changed=cat.patch{row->
  if(spec[0]!='skillgrp')return null
  int id=row.skill_id.intValue()
  if(id==19006){row.description='';return row} // Bow animation retains its existing timing.
  def names=[19007:'Rain',19008:'FireRain',19009:'FireShot'+row.skill_level,19010:'Mark']
  if(!names.containsKey(id))return null
  instantFields.each{row[it]=nativeItem[it]};row.description='AmberEffectsV5.'+names[id];return row
 }
 extrasSpec.each{item->
  assert !cat.rows.any{it.skill_id==item.id}:'New visual ID already in use: '+item.id
  def template=spec[0]=='skillgrp'?nativeItem:cat.rows.find{it.skill_id==19013&&it.skill_level==1}
  def row=new LinkedHashMap(template);row.skill_id=item.id;row.skill_level=1
  if(spec[0]=='skillgrp')row.description='AmberEffectsV5.'+item.name
  else {row.name='Visual local';row.desc='Efecto cosmetico. No cambia estadisticas ni dano.'}
  extra<<row
 }
 def mid=new File(stage,spec[0]+'.patched.raw');mid.bytes=changed
 def parsed=new AmberCatalog(mid,schemas,spec[2],'ScionsOfDestiny')
 def out=new ByteArrayOutputStream();out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(cat.count+extra.size()).array());out.write(changed,4,parsed.end-4);extra.each{out.write(cat.encode(it))};out.write(changed,parsed.end,changed.length-parsed.end)
 def raw=new File(stage,spec[0]+'.raw');raw.bytes=out.toByteArray()
 def finalCat=new AmberCatalog(raw,schemas,spec[2],'ScionsOfDestiny');assert finalCat.count==cat.count+402
 cat.rows.eachWithIndex{old,i->if(spec[0]!='skillgrp'||!(old.skill_id.intValue() in [19006,19007,19008,19009,19010]))assert Arrays.equals(Arrays.copyOfRange(cat.data,old._start,old._end),Arrays.copyOfRange(finalCat.data,finalCat.rows[i]._start,finalCat.rows[i]._end))}
 def encoded=new File(stage,spec[1]);run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path]);def check=new File(stage,spec[0]+'.roundtrip.raw');run([codec.path,'-o',check.path,encoded.path]);assert Arrays.equals(raw.bytes,check.bytes)
 println 'PASS: '+spec[0]+' native item casting path, 402 hidden visuals, unrelated records preserved, roundtrip exact.'
}
