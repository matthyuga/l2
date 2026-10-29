import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RefreshTrial{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory);Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){List<ClassDefinition> defs=new ArrayList<>();
   for(String name:List.of("RoomTacticalPolicy","PvpTacticalEngine"))defs.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom."+name),Files.readAllBytes(dir.resolve("compiled/custom/ElvenPvpRoom/"+name+".class"))));
   defs.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom.TacticalBenchmark"),Files.readAllBytes(dir.resolve("test-classes/custom/ElvenPvpRoom/TacticalBenchmark.class"))));
   inst.redefineClasses(defs.toArray(ClassDefinition[]::new));
  }
 }
}
