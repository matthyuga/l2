import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
import java.nio.ByteBuffer
import java.nio.ByteOrder
def root=new File(args[0]),stage=new File(root,'research/visual-effects/npc-labels/native-v1/compact-v3'),file=new File(stage,'HellgamesLabelsV1.u')
def compact=AmberCatalog.&compact
new UnrealPackage(file,false).withCloseable{up->
 up.addNameEntries(['UniformSize','UseRegularSizeScale'].collectEntries{[(it):UnrealPackage.DEFAULT_NAME_FLAGS]})
 up.addImportEntries(['HGLabelArtV3.EventLabel':'Engine.Texture'])
 int texture=up.importTable.find{it.objectFullName=='HGLabelArtV3.EventLabel'}.objectReference
 def factory=new UnrealSerializerFactory(new Environment(root,['research/visual-effects/npc-labels/native-v1/compact-v3/*.u','../l2/system-hud/*.u']))
 def floats={List vals->def b=ByteBuffer.allocate(vals.size()*4).order(ByteOrder.LITTLE_ENDIAN);vals.each{b.putFloat(it as float)};b.array()}
 def structprop={String name,String type,byte[] data->def out=new ByteArrayOutputStream();out.write(compact(up.nameReference(name)));out.write(0x5a);out.write(compact(up.nameReference(type)));out.write(data.length);out.write(data);out.toByteArray()}
 def props=[:]
 for(String name:['StartSizeRange','StartLocationRange'])up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}.each{e->
  def o=factory.getOrCreateObject(e)
  props[e.objectInnerFullName+'.'+name]=o.@properties.find{it.name==name}
 }
 // Property payloads have tagged range subfields; retain their native shape and
 // replace only float values using the reader/writer rather than guessing offsets.
 def rangevector={float x,float y,float z, boolean location->
  def vec=new ByteArrayOutputStream()
  ['X':x,'Y':y,'Z':z].each{axis,v->
   def range=new ByteArrayOutputStream()
   for(String edge:['Min','Max']){range.write(compact(up.nameReference(edge)));range.write(0x24);range.write(floats([v]))}
   range.write(compact(up.nameReference('None')))
   vec.write(structprop(axis,'Range',range.toByteArray()))
  }
  vec.write(compact(up.nameReference('None')));vec.toByteArray()
 }
 up.exportTable.findAll{it.fullClassName=='Engine.SpriteEmitter'}.each{e->
  byte[] raw=e.objectRawData
  // Parse and retain every existing tag, replacing selected properties below.
  def input=new acmi.l2.clientmod.io.DataInputStream(new ByteArrayInputStream(raw),null)
  def out=new ByteArrayOutputStream()
  while(true){int start=raw.length-input.available();int nameidx=input.readCompactInt();String name=up.nameTable[nameidx].name;if(name=='None')break
   int info=input.readUnsignedByte(),kind=info&15,code=(info>>4)&7
   if(kind==10)input.readCompactInt()
   int size=[1,2,4,12,16,0,0,0][code]
   if(code==5)size=input.readUnsignedByte();if(code==6)size=input.readUnsignedShort();if(code==7)size=input.readInt()
   if(kind!=3){assert !(info&128);input.skipBytes(size)}
   int end=raw.length-input.available()
   def replace=e.objectInnerFullName.endsWith('.Label')?['Texture','StartSizeRange','StartLocationRange','UniformSize','UseRegularSizeScale']:['Disabled']
   if(!(name in replace))out.write(raw,start,end-start)
  }
  if(e.objectInnerFullName.endsWith('.Label')){
   out.write(compact(up.nameReference('Texture')));out.write(0x05);out.write(compact(texture))
   out.write(structprop('StartSizeRange','RangeVector',rangevector(20f,10f,1f,false)))
   out.write(structprop('StartLocationRange','RangeVector',rangevector(0f,0f,18f,true)))
   for(String name:['UniformSize','UseRegularSizeScale']){out.write(compact(up.nameReference(name)));out.write(0x03)}
  }else{out.write(compact(up.nameReference('Disabled')));out.write(0x83)}
  out.write(compact(up.nameReference('None')));e.setObjectRawData(out.toByteArray())
 }
}
println 'PASS: compact label size20x10, height18, alpha atlas, regular/uniform scaling explicitly disabled; motes disabled.'
