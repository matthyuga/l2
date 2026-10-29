import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RunTacticsTrial{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  ClassLoader loader=VoicedCommandHandler.getInstance().getHandler("salas").getClass().getClassLoader();
  try{loader.loadClass("custom.ElvenPvpRoom.TacticalBenchmark").getMethod("run",Path.class).invoke(null,Path.of(directory));}
  catch(java.lang.reflect.InvocationTargetException e){Files.writeString(Path.of(directory,"trial-error.txt"),e.getCause().toString()+"\n");throw e;}
 }
}
