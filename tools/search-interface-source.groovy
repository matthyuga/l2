import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import acmi.l2.clientmod.unreal.core.TextBuffer

if (args.length != 2) {
    System.err.println('Usage: search-interface-source.groovy <system directory> <text regex>')
    System.exit(2)
}

def systemDir = new File(args[0])
def packageFile = new File(systemDir, 'Interface.u')
def environment = Environment.fromIni(new File(systemDir, 'l2.ini'))
def serializer = new UnrealSerializerFactory(environment)
def pattern = ~/(?i)${args[1]}/

new UnrealPackage(packageFile, true).withCloseable { up ->
    up.exportTable.findAll { it.fullClassName.equalsIgnoreCase('Core.TextBuffer') }.each { entry ->
        try {
            def object = serializer.getOrCreateObject(entry)
            if (object instanceof TextBuffer && pattern.matcher(object.text ?: '').find()) {
                println("===== ${entry.objectFullName} =====")
                object.text.readLines().eachWithIndex { line, index ->
                    if (pattern.matcher(line).find()) {
                        println("${index + 1}: ${line}")
                    }
                }
            }
        } catch (Throwable ignored) {
        }
    }
}
