import acmi.l2.clientmod.io.UnrealPackage
import acmi.l2.clientmod.unreal.Environment
import acmi.l2.clientmod.unreal.UnrealSerializerFactory
def root=new File(args[0]),stage=new File(root,'research/visual-effects/npc-labels/native-v1/npc-hook-v2');stage.mkdirs()
def file=new File(stage,'HGLabelNpcV2.u')
file.bytes=new File(root,'research/visual-effects/npc-labels/native-reference/Client Side/system/athenas.u').bytes
def compact=AmberCatalog.&compact
new UnrealPackage(file,false).withCloseable{up->
 up.setUUID(UUID.randomUUID())
 up.addImportEntries(['HellgamesLabelsV1.EventGold':'Core.Class'])
 int replacement=up.importTable.find{it.objectFullName=='HellgamesLabelsV1.EventGold'}.objectReference
 byte[] before=compact(up.exportTable.find{it.objectInnerFullName=='effect'}.objectReference),after=compact(replacement)
 assert before.length==1&&after.length==1
 def e=up.exportTable.find{it.objectInnerFullName=='Npc.PostSetPawnResource'}
 byte[] raw=e.objectRawData
 def matches=[]
 for(int i=0;i<raw.length-2;i++)if((raw[i]&255)==0x20&&raw[i+1]==before[0]&&(raw[i+2]&255)==0x17)matches<<i+1
 assert matches.size()==1:'Expected exactly one Spawn class constant'
 raw[matches[0]]=after[0];e.setObjectRawData(raw)
 println 'PASS: PostSetPawnResource Spawn constant now references '+up.objectReference(replacement).objectFullName+'; bytecode length unchanged; bone attachment and cleanup preserved.'
}
def factory=new UnrealSerializerFactory(new Environment(root,['research/visual-effects/npc-labels/native-v1/npc-hook-v2/*.u','../l2/system-hud/*.u']))
new UnrealPackage(file,true).withCloseable{up->
 for(String name:['Npc','Npc.PostSetPawnResource','Npc.ClearL2Game','Npc.Detach','Npc.Destroyed']) {
  def e=up.exportTable.find{it.objectInnerFullName==name};assert e
  factory.getOrCreateObject(e)
  println 'PASS native object reads: '+name
 }
 assert up.exportTable.find{it.objectInnerFullName=='Npc'}.objectSuperClass.objectFullName=='LineageWarrior.LineagePawn'
}
