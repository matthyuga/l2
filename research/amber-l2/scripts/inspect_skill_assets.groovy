import acmi.l2.clientmod.io.UnrealPackage
new UnrealPackage(new File('E:/l2/animations/skill.usk'),true).withCloseable {up->
    up.exportTable.findAll {it.objectInnerFullName==~ /.*\.(19|24|1423|1223|1059|1111)/}.each{println "${it.objectInnerFullName} ${it.fullClassName} ${it.size}"}
    println up.exportTable.take(12).collect{"${it.objectInnerFullName} ${it.fullClassName}"}.join('\n')
}
