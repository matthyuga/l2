import acmi.l2.clientmod.io.UnrealPackage
import java.nio.ByteBuffer
import java.nio.ByteOrder

def root=new File(args[0]);def project=root.parentFile.parentFile;def client=new File(project.parentFile,'l2')
def stage=new File(root,'exports/contract/combat-vfx-v2');stage.mkdirs()
def compact={int n->boolean neg=n<0;n=Math.abs(n);def bytes=[(byte)((n&63)|(neg?128:0)|(n>63?64:0))];n>>>=6;while(n){bytes<<(byte)((n&127)|(n>127?128:0));n>>>=7};bytes as byte[]}
def anchor=new File(stage,'AmberAnchorsV1.u');anchor.bytes=new File(client,'system-hud/LineageNPC.u').bytes
new UnrealPackage(anchor,false).withCloseable { up ->
 up.setUUID(UUID.randomUUID());up.updateNameTable{names->int i=up.nameReference('a_traderB_FHuman');names[i]=new UnrealPackage.NameEntry(up,i,'RainAnchor',names[i].flags)}
 up.addNameEntries(['bHidden','DrawScale'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 def entry=up.exportTable.find{it.objectInnerFullName=='RainAnchor'};byte[] raw=entry.objectRawData,none=compact(up.nameReference('None'))
 assert raw[-none.length..-1] as byte[]==none
 def out=new ByteArrayOutputStream();out.write(raw,0,raw.length-none.length)
 out.write(compact(up.nameReference('bHidden')));out.write(0x03)
 out.write(compact(up.nameReference('DrawScale')));out.write(0x24);out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putFloat(0.001f).array())
 out.write(none);entry.setObjectRawData(out.toByteArray())
}
if(args.length>1&&args[1]=='anchorOnly'){println 'Valid tiny anchor rebuilt.';return}
def effect=new File(stage,'AmberEffectsV2.usk');effect.bytes=new File(client,'animations/skill.usk').bytes
new UnrealPackage(effect,false).withCloseable { up ->
 up.setUUID(UUID.randomUUID())
 def names=['Rain','FireRain','SkyVolley','FireShot','ShotCharge','Mark']
 up.addNameEntries(['EffectClass','bSpawnOnTarget','bUseCharacterRotation','ShotActions','Action','None','AttachOn','AttachBoneName','Weapon_L_Bone','offset','Vector'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['Engine.SkillAction_LocateEffect':'Core.Class','Engine.SkillVisualEffect':'Core.Class']+names.collectEntries{[('AmberParticlesV2.'+it):'Core.Class']})
 def prop={String name,int type,byte[] payload->def o=new ByteArrayOutputStream();o.write(compact(up.nameReference(name)));o.write(type|0x50);if(type==10)o.write(compact(up.nameReference('Vector')));o.write(payload.length);o.write(payload);o.toByteArray()}
 names.each { name ->
  def action=new ByteArrayOutputStream();action.write(prop('EffectClass',5,compact(up.importTable.find{it.objectFullName=='AmberParticlesV2.'+name}.objectReference)))
  if(name in ['Rain','FireRain','Mark']){action.write(compact(up.nameReference('bSpawnOnTarget')));action.write(0x83)}
  if(name=='FireShot'){action.write(compact(up.nameReference('bUseCharacterRotation')));action.write(0x83);action.write(prop('offset',10,ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN).putFloat(20f).putFloat(45f).putFloat(0f).array()))}
  if(name=='ShotCharge'){
   action.write(prop('AttachOn',1,[3] as byte[]));action.write(prop('AttachBoneName',6,compact(up.nameReference('Weapon_L_Bone'))))
  }
  action.write(compact(up.nameReference('None')))
  up.addExportEntry(name+'Action','Engine.SkillAction_LocateEffect',null,action.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
  def ref=up.exportTable.find{it.objectInnerFullName==name+'Action'}.objectReference
  def item=new ByteArrayOutputStream();item.write(compact(1));item.write(prop('Action',5,compact(ref)));item.write(compact(up.nameReference('None')))
  def visual=new ByteArrayOutputStream();visual.write(prop('ShotActions',9,item.toByteArray()));visual.write(compact(up.nameReference('None')))
  up.addExportEntry(name,'Engine.SkillVisualEffect',null,visual.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats'),codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
def run={List<String> cmd->def p=new ProcessBuilder(cmd).redirectErrorStream(true).start();String out=p.inputStream.text;assert p.waitFor()==0:out}
for(def spec:[['npcgrp','npcgrp.dat','npcgrp.xml','Interlude'],['skillgrp','skillgrp.dat','skillgrp.xml','ScionsOfDestiny'],['skillname','skillname-e.dat','skillname.xml','ScionsOfDestiny']]){
 def before=new File(stage,spec[0]+'.before.raw');run([codec.path,'-o',before.path,new File(client,'system-hud/'+spec[1]).path])
 def cat=new AmberCatalog(before,schemas,spec[2],spec[3]);def touched=[]
 byte[] changed=cat.patch{row->
  int id=(spec[0]=='npcgrp'?row.npc_id:row.skill_id).intValue()
  if(spec[0]=='npcgrp'){
   if(id==59002){row.attack_effect='';touched<<id;return row}
   if(id==59003){row.class_name='AmberAnchorsV1.RainAnchor';row.mesh_name='L2AmberArcherV2.AmberNPC';row.texture_name=2;row.texture_name_items=cat.rows.find{it.npc_id==59002}.texture_name_items;row.attack_effect='';touched<<id;return row}
  } else if(spec[0]=='skillgrp') {
   def fx=[19006:'SkyVolley',19007:'Rain',19008:'FireRain',19009:'FireShot',19010:'Mark']
   if(fx.containsKey(id)){row.description='AmberEffectsV2.'+fx[id];touched<<id;return row}
   if(id==19005){row.description='';touched<<id;return row}
  } else if(id in [19002,19005]){row.desc='Amber: +25% PAtk y +20 ataque de fuego durante 15s. Resistencias elementales aplican. Fuego: 60 MP, recarga 30s.';touched<<id;return row}
  null
 }
 def mid=new File(stage,spec[0]+'.patched.raw');mid.bytes=changed;def parsed=new AmberCatalog(mid,schemas,spec[2],spec[3]);def extras=[]
 if(spec[0]!='npcgrp') {
  [19011,19013].each { id ->
   assert !cat.rows.any{it.skill_id==id}
   def row=new LinkedHashMap(cat.rows.find{it.skill_id==19005})
   row.skill_id=id
   if(spec[0]=='skillgrp') {row.description=id==19013?'AmberEffectsV2.ShotCharge':'';row.operate_type=id==19011?1:0;row.cast_style=id==19013?12:0;row.hit_time=0f;row.icon='AmberIconsV1.Fire'}
   else {row.name=id==19011?'Amber: fuego activo':'Carga de Soulshot de Amber';row.desc=id==19011?'Indicador del fuego de Amber. Dura 15s; no aumenta las estadisticas de tu personaje.':'Beast Soulshot cargado en el arco de Amber.'}
   extras<<row
  }
 }
 def out=new ByteArrayOutputStream();out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(cat.count+extras.size()).array());out.write(changed,4,parsed.end-4);extras.each{out.write(cat.encode(it))};out.write(changed,parsed.end,changed.length-parsed.end)
 def raw=new File(stage,spec[0]+'.raw');raw.bytes=out.toByteArray();def fresh=new AmberCatalog(raw,schemas,spec[2],spec[3]);assert fresh.count==cat.count+extras.size()
 def index=fresh.rows.collectEntries{row->[(spec[0]=='npcgrp'?row.npc_id.toString():row.skill_id+':'+row.skill_level):row]}
 cat.rows.each{old->int id=(spec[0]=='npcgrp'?old.npc_id:old.skill_id).intValue();if(!(id in touched)){def now=index[spec[0]=='npcgrp'?old.npc_id.toString():old.skill_id+':'+old.skill_level];assert Arrays.equals(Arrays.copyOfRange(cat.data,old._start,old._end),Arrays.copyOfRange(fresh.data,now._start,now._end))}}
 def encoded=new File(stage,spec[1]);run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path]);def check=new File(stage,spec[0]+'.roundtrip.raw');run([codec.path,'-o',check.path,encoded.path]);assert Arrays.equals(raw.bytes,check.bytes)
 println spec[0]+': Amber changes '+touched+', additions '+extras*.skill_id+'; all other rows preserved.'
}
println 'New effects use ShotActions, real hidden anchor and bow bone; no original game package overwritten.'
