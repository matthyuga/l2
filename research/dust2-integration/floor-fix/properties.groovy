import acmi.l2.clientmod.unreal.*
import acmi.l2.clientmod.unreal.properties.PropertiesUtil
 def f=new UnrealSerializerFactory(new Environment(new File('E:/l2-local'),['../l2/system-hud/*.u']))
for(def n in ['Engine.StaticMesh','Engine.StaticMeshActor','Engine.Actor']) {println(n);PropertiesUtil.getPropertyFields(f,n).filter{p->p.entry.objectName.name.toLowerCase().contains('coll')||p.entry.objectName.name.toLowerCase().contains('block')||p.entry.objectName.name.toLowerCase().contains('simple')}.forEach{println(it.entry.objectName.name)}}
for(def n in ['Engine.StaticMeshActor','Engine.Actor']) {println('DEFAULTS '+n);def c=f.getStruct(n).orElse(null);println(c?.@properties);println(c?.scriptText)}