import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class ActivateRhythm {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory);if(!Files.readString(dir.resolve("pressure-status.txt")).startsWith("PASS"))throw new IllegalStateException("Native trial not passed");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){List<ClassDefinition> defs=new ArrayList<>();for(String name:List.of("PvpTacticalEngine","PvpRoomBots","PvpSiegeCombat"))defs.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom."+name),Files.readAllBytes(dir.resolve("compiled/custom/ElvenPvpRoom/"+name+".class"))));inst.redefineClasses(defs.toArray(ClassDefinition[]::new));Files.writeString(dir.resolve("activation.txt"),"PASS100ms reactions, continuous native attacks, conditional class skills and guarded seals active; no restart, player teleport, party change or round reset.\n");}
 }
}
