import acmi.l2.clientmod.io.UnrealPackage
for(String path:['E:/l2-local/research/visual-effects/npc-labels/native-reference/Client Side/system/athenas.u','E:/l2/system-hud/LineageNPC.u']){
 new UnrealPackage(new File(path),true).withCloseable{up->
 println path
 up.exportTable.findAll{path.contains('athenas')||it.objectInnerFullName.startsWith('a_traderB_FHuman')}.each{println it.objectInnerFullName+' '+it.fullClassName+' '+it.size}
 }
}
