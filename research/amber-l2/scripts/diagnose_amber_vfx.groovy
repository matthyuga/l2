import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory

def root=new File(args[0]),project=root.parentFile.parentFile,client=new File(project.parentFile,'l2')
def factory=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
for(def spec:[['system-hud/Engine.u',['SkillAction_LocateEffect','SkillAction_LocateEffect.AttachOn','SkillVisualEffect','SkillAction']],['animations/AmberEffectsV2.usk',['RainAction','FireShotAction','ShotChargeAction']],['system-hud/AmberAnchorsV1.u',['RainAnchor']]]){
 new UnrealPackage(new File(client,spec[0]),true).withCloseable{up->
  spec[1].each{name->
   def entry=up.exportTable.find{it.objectInnerFullName==name}
   println '\n'+spec[0]+' '+name
   def obj=factory.getOrCreateObject(entry)
   obj.@properties.each{println it.name+'='+it.value}
   if(name.endsWith('.AttachOn')) println obj
  }
 }
}
def schemas=new File(root,'tools/L2ClientDat/dist/data/structure/dats')
def cat=new AmberCatalog(new File(project,'reports/amber-combat-vfx-installed-catalogs/skillgrp.raw'),schemas,'skillgrp.xml','ScionsOfDestiny')
cat.rows.findAll{it.skill_id.intValue() in [19002,19005,19006,19007,19008,19009,19010,19013,2033]}.each{println it.findAll{k,v->!k.startsWith('_')}}
