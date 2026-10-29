import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import java.nio.ByteBuffer
import java.nio.ByteOrder

def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2'),stage=new File(root,'exports/contract/combat-vfx-v3')
boolean installed=args.length>1&&args[1]=='installed'
def particles=installed?new File(client,'system-hud/AmberParticlesV3.u'):new File(root,'tools/l2editor/L2Editor/AmberParticlesV3.u')
if(!installed)new File(stage,'AmberParticlesV3.u').bytes=particles.bytes
def effect=installed?new File(client,'animations/AmberEffectsV3.usk'):new File(stage,'AmberEffectsV3.usk')
def env=installed?Environment.fromIni(new File(client,'system-hud/l2.ini')):new Environment(project,['research/amber-l2/exports/contract/combat-vfx-v3/*.u','research/amber-l2/exports/contract/combat-vfx-v3/*.usk','../l2/system-hud/*.u','../l2/system/*.u','../l2/animations/*.ukx','../l2/animations/*.usk','../l2/systextures/*.utx','../l2/staticmeshes/*.usx'])
def factory=new UnrealSerializerFactory(env)
int checks=0
def check={boolean ok,String label->assert ok:label;checks++}
def property={obj,String name->obj.@properties.find{it.name==name}}
def value={obj,String name->property(obj,name)?.getAt(0)}
def number={obj,String name,String axis,String bound->value(obj,name).find{it.name==axis}.getAt(0).find{it.name==bound}.getAt(0)}
def range={obj,String name,String bound->value(obj,name).find{it.name==bound}.getAt(0)}
def close={a,b->Math.abs(a.doubleValue()-b.doubleValue())<0.0001}
new UnrealPackage(effect,true).withCloseable{up->
 for(String name:['Rain','FireRain','Mark','SkyVolley','ShotCharge','FireIgnite']+(1..16).collect{'FireShot'+it}){
  def visual=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name})
  check(visual.@properties.size()==1&&visual.@properties[0].name=='CastingActions',name+' starts in casting phase')
 }
 for(String name:['Rain','FireRain','RainImpact','FireRainImpact','Mark','SkyVolley','ShotCharge','FireIgnite']+(1..16).collect{'FireShot'+it}){
  def obj=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name+'Action'})
  check(up.objectReference(value(obj,'EffectClass')).objectFullName=='AmberParticlesV3.'+name,name+' emitter reference')
  check(value(obj,'bRelativeToCylinder')==false&&value(obj,'bSizeScale')==false,name+' independent of tiny anchor size/cylinder')
   if(name.endsWith('Impact'))check(close(value(obj,'SpawnDelay'),0.650),name+' hits at 650ms')
  if(name in ['ShotCharge','FireIgnite'])check(value(obj,'AttachOn')==2,name+' attaches to left hand')
  if(name in ['Rain','FireRain','RainImpact','FireRainImpact','Mark'])check(value(obj,'bSpawnOnTarget')==true,name+' fixed ground anchor')
  if(name.startsWith('FireShot')){
   def offset=value(obj,'offset')
   check(close(offset.find{it.name=='Y'}.getAt(0),0)&&close(offset.find{it.name=='Z'}.getAt(0),45),name+' tracer starts above floor')
  }
 }
 for(String name:['Rain','FireRain']){
  def actions=value(factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name}),'CastingActions')
  check(actions.size()==2,name+' includes descent and impact')
  def refs=actions.collect{up.objectReference(it.find{it.name=='Action'}.getAt(0)).objectInnerFullName}
  check(refs==[name+'Action',name+'ImpactAction'],name+' ordered visual actions')
 }
}
new UnrealPackage(particles,true).withCloseable{up->
 for(String name:['Rain','FireRain']){
  def cls=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name})
  check(cls.superField.entry.objectFullName=='Engine.Emitter',name+' compiled emitter')
  check(value(cls,'Emitters').size()==30,name+' 30 deterministic arrows')
  for(int i=0;i<30;i++){
   def arrow=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name+'.P'+i})
   double x=number(arrow,'StartLocationRange','X','Min'),y=number(arrow,'StartLocationRange','Y','Min')
   check(Math.hypot(x,y)<=200,name+' arrow inside circular damage zone')
   check(close(x,number(arrow,'StartLocationRange','X','Max'))&&close(y,number(arrow,'StartLocationRange','Y','Max')),name+' deterministic impact position')
   check(close(number(arrow,'StartLocationRange','Z','Min'),430)&&close(number(arrow,'StartVelocityRange','Z','Min'),-600),name+' descent')
   check(close(range(arrow,'LifetimeRange','Min'),0.650),name+' ends at impact')
   double scale=number(arrow,'StartSizeRange','X','Min')
   check(close(430-32*scale-600*0.650,0),name+' tip reaches ground at damage time')
   check(value(arrow,'MaxParticles')==1,name+' one arrow per point')
  }
 }
}
if(args.length>1&&args[1]=='packages'){println 'PASS: '+checks+' compiled VFX package checks.';return}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats'),codec=new File(project,'tools/open-l2encdec-1.3.9/l2encdec_win.exe')
for(def spec:[['skillgrp','skillgrp.dat','skillgrp.xml'],['skillname','skillname-e.dat','skillname.xml']]){
 def raw=new File(stage,spec[0]+'.raw')
 if(installed){
  def actual=new File(stage,spec[0]+'.installed.raw');def p=new ProcessBuilder(codec.path,'-o',actual.path,new File(client,'system-hud/'+spec[1]).path).redirectErrorStream(true).start();def output=p.inputStream.text;check(p.waitFor()==0,'decode installed catalog '+output);check(Arrays.equals(actual.bytes,raw.bytes),'installed bytes '+spec[0])
 }
 def before=new AmberCatalog(new File(stage,spec[0]+'.before.raw'),schemas,spec[2],'ScionsOfDestiny'),cat=new AmberCatalog(raw,schemas,spec[2],'ScionsOfDestiny')
 check(cat.count==before.count+15,'15 added cosmetic levels')
 def index=cat.rows.collectEntries{[(it.skill_id+':'+it.skill_level):it]}
 before.rows.each{old->if(spec[0]!='skillgrp'||!(old.skill_id.intValue() in [19002,19006,19007,19008,19009,19010,19013])){
  def now=index[old.skill_id+':'+old.skill_level];check(Arrays.equals(Arrays.copyOfRange(before.data,old._start,old._end),Arrays.copyOfRange(cat.data,now._start,now._end)),'unrelated row '+old.skill_id+':'+old.skill_level)
 }}
 if(spec[0]=='skillgrp'){
  check(cat.rows.find{it.skill_id.intValue()==19002}.description=='AmberEffectsV3.FireIgnite','fire activation linked')
  for(int level=1;level<=16;level++)check(cat.rows.find{it.skill_id.intValue()==19009&&it.skill_level.intValue()==level}.description=='AmberEffectsV3.FireShot'+level,'tracer level '+level)
 }
}
println 'PASS: '+checks+' VFX checks; '+(installed?'installed':'staged')+' packages, phases, attachments, circular distribution and unrelated catalog records.'
