import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def client=new File(args[0]),factory=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
new UnrealPackage(new File(client,'system-hud/Engine.u'),true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName.startsWith('SkillAction')&&it.fullClassName in ['Core.Class','Core.Enum']}.each{println it.objectInnerFullName+' '+it.fullClassName}
 for(String name:['SkillAction_LocateEffect','SkillAction_LocateEffect.AttachOn','SkillAction_ProjectileEffect','ParticleEmitter','MeshEmitter']){
  def e=up.exportTable.find{it.objectInnerFullName==name};if(!e)continue
  def o=factory.getOrCreateObject(e);println '\n'+name
  println 'fields='+o.class.fields*.name
  if(name.endsWith('.AttachOn')){println 'enum='+o.enumType;println 'enum values='+o.enumType?.values}
  o.@properties.each{println it.name+'='+it.value}
 }
}
new UnrealPackage(new File(client,'animations/skill.usk'),true).withCloseable{up->
 def effects=up.exportTable.findAll{it.fullClassName=='Engine.SkillAction_LocateEffect'}
 effects.findAll{it.objectInnerFullName==~/(?i).*(2033|2150|1460|1223|1059).*/}.take(18).each{e->
  println '\nNative '+e.objectInnerFullName
  factory.getOrCreateObject(e).@properties.each{p->def v=p.value;if(p.name=='EffectClass')v=up.objectReference(p.getAt(0))?.objectFullName;println p.name+'='+v}
 }
 ['it.2033','su.1223','su.1059'].each{n->def e=up.exportTable.find{it.objectInnerFullName==n};if(e){println '\n'+n;factory.getOrCreateObject(e).@properties.each{println it.name+'='+it.value}}}
}
