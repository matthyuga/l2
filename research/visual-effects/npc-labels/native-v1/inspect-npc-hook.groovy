import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def env=new Environment(new File('E:/l2-local'),['research/visual-effects/npc-labels/native-reference/Client Side/system/*.u','../l2/system-hud/*.u'])
def f=new UnrealSerializerFactory(env)
new UnrealPackage(new File('E:/l2-local/research/visual-effects/npc-labels/native-reference/Client Side/system/athenas.u'),true).withCloseable{up->
 for(String name:['Npc.ScriptText','effect.ScriptText']){
 def o=f.getOrCreateObject(up.exportTable.find{it.objectInnerFullName==name});println name+'\n'+o.text
 }
 def e=up.exportTable.find{it.objectInnerFullName=='Npc.PostSetPawnResource'};println 'imports='+up.importTable.collect{it.objectFullName+' '+it.fullClassName}.join('\n')
 println 'classRefs='+up.exportTable.findAll{it.objectInnerFullName.startsWith('Npc.')&&it.fullClassName=='Core.Function'}.collect{it.objectInnerFullName+' '+it.objectRawData.encodeHex()}.join('\n')
}
