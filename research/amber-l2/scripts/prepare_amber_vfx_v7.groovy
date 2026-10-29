import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2'),stage=new File(root,'exports/contract/combat-vfx-v7');stage.mkdirs()
def compact=AmberCatalog.&compact
def factory=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
def particles=new File(stage,'AmberParticlesV7.u');particles.bytes=new File(client,'system-hud/AmberParticlesV6.u').bytes
int changed=0
new UnrealPackage(particles,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 up.exportTable.findAll{it.fullClassName in ['Engine.SpriteEmitter','Engine.MeshEmitter']}.each{entry->
  def obj=factory.getOrCreateObject(entry)
  def coord=obj.@properties.find{it.name=='CoordinateSystem'}?.getAt(0)
  if(coord==1)return
  byte[] prefix=compact(up.nameReference('CoordinateSystem'));byte[] raw=entry.objectRawData
  if(coord==null){
   byte[] none=compact(up.nameReference('None'))
   assert Arrays.equals(Arrays.copyOfRange(raw,raw.length-none.length,raw.length),none)
   def out=new ByteArrayOutputStream();out.write(raw,0,raw.length-none.length);out.write(prefix);out.write(1);out.write(1);out.write(none)
   entry.setObjectRawData(out.toByteArray());changed++;return
  }
  def offsets=[]
  for(int i=0;i<raw.length-prefix.length-1;i++)if((0..<prefix.length).every{raw[i+it]==prefix[it]}&&(raw[i+prefix.length]&255)==1&&(raw[i+prefix.length+1]&255)==2)offsets<<i+prefix.length+1
  assert offsets.size()==1:'coordinate byte ambiguous: '+entry.objectInnerFullName
  raw[offsets[0]]=1;entry.setObjectRawData(raw);changed++
 }
}
assert changed==436:'All 436 particle coordinates must be corrected'
def glyphs=new File(stage,'DamageGlyphsV2.u');glyphs.bytes=new File(root,'tools/l2editor/L2Editor/DamageGlyphsV2.u').bytes
def force=new ProcessBuilder(new File(project,'tools/jdk-25.0.4.1+1/bin/java.exe').path,'-cp',new File(project,'tools/XDAT_NEW/xdat_editor/dist/*').path+';'+new File(root,'scripts').path,'groovy.ui.GroovyMain',new File(root,'scripts/force_client_particles.groovy').path,glyphs.path).redirectErrorStream(true).start()
def forced=force.inputStream.text;assert force.waitFor()==0:forced;println forced.trim()
def effects=new File(stage,'AmberEffectsV7.usk');effects.bytes=new File(client,'animations/AmberEffectsV6.usk').bytes
new UnrealPackage(effects,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 for(def pair:[['AmberParticlesV6','AmberParticlesV7'],['DamageGlyphsV1','DamageGlyphsV2']]){
  def n=up.nameTable.find{it.name==pair[0]};assert n;up.updateNameEntry(n.index,pair[1],n.flags)
 }
 up.exportTable.findAll{it.fullClassName=='Engine.SkillAction_LocateEffect'&&!it.objectInnerFullName.startsWith('Dmg_')}.each{e->
  byte[] raw=e.objectRawData,prefix=compact(up.nameReference('bRelativeToCylinder'))
  def offsets=[]
  for(int i=0;i<raw.length-prefix.length;i++)if((0..<prefix.length).every{raw[i+it]==prefix[it]}&&(raw[i+prefix.length]&255)==3)offsets<<i+prefix.length
  assert offsets.size()<=1
  if(offsets){raw[offsets[0]]=(byte)0x83}
  if(e.objectInnerFullName.startsWith('FireShot')){
   byte[] before=java.nio.ByteBuffer.allocate(12).order(java.nio.ByteOrder.LITTLE_ENDIAN).putFloat(20.0f).putFloat(0.0f).putFloat(45.0f).array()
   byte[] after=java.nio.ByteBuffer.allocate(12).order(java.nio.ByteOrder.LITTLE_ENDIAN).putFloat(0.35f).putFloat(0.0f).putFloat(0.8f).array()
   def matches=[];for(int i=0;i<=raw.length-12;i++)if((0..<12).every{raw[i+it]==before[it]})matches<<i
   assert matches.size()==1;System.arraycopy(after,0,raw,matches[0],12)
  }
  e.setObjectRawData(raw)
 }
 up.exportTable.findAll{it.objectInnerFullName.startsWith('Dmg_')&&it.objectInnerFullName.endsWith('Action')}.each{e->
  def out=new ByteArrayOutputStream()
  def prop={name,type,byte[] payload->out.write(compact(up.nameReference(name)));out.write(type|0x50);out.write(payload.length);out.write(payload)}
  String cls='DamageGlyphsV2.'+e.objectInnerFullName.replace('Action','')
  prop('EffectClass',5,compact(up.importTable.find{it.objectFullName==cls}.objectReference))
  out.write(compact(up.nameReference('bRelativeToCylinder')));out.write(0x83)
  out.write(compact(up.nameReference('bSizeScale')));out.write(0x03)
  out.write(compact(up.nameReference('bSpawnOnTarget')));out.write(0x83)
  // No Trail attachment or cylinder-scaled offsets: font starts 110 units above feet.
  prop('AttachOn',1,[0] as byte[])
  out.write(compact(up.nameReference('None')));e.setObjectRawData(out.toByteArray())
 }
}
def codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe'),schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def run={List cmd->def p=new ProcessBuilder(cmd).redirectErrorStream(true).start();def output=p.inputStream.text;assert p.waitFor()==0:output}
for(def spec:[['skillgrp','skillgrp.dat','skillgrp.xml'],['skillname','skillname-e.dat','skillname.xml']]){
 def before=new File(stage,spec[0]+'.before.raw');run([codec.path,'-o',before.path,new File(client,'system-hud/'+spec[1]).path])
 def cat=new AmberCatalog(before,schemas,spec[2],'ScionsOfDestiny'),raw=new File(stage,spec[0]+'.raw')
 raw.bytes=cat.patch{r->
  if(spec[0]=='skillgrp'&&r.description.startsWith('AmberEffectsV6.')){r.description=r.description.replace('AmberEffectsV6.','AmberEffectsV7.');return r}
  return null
 }
 def encoded=new File(stage,spec[1]);run([codec.path,'-c','encode','-p','413','-o',encoded.path,raw.path]);def check=new File(stage,spec[0]+'.roundtrip.raw');run([codec.path,'-o',check.path,encoded.path]);assert Arrays.equals(raw.bytes,check.bytes)
 println 'PASS: '+spec[0]+' existing IDs preserved, new package descriptions, exact encoding roundtrip.'
}
println 'PASS: '+changed+' world-coordinate particles moved to local coordinates; digits flipped and Trail attachment and extra cylinder height offset removed; native cylinder-relative spawning restored.'
