import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory

def root=new File(args[0]),stage=new File(root,'research/gludio-sky/stage')
def f=new UnrealSerializerFactory(new Environment(root,['research/gludio-sky/stage/StaticMeshes/*.usx','research/gludio-sky/stage/Textures/*.utx','../l2/system-hud/*.u','../l2/textures/*.utx','../l2/systextures/*.utx']))
int count=0
new UnrealPackage(new File(stage,'StaticMeshes/HGGludioSky_S.usx'),true).withCloseable{up->
 assert up.version==123&&up.license==28
 up.exportTable.findAll{it.fullClassName=='Engine.StaticMesh'}.each{entry->
  def o=f.getOrCreateObject(entry)
  assert o.vertexStream.vert.length>0&&o.indexStream1.indices.length>0:entry.objectInnerFullName
  assert o.offsetAfterU1>entry.offset && o.offsetAfterU2>o.offsetAfterU1 && o.offsetAfterU3>o.offsetAfterU2:entry.objectInnerFullName
  count++
 }
}
assert count==98
println 'PASS: 98 converted meshes fully deserialized with Interlude license 28, geometry and three collision lazy arrays.'
