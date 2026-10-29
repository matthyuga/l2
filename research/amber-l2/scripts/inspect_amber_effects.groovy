import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import acmi.l2.clientmod.unreal.core.TextBuffer

def client = new File(args[0])
def factory = new UnrealSerializerFactory(Environment.fromIni(new File(client, 'system-hud/l2.ini')))
new UnrealPackage(new File(client, 'system-hud/Engine.u'), true).withCloseable { up ->
    if (args.length == 1) {
        up.exportTable.findAll { it.objectInnerFullName.contains('SkillAction') }.each { println it.objectInnerFullName }
    } else {
        for (String name : args.drop(1)) {
            def entry = up.exportTable.find { it.objectInnerFullName == name + '.ScriptText' }
            assert entry != null : name
            println ((TextBuffer) factory.getOrCreateObject(entry)).text
        }
    }
}
