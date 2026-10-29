import acmi.l2.clientmod.io.UnrealPackage
def root=new File(args[0])
new UnrealPackage(new File('E:/l2/animations/Fighter.ukx'),true).withCloseable {up->
    def entry=up.exportTable.find {it.objectInnerFullName=='FFighter_anim'}
    assert entry!=null
    new File(root,'reports/archer-animation-native.bin').bytes=entry.objectRawData
    new File(root,'reports/archer-animation-names.txt').text=up.nameTable.collect{it.name}.join('\n')
    println "Animation native bytes=${entry.size}"
}
new UnrealPackage(new File('E:/l2/system-hud/LineageNPC.u'),true).withCloseable {up->
    def types=up.exportTable.findAll {it.objectInnerFullName.toLowerCase().contains('traderb_fhuman')}
    types.each { println "${it.objectInnerFullName} ${it.fullClassName} ${it.size}" }
}
