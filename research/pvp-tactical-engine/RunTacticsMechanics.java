import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RunTacticsMechanics{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
  Class<?> type=lookup.defineClass(Files.readAllBytes(Path.of(directory,"test-classes/custom/ElvenPvpRoom/TacticalMechanics.class")));
  try{type.getMethod("run",Path.class).invoke(null,Path.of(directory));}catch(java.lang.reflect.InvocationTargetException e){Files.writeString(Path.of(directory,"mechanics-error.txt"),e.getCause().toString());throw e;}
 }
}
