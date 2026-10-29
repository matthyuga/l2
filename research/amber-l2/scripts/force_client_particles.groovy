import acmi.l2.clientmod.io.UnrealPackage
def file=new File(args[0]),compact=AmberCatalog.&compact
int count=0
new UnrealPackage(file,false).withCloseable{up->
 up.addNameEntries(['ForcedMaxParticles','RenderTwoSided'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 byte[] none=compact(up.nameReference('None'))
 up.exportTable.findAll{it.fullClassName in ['Engine.SpriteEmitter','Engine.MeshEmitter']}.each{entry->
  byte[] raw=entry.objectRawData
  assert Arrays.equals(Arrays.copyOfRange(raw,raw.length-none.length,raw.length),none):'Native particle has unexpected trailer'
  def out=new ByteArrayOutputStream();out.write(raw,0,raw.length-none.length)
  out.write(compact(up.nameReference('ForcedMaxParticles')));out.write(0x83)
  if(entry.fullClassName=='Engine.MeshEmitter'){out.write(compact(up.nameReference('RenderTwoSided')));out.write(0x83)}
  out.write(none);entry.setObjectRawData(out.toByteArray());count++
 }
}
assert count>0
println 'PASS: '+count+' native particle objects force their declared count: '+file.name
