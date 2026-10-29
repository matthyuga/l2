import acmi.l2.clientmod.io.*
import acmi.l2.clientmod.unreal.*
// The old editor lacks some optional dependency metadata. Validate the package's
// actual mip data directly without flooding the console with template warnings.
java.util.logging.Logger.getLogger('').level=java.util.logging.Level.OFF
def editor=new File(args[0]),raw=new File(args[1])
def serializer=new UnrealSerializerFactory(new Environment(editor,['./*.u']))
new UnrealPackage(raw,true).withCloseable{up->
 def entries=up.exportTable.findAll{it.fullClassName=='Engine.Texture'};assert entries.size()==70
 entries.each{e->
  def texture=serializer.getOrCreateObject(e);assert texture.mipMaps.length==1
  def mip=texture.mipMaps[0];assert mip.@height==32 && mip.@width in [32,64,128,256]
  assert mip.data.length==mip.@width*mip.@height*4
  if(e.objectInnerFullName.startsWith('H'))assert mip.@width==32
 }
 println 'PASS: all 70 header/button textures have valid dimensions, uncompressed BGRA pixel data and a single mip.'
}
