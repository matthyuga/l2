import acmi.l2.clientmod.io.*
def output=new File(args[0]);output.mkdirs()
new UnrealPackage(new File('E:/l2/systextures/l2zonename.utx'),true).withCloseable{up->
    up.exportTable.findAll{it.fullClassName in ['Engine.Texture','Engine.Palette']}.each{e->
        new File(output,e.objectInnerFullName+'.raw').bytes=e.objectRawData
    }
    new File(output,'names.txt').text=(0..<up.nameTable.size()).collect{up.nameReference(it)}.join('\n')
    new File(output,'exports.tsv').text=up.exportTable.collect{it.objectInnerFullName+'\t'+it.fullClassName+'\t'+it.objectRawData.length}.join('\n')
    println 'Extracted '+up.exportTable.size()+' exports; original package read-only.'
}
