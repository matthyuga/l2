import acmi.l2.clientmod.io.UnrealPackage
new UnrealPackage(new File(args[0]), true).withCloseable { up ->
    def matches = up.exportTable.findAll { it.objectInnerFullName.equalsIgnoreCase('a_traderB_FHuman') }
    assert matches.size() == 1 : 'Missing/ambiguous client NPC class'
    assert matches[0].fullClassName == 'Core.Class'
    println "Verified ${up.packageName}.${matches[0].objectInnerFullName} (${matches[0].fullClassName})"
}
