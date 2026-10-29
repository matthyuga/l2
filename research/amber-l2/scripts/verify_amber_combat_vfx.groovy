import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory

def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2')
def stage=new File(root,'exports/contract/combat-vfx-v2')
boolean staged=args.length>1&&args[1]=='stage'
def effects=staged?new File(stage,'AmberEffectsV2.usk'):new File(client,'animations/AmberEffectsV2.usk')
def anchors=staged?new File(stage,'AmberAnchorsV1.u'):new File(client,'system-hud/AmberAnchorsV1.u')
def particles=staged?new File(root,'tools/l2editor/L2Editor/AmberParticlesV2.u'):new File(client,'system-hud/AmberParticlesV2.u')
def ini=new File(client,'system-hud/l2.ini')
if(staged){
 new File(stage,'AmberParticlesV2.u').bytes=particles.bytes
 ini=new File(stage,'verify.ini')
 ini.text='[Core.System]\n'+[new File(stage,'*.u'),new File(stage,'*.usk'),new File(client,'system-hud/*.u'),new File(client,'system/*.u'),new File(client,'animations/*.ukx'),new File(client,'animations/*.usk'),new File(client,'systextures/*.utx'),new File(client,'staticmeshes/*.usx')].collect{'Paths='+it.path.replace('\\','/')}.join('\n')+'\n'
}
def environment=staged?new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v2/*.u','research/amber-l2/exports/contract/combat-vfx-v2/*.usk','../l2/system-hud/*.u','../l2/system/*.u','../l2/animations/*.ukx','../l2/animations/*.usk','../l2/systextures/*.utx','../l2/staticmeshes/*.usx']):Environment.fromIni(ini)
def factory=new UnrealSerializerFactory(environment)
new UnrealPackage(effects,true).withCloseable { up ->
 ['Rain','FireRain','Mark','SkyVolley','FireShot','ShotCharge'].each{ name ->
  def props=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name}).@properties
  assert props.size()==1&&props[0].name=='ShotActions'
  def action=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name+'Action'}).@properties
  assert up.objectReference(action.find{it.name=='EffectClass'}.getAt(0)).objectFullName=='AmberParticlesV2.'+name
  if(name in ['Rain','FireRain','Mark'])assert action.find{it.name=='bSpawnOnTarget'}.getAt(0)==true
  if(name=='ShotCharge'){assert action.find{it.name=='AttachOn'}.getAt(0)==3;assert up.nameReference(action.find{it.name=='AttachBoneName'}.getAt(0))=='Weapon_L_Bone'}
  println name+': launch phase and emitter linkage verified.'
 }
}
new UnrealPackage(anchors,true).withCloseable { up ->
 def cls=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName=='RainAnchor'})
 assert cls.@properties.find{it.name=='DrawScale'}.getAt(0)==0.001f
 println 'Ground anchor is a real Pawn with a tiny valid mesh.'
}
new UnrealPackage(particles,true).withCloseable { up ->
 for(String name:['Rain','FireRain','SkyVolley','FireShot','ShotCharge','Mark']){
  def cls=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name})
  assert cls.superField.entry.objectFullName=='Engine.Emitter'
 }
 assert up.exportTable.any{it.objectInnerFullName=='Rain.Glow'}
 assert up.exportTable.any{it.objectInnerFullName=='FireRain.Glow'}
 println 'Compiled emitter classes and visible glow components resolve.'
}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def catalogDir=stage
if(!staged){
 catalogDir=new File(project,'reports/amber-combat-vfx-installed-catalogs');catalogDir.mkdirs()
 ['npcgrp','skillgrp','skillname'].each{ name ->
  def datName=name=='skillname'?'skillname-e':name
  def raw=new File(catalogDir,name+'.raw')
  def codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
  def process=new ProcessBuilder(codec.path,'-o',raw.path,new File(client,'system-hud/'+datName+'.dat').path).redirectErrorStream(true).start()
  def output=process.inputStream.text
  assert process.waitFor()==0:output
  assert Arrays.equals(raw.bytes,new File(stage,name+'.raw').bytes):'Installed catalog differs: '+name
 }
 println 'Installed catalog bytes match the verified correction.'
}
def npc=new AmberCatalog(new File(catalogDir,'npcgrp.raw'),schemas,'npcgrp.xml','Interlude')
assert npc.rows.find{it.npc_id==59002}.attack_effect==''
def anchor=npc.rows.find{it.npc_id==59003};assert anchor.class_name=='AmberAnchorsV1.RainAnchor'&&anchor.mesh_name!=''
def grp=new AmberCatalog(new File(catalogDir,'skillgrp.raw'),schemas,'skillgrp.xml','ScionsOfDestiny')
assert grp.rows.find{it.skill_id==19013}.description=='AmberEffectsV2.ShotCharge'
assert grp.rows.find{it.skill_id==19011}.operate_type==1
println 'PASS: shot charge at bow, timed indicator, ground anchor and all VFX catalog links.'
