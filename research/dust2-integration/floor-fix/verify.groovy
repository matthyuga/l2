import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),stage=new File(root,'research/dust2-integration/floor-fix/stage')
def f=new UnrealSerializerFactory(new Environment(root,['research/dust2-integration/floor-fix/stage/StaticMeshes/*.usx','../l2/system-hud/*.u']))
int meshes=0,faces=0,nodes=0
new UnrealPackage(new File(stage,'StaticMeshes/HGDust2Arena.usx'),true).withCloseable { up ->
 assert up.version==123&&up.license==28
 up.exportTable.findAll{it.fullClassName=='Engine.StaticMesh'}.each {entry ->
  def o=f.getOrCreateObject(entry)
  assert o.vertexStream.vert.length>0&&o.indexStream1.indices.length>0
  assert o.u1.length>0&&o.u2.length>0&&o.u3.length>0
  assert o.offsetAfterU1>entry.offset&&o.offsetAfterU2>o.offsetAfterU1&&o.offsetAfterU3>o.offsetAfterU2
  meshes++;faces+=o.u1.length;nodes+=o.u2.length
 }
}
assert meshes==37&&faces==9932
println "PASS: Interlude full native deserialization, ${meshes} meshes, ${faces} collision faces, ${nodes} collision nodes."
