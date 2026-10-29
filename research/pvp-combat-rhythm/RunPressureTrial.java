import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RunPressureTrial {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
  for(String prefix:List.of("RoomCombatRhythm","RoomClassSkills","PressureBaseline","PressureCandidate","PressureTrial")){
   List<Path> files;try(var stream=Files.list(folder)){files=stream.filter(p->(p.getFileName().toString().equals(prefix+".class")||p.getFileName().toString().startsWith(prefix+"$"))&&p.toString().endsWith(".class")).sorted().toList();}
   for(Path p:files)lookup.defineClass(Files.readAllBytes(p));
  }
  try{loader.loadClass("custom.ElvenPvpRoom.PressureTrial").getMethod("run",Path.class).invoke(null,dir);}catch(java.lang.reflect.InvocationTargetException error){Files.writeString(dir.resolve("trial-error.txt"),error.getCause().toString());throw error;}
 }
}
