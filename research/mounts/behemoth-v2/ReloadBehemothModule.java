import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Npc;
/** Reload only our custom script; no core/game-client classes are modified. */
public final class ReloadBehemothModule {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  Class<?> target=null;Object service=null;
  for(Class<?> c:inst.getAllLoadedClasses())if(c.getName().equals("custom.BehemothTransport.BehemothTransport")){var f=c.getDeclaredField("instance");f.setAccessible(true);if(f.get(null)!=null){target=c;service=f.get(null);break;}}
  if(target==null)throw new IllegalStateException("Custom script not active");
  byte[] code=Files.readAllBytes(Path.of(directory,"BehemothTransport-fixed.class"));
  synchronized(service){
   inst.redefineClasses(new ClassDefinition(target,code));
   var f=target.getDeclaredField("owned");f.setAccessible(true);int count=0;
   for(Object trip:((Map<?,?>)f.get(service)).values()){
    var field=trip.getClass().getDeclaredField("npc");field.setAccessible(true);Npc npc=(Npc)field.get(trip);
    if(npc.getTemplate().getFCollisionHeight()!=54||npc.getTemplate().getFCollisionRadius()!=63)throw new IllegalStateException("Live dimensions differ");
    int x=npc.getX(),y=npc.getY(),z=npc.getZ();npc.decayMe();npc.spawnMe(x,y,z);npc.broadcastInfo();count++;
   }
   Files.writeString(Path.of(directory,"module-reload.txt"),"Reloaded custom.BehemothTransport.BehemothTransport only. New NPCs now initialize radius63/height54 BEFORE spawn.\nExisting experimental NPCs re-created client-side with corrected dimensions: "+count+"\nReal boarding remains disabled.\n");
  }
 }
}
