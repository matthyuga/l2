import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory

def client = new File(args[0])
def factory = new UnrealSerializerFactory(Environment.fromIni(new File(client, 'system-hud/l2.ini')))
for (String packageName : ['Engine', 'LineageNPC', 'LineageWarrior']) {
    def file = new File(client, 'system-hud/' + packageName + '.u')
    if (!file.exists()) continue
    new UnrealPackage(file, true).withCloseable { up ->
        for (String name : ['Pawn', 'LineagePawn', 'a_traderB_FHuman', 'Fighter', 'FFighter']) {
            def entry = up.exportTable.find { it.objectInnerFullName == name }
            if (entry == null) continue
            def object = factory.getOrCreateObject(entry)
            println packageName + '.' + name
            println '  parent = ' + object.superField?.entry?.objectFullName
            object.@properties.findAll { it.name ==~ /(?i).*(bone|weapon|hand|mesh|action|scale).*/ }.each {
                def value = it.getAt(0)
                if (it.template.class.simpleName == 'NameProperty' && value instanceof Number) value = up.nameReference(value.intValue())
                println '  ' + it.name + ' = ' + value
            }
        }
        if (packageName == 'LineageNPC') println 'Archer/guard classes: ' + up.exportTable.findAll { it.fullClassName == 'Core.Class' && it.objectInnerFullName ==~ /(?i).*(archer|guard).*FHuman.*/ }.collect { it.objectInnerFullName }
    }
}
