import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import acmi.l2.clientmod.unreal.core.TextBuffer

if (args.length != 3) {
    throw new IllegalArgumentException('Uso: extract-interface-script.groovy <system> <entrada.u> <objeto.ScriptText>')
}

def environment = Environment.fromIni(new File(args[0], 'l2.ini'))
def serializer = new UnrealSerializerFactory(environment)
new UnrealPackage(new File(args[1]), true).withCloseable { up ->
    def entry = up.exportTable.find { it.objectInnerFullName.equalsIgnoreCase(args[2]) }
    if (entry == null) {
        throw new IllegalArgumentException("No se encontro ${args[2]}")
    }
    TextBuffer script = (TextBuffer) serializer.getOrCreateObject(entry)
    print script.text
}
