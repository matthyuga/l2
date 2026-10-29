import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class DeployRoundSets{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){
   var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
   List<Path> files;try(var stream=Files.list(folder)){files=stream.filter(p->p.getFileName().toString().startsWith("PvpRoundSets")&&p.toString().endsWith(".class")).sorted().toList();}
   for(Path p:files)lookup.defineClass(Files.readAllBytes(p));
   List<ClassDefinition> changes=new ArrayList<>();for(String name:List.of("PvpRoundRooms","PvpRoomBots","PvpSiegeRoster"))changes.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom."+name),Files.readAllBytes(folder.resolve(name+".class"))));
   inst.redefineClasses(changes.toArray(ClassDefinition[]::new));
   Files.writeString(dir.resolve("deployment.txt"),"PASS batch helper defined; lobby, bot controller and roster redefined. Current round, real parties and instance retained. Next batch prepares on the normal tick.\n");
  }
 }
}
