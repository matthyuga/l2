import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RunNativeNavigation {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
  for(String name:List.of("RoomRouteNetwork","RoomNavigator","RoomNavigator$State","NativeNavigationTrial"))lookup.defineClass(Files.readAllBytes(folder.resolve(name+".class")));
  try{loader.loadClass("custom.ElvenPvpRoom.NativeNavigationTrial").getMethod("run",Path.class).invoke(null,dir);}catch(java.lang.reflect.InvocationTargetException e){Files.writeString(dir.resolve("native-walk-error.txt"),e.getCause().toString());throw e;}
 }
}
