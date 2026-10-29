import acmi.l2.clientmod.io.UnrealPackage

if (args.length != 1) {
    throw new IllegalArgumentException('Uso: inspect-interface-u.groovy <Interface.u>')
}

new UnrealPackage(new File(args[0]), true).withCloseable { up ->
    println "package=${up.packageName} exports=${up.exportTable.size()} names=${up.nameTable.size()}"
    up.exportTable.each { entry ->
        String name = entry.objectInnerFullName
        String type = entry.fullClassName
        if (name.toLowerCase().contains('eventmatchgmcommand') ||
            name.toLowerCase().contains('interface') ||
            name.toLowerCase().contains('html') ||
            type.toLowerCase().contains('textbuffer')) {
            println String.format('%5d  %-55s %-35s size=%d offset=%d', entry.index, name, type, entry.size, entry.offset)
        }
    }
}
