import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def client=new File(args[0])
def factory=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
new UnrealPackage(new File(client,'animations/AmberEffects.usk'),true).withCloseable{up->['Rain','FireRain','SkyVolley','FireShot','Mark'].each{name->def e=up.exportTable.find{it.objectInnerFullName==name};def props=factory.getOrCreateObject(e).@properties;assert props.size()==1&&props[0].template.entry.objectInnerFullName.endsWith('CastingActions');println name+' CastingActions verified'}
 ['Rain','FireRain','SkyVolley','FireShot','Mark'].each{name->
    def actor=factory.getOrCreateObject('AmberParticles.'+name,{it=='Core.Class'})
    assert actor.entry.unrealPackage!=null&&actor.superField!=null
    assert actor.superField.entry.objectFullName=='Engine.Emitter'
    println 'AmberParticles.'+name+': resolves through actual l2.ini package paths (not a dummy class).'
 }
 def action=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName=='FireShotAction'}).@properties
 assert action.any{it.template.entry.objectInnerFullName.endsWith('bUseCharacterRotation')&&it.getAt(0)==true}
 println 'FireShot uses character heading, independently of the upward rain charge.'
}
