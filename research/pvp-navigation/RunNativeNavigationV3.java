import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RunNativeNavigationV3 {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
  lookup.defineClass(Files.readAllBytes(folder.resolve("RoomRouteNetwork.class")));inst.redefineClasses(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom.RoomNavigator"),Files.readAllBytes(folder.resolve("RoomNavigator.class"))));
  try{loader.loadClass("custom.ElvenPvpRoom.NativeNavigationTrial").getMethod("run",Path.class).invoke(null,dir);}catch(java.lang.reflect.InvocationTargetException e){Files.writeString(dir.resolve("native-walk-error.txt"),e.getCause().toString());throw e;}
 }
}
