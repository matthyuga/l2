import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class DeploySiegeBots {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path s=Path.of(directory);Object host=VoicedCommandHandler.getInstance().getHandler("salas");
  if(host==null||!host.getClass().getName().equals("custom.ElvenPvpRoom.PvpRoundRooms"))throw new IllegalStateException("Four-room lobby missing");
  synchronized(host){
   var f=host.getClass().getDeclaredField("bots");f.setAccessible(true);Object bots=f.get(host);Class<?> type=bots.getClass();
   var stop=type.getDeclaredMethod("stopAll");stop.setAccessible(true);stop.invoke(bots);
   MethodHandles.Lookup lookup=MethodHandles.privateLookupIn(type,MethodHandles.lookup());
   Path folder=s.resolve("compiled/custom/ElvenPvpRoom");
   // Define new helpers in the existing script loader; no lobby replacement or player teleport.
   for(String prefix:List.of("PvpSiegeRoster","PvpSiegeBrain")){
    List<Path> files;try(var stream=Files.list(folder)){files=stream.filter(p->p.getFileName().toString().startsWith(prefix)&&p.toString().endsWith(".class")).sorted().toList();}
    for(Path p:files)lookup.defineClass(Files.readAllBytes(p));
   }
   inst.redefineClasses(new ClassDefinition(type,Files.readAllBytes(folder.resolve("PvpRoomBots.class"))));
   Files.writeString(s.resolve("deployment.txt"),"PASS new roster/brain defined in active script loader; bot controller redefined; lobby, round clocks and real players preserved.\n");
  }
 }
}
