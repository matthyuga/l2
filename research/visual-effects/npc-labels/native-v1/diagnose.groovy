import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def f=new UnrealSerializerFactory(Environment.fromIni(new File('E:/l2/system-hud/l2.ini')))
for(def spec:[['LineageEffect.u','ra_boss_halo_a_ca'],['Engine.u','Emitter'],['Engine.u','ParticleEmitter'],['HellgamesLabelsV1.u','EventGold']]){
 new UnrealPackage(new File('E:/l2/system-hud/'+spec[0]),true).withCloseable{up->
 def e=up.exportTable.find{it.objectInnerFullName==spec[1]};println spec[0]+' '+spec[1]+' class='+e?.fullClassName
 if(e){def o=f.getOrCreateObject(e);o.@properties.each{println it.name+'='+it.value};println 'tail='+e.objectRawData[-Math.min(e.objectRawData.length,40)..-1].collect{String.format('%02x',it&255)}.join(' ')}
 }
}


