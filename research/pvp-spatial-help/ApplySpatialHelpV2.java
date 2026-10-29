import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class ApplySpatialHelpV2 {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){
   var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
   for(String name:List.of("RoomSpatialTactics","RoomCommandHelp","RoomCommandHelp$Entry","SpatialVerification")){Class<?> existing=loader.loadClass("custom.ElvenPvpRoom."+name);inst.redefineClasses(new ClassDefinition(existing,Files.readAllBytes(folder.resolve(name+".class"))));}
   // Verify new spatial helpers before changing the production controller.
   loader.loadClass("custom.ElvenPvpRoom.SpatialVerification").getMethod("run",Path.class).invoke(null,dir);
   inst.redefineClasses(new ClassDefinition(host.getClass(),Files.readAllBytes(folder.resolve("PvpRoundRooms.class"))),new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom.PvpTacticalEngine"),Files.readAllBytes(folder.resolve("PvpTacticalEngine.class"))));
   loader.loadClass("custom.ElvenPvpRoom.RoomCommandHelp").getMethod("register").invoke(null);
   Files.writeString(dir.resolve("activation.txt"),"PASS live controller and tactics redefined; ayuda/macros registered; no round reset or participant teleport.\n");
  }
 }
}
