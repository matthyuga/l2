import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def client=new File(args[0]),f=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
new UnrealPackage(new File(client,'system-hud/Engine.u'),true).withCloseable{up->
 up.exportTable.findAll{it.fullClassName=='Core.Enum'&&it.objectInnerFullName==~/(?i).*(Coordinate|Direction|AttachOn).*/}.each{e->
  def o=f.getOrCreateObject(e);println e.objectInnerFullName+' '+o.values
 }
}
new UnrealPackage(new File(client,'system-hud/LineageEffect.u'),true).withCloseable{up->
 for(String n:['it_scroll_of_escape_ca.MeshEmitter3','NArrow']){
  def e=up.exportTable.find{it.objectInnerFullName==n};if(!e)continue
  def o=f.getOrCreateObject(e);println 'OBJ '+n
  o.@properties.each{p->def v=p.value;if(p.name in ['StaticMesh','Mesh'])v=up.objectReference(p.getAt(0))?.objectFullName;println p.name+'='+v}
 }
}
