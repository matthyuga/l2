import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.io.*
def stage=new File(args[0])
def target=new File(stage,'NexusStickerEffectsV3.usk')
target.bytes=new File('E:/l2/animations/NexusStickerEffectsV3.usk').bytes
def original=[:]
new UnrealPackage(target,false).withCloseable{up->
 up.exportTable.each{original[it.objectInnerFullName]=it.objectRawData.clone()}
 up.addNameEntries(['Bip01_head':UnrealPackage.DEFAULT_NAME_FLAGS,'bAbsolute':UnrealPackage.DEFAULT_NAME_FLAGS])
 def compact=AmberCatalog.&compact
 def prop={int value->def o=new ByteArrayOutputStream();o.write(compact(up.nameReference('AttachBoneName')));o.write(0x56);def v=compact(value);o.write(v.length);o.write(v);o.toByteArray()}
 byte[] before=prop(up.nameReference('Bip01 Neck1')),after=prop(up.nameReference('Bip01_head'))
 (0..<19).each{i->
  def e=up.exportTable.find{it.objectInnerFullName=='Sticker'+i+'Action'}
  byte[] raw=e.objectRawData;def hits=[]
  (0..raw.length-before.length).each{at->if(Arrays.equals(Arrays.copyOfRange(raw,at,at+before.length),before))hits<<at}
  assert hits.size()==1
  int at=hits[0];def o=new ByteArrayOutputStream();o.write(raw,0,at);o.write(after);o.write(raw,at+before.length,raw.length-at-before.length)
  byte[] updated=o.toByteArray(),none=compact(up.nameReference('None'))
  assert Arrays.equals(Arrays.copyOfRange(updated,updated.length-none.length,updated.length),none)
  o=new ByteArrayOutputStream();o.write(updated,0,updated.length-none.length);o.write(compact(up.nameReference('bAbsolute')));o.write(0x83);o.write(none)
  e.setObjectRawData(o.toByteArray())
 }
 up.exportTable.findAll{!it.objectInnerFullName.matches('Sticker\\d+Action')}.each{assert Arrays.equals(it.objectRawData,original[it.objectInnerFullName])}
}
new UnrealPackage(target,true).withCloseable{up->
 def factory=new UnrealSerializerFactory(new Environment(stage,['./*.usk','../../../l2/system-hud/*.u','../../../l2/animations/*.usk']))
 (0..<19).each{i->
  def o=factory.getOrCreateObject(up.exportTable.find{it.objectInnerFullName=='Sticker'+i+'Action'})
  assert up.nameTable[o.@properties.find{it.name=='AttachBoneName'}.getAt(0)].name=='Bip01_head'
  assert o.@properties.find{it.name=='bAbsolute'}.getAt(0)==true
 }
}
println 'PASS: 19 actions use Bip01_head and bAbsolute=true; all unrelated export bytes preserved; fresh native parser verified.'
