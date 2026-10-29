import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory

def root=new File(args[0]);def client=new File(root.parentFile.parentFile.parentFile,'l2')
def output=new File(root,'exports/contract/AmberEffects.usk');output.bytes=new File(client,'animations/skill.usk').bytes
def compact={int n->boolean neg=n<0;n=Math.abs(n);def bytes=[(byte)((n&63)|(neg?128:0)|(n>63?64:0))];n>>>=6;while(n){bytes<<(byte)((n&127)|(n>127?128:0));n>>>=7};bytes as byte[]}
new UnrealPackage(output,false).withCloseable{up->
 up.addNameEntries(['EffectClass','bSpawnOnTarget','bUseCharacterRotation','CastingActions','ShotActions','Action','None'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['Engine.SkillAction_LocateEffect':'Core.Class','Engine.SkillVisualEffect':'Core.Class']+['Rain','FireRain','SkyVolley','FireShot','Mark'].collectEntries{[('AmberParticles.'+it):'Core.Class']})
 def prop={String name,int type,byte[] payload->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(type|0x50);out.write(payload.length);out.write(payload);out.toByteArray()}
 for(String name:['Rain','FireRain','SkyVolley','FireShot','Mark']){
  def action=new ByteArrayOutputStream();action.write(prop('EffectClass',5,compact(up.importTable.find{it.objectFullName=='AmberParticles.'+name}.objectReference)))
  if(name!='SkyVolley'&&name!='FireShot'){action.write(compact(up.nameReference('bSpawnOnTarget')));action.write(0x83)}
  if(name=='FireShot'){action.write(compact(up.nameReference('bUseCharacterRotation')));action.write(0x83)}
  action.write(compact(up.nameReference('None')))
  up.addExportEntry(name+'Action','Engine.SkillAction_LocateEffect',null,action.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
  def ref=up.exportTable.find{it.objectInnerFullName==name+'Action'}.objectReference
  def item=new ByteArrayOutputStream();item.write(compact(1));item.write(prop('Action',5,compact(ref)));item.write(compact(up.nameReference('None')))
  def visual=new ByteArrayOutputStream();visual.write(prop('CastingActions',9,item.toByteArray()));visual.write(compact(up.nameReference('None')))
  up.addExportEntry(name,'Engine.SkillVisualEffect',null,visual.toByteArray(),UnrealPackage.DEFAULT_OBJECT_FLAGS)
 }
}
def factory=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
new UnrealPackage(output,true).withCloseable{up->['Rain','FireRain','SkyVolley','FireShot','Mark'].each{name->def e=up.exportTable.find{it.objectInnerFullName==name};println name+' '+factory.getOrCreateObject(e).@properties;println factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name+'Action'}).@properties}}
