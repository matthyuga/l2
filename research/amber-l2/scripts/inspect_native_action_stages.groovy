import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def client=new File(args[0]),factory=new UnrealSerializerFactory(Environment.fromIni(new File(client,'system-hud/l2.ini')))
new UnrealPackage(new File(client,'animations/skill.usk'),true).withCloseable{up->
 for(String n:['it.2033','su.1059','su.1001','su.1010','su.1230']){
  def entry=up.exportTable.find{it.objectInnerFullName==n};if(!entry)continue
  println n
  factory.getOrCreateObject(entry).@properties.findAll{it.name.endsWith('Actions')}.each{array->
   array.getAt(0).each{item->
    println ' '+array.name+' stage='+item.find{it.name=='SpecificStage'}?.getAt(0)
    def ref=item.find{it.name=='Action'}.getAt(0),action=up.objectReference(ref)
    println '  '+action.objectFullName
    factory.getOrCreateObject(action).@properties.each{p->println '   '+p.name+'='+(p.name=='EffectClass'?up.objectReference(p.getAt(0))?.objectFullName:p.value)}
   }
  }
 }
}
