import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
def s=new File(args[0]),target=new File(s,'NexusStickersV3.patched.raw.u')
target.bytes=new File(s,'NexusStickersV3.before.raw.u').bytes
byte[] lut=new File(s,'inverse-lut.bin').bytes;assert lut.length==256
def makeFactory={->new UnrealSerializerFactory(new Environment(new File('E:/l2/system-hud'),['./*.u'])){
 @Override Optional<UnrealPackage.ExportEntry> resolveExportEntry(UnrealPackage.Entry entry){
  if(entry instanceof UnrealPackage.ExportEntry)return Optional.of((UnrealPackage.ExportEntry)entry)
  return super.resolveExportEntry(entry)
 }
}}
def factory=makeFactory()
def old=[:],offsets=[:],blocks=[]
new UnrealPackage(target,false).withCloseable{up->
 up.exportTable.each{old[it.objectInnerFullName]=it.objectRawData;offsets[it.objectInnerFullName]=[it.offset,it.size]}
 def entries=up.exportTable.findAll{it.objectInnerFullName.matches('Reaction\\d+')};assert entries.size()==19
 entries.each{e->
  def tex=factory.getOrCreateObject(e),props=tex.@properties.collectEntries{[(it.name):it.getAt(0)]}
  assert props.Format==5 && props.bAlphaTexture && props.USize==256 && props.VSize==256
  assert tex.mipMaps.length==1;byte[] data=tex.mipMaps[0].data;assert data.length==256*256*4
  byte[] raw=e.objectRawData;def hits=[]
  for(int at=0;at<=raw.length-data.length;at++)if(Arrays.mismatch(raw,at,at+data.length,data,0,data.length)==-1)hits<<at
  assert hits.size()==1:e.objectInnerFullName+' mip block ambiguous'
  int at=hits[0]
  for(int i=0;i<data.length;i++)if(i%4!=3)raw[at+i]=lut[data[i]&255]
  for(int i=3;i<data.length;i+=4)assert raw[at+i]==data[i]
  assert Arrays.equals(Arrays.copyOfRange(raw,0,at),Arrays.copyOfRange(old[e.objectInnerFullName],0,at))
  assert Arrays.equals(Arrays.copyOfRange(raw,at+data.length,raw.length),Arrays.copyOfRange(old[e.objectInnerFullName],at+data.length,raw.length))
  e.setObjectRawData(raw);assert [e.offset,e.size]==offsets[e.objectInnerFullName]
  blocks<<e.objectInnerFullName+','+(e.offset+at)+','+data.length
 }
 up.exportTable.findAll{!it.objectInnerFullName.matches('Reaction\\d+')}.each{assert Arrays.equals(it.objectRawData,old[it.objectInnerFullName])}
 assert target.length()==new File(s,'NexusStickersV3.before.raw.u').length()
}
// Fresh independent parser verifies all 19 mapped mip arrays and every preserved alpha byte.
def fresh=makeFactory()
new UnrealPackage(target,true).withCloseable{up->
 up.exportTable.findAll{it.objectInnerFullName.matches('Reaction\\d+')}.each{e->
  def tex=fresh.getOrCreateObject(e);byte[] actual=tex.mipMaps[0].data
  def row=blocks.find{it.startsWith(e.objectInnerFullName+',')}.split(',');int at=row[1].toInteger()-e.offset;byte[] before=old[e.objectInnerFullName]
  for(int i=0;i<actual.length;i++){
   int expected=(i%4==3?before[at+i]:lut[before[at+i]&255])&255
   if((actual[i]&255)!=expected)throw new IllegalStateException('Mismatch '+e.objectInnerFullName+' byte '+i+' actual='+(actual[i]&255)+' expected='+expected+' source='+(before[at+i]&255))
  }
 }
}
new File(s,'pixel-blocks.csv').text='texture,offset,length\n'+blocks.join('\n')+'\n'
println 'PASS: exactly19 world sticker RGB mip arrays compensated; alpha, sizes, offsets, mip headers and all unrelated exports byte identical; independent parser verified.'
