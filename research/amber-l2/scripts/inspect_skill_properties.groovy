import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def serializer=new UnrealSerializerFactory(Environment.fromIni(new File('E:/l2/system-hud/l2.ini')))
new UnrealPackage(new File('E:/l2/animations/skill.usk'),true).withCloseable {up->
    def e=up.exportTable.find{it.objectInnerFullName=='su.1059'}
    println 'raw='+e.objectRawData.encodeHex().toString()
    def object=serializer.getOrCreateObject(e);object.@properties.each{println "${it.template.entry.objectInnerFullName} ${it.value}"}
    def effect=up.exportTable.find{it.fullClassName=='Engine.SkillAction_LocateEffect'}
    println effect.objectInnerFullName
    serializer.getOrCreateObject(effect).@properties.each{println "${it.template.entry.objectInnerFullName} ${it.value}"}
}
