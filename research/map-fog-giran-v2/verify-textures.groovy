import acmi.l2.clientmod.io.*
def dir=new File(args[0])
new UnrealPackage(new File(dir,'NexusMapFogV2.u'),true).withCloseable{up->
 def entries=up.exportTable.findAll{it.fullClassName=='Engine.Texture'}
 assert entries*.objectInnerFullName.sort()==['CloudTile','GiranClear']
 entries.each{e->
  new File(dir,e.objectInnerFullName+'.texture.raw').bytes=e.objectRawData
  println e.objectInnerFullName+' '+e.objectRawData.length+' bytes'
 }
 new File(dir,'texture-names.txt').text=(0..<up.nameTable.size()).collect{up.nameReference(it)}.join('\n')
}
