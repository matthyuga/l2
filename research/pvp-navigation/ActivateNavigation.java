import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class ActivateNavigation {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory);if(!Files.readString(dir.resolve("native-walk-status.txt")).startsWith("PASS"))throw new IllegalStateException("Native walking not certified");
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){
   Class<?> type=loader.loadClass("custom.ElvenPvpRoom.PvpTacticalEngine");inst.redefineClasses(new ClassDefinition(type,Files.readAllBytes(dir.resolve("compiled/custom/ElvenPvpRoom/PvpTacticalEngine.class"))));
   type.getField("enabled").setBoolean(null,true);
   Files.writeString(dir.resolve("activation.txt"),"PASS navigation and hybrid utilities active without restarting rooms, changing parties or teleporting participants.\n");
  }
 }
}
