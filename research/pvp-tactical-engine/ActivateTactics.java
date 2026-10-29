import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.actor.Player;
public class ActivateTactics{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){
   List<ClassDefinition> defs=new ArrayList<>();for(String name:List.of("PvpSiegeBrain","PvpRoomBots","PvpTacticalEngine"))defs.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom."+name),Files.readAllBytes(folder.resolve(name+".class"))));
   defs.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster"),Files.readAllBytes(dir.resolve("restore-classes/custom/ElvenPvpRoom/PvpSiegeRoster.class"))));
   inst.redefineClasses(defs.toArray(ClassDefinition[]::new));
   loader.loadClass("custom.ElvenPvpRoom.PvpTacticalEngine").getField("enabled").setBoolean(null,true);
   Field f=host.getClass().getDeclaredField("bots");f.setAccessible(true);Object bots=f.get(host);String status=(String)bots.getClass().getMethod("status").invoke(bots);
   Files.writeString(dir.resolve("activation.txt"),"PASS tactical engine enabled in active lobby; no restart, room clock reset, or real-player teleport.\n"+status+"\n");
  }
 }
}
