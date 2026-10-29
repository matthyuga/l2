import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RunTacticsMechanicsV2{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  ClassLoader loader=VoicedCommandHandler.getInstance().getHandler("salas").getClass().getClassLoader();Class<?> type=loader.loadClass("custom.ElvenPvpRoom.TacticalMechanics");
  inst.redefineClasses(new ClassDefinition(type,Files.readAllBytes(Path.of(directory,"test-classes/custom/ElvenPvpRoom/TacticalMechanics.class"))));
  try{type.getMethod("run",Path.class).invoke(null,Path.of(directory));}catch(java.lang.reflect.InvocationTargetException e){Files.writeString(Path.of(directory,"mechanics-error.txt"),e.getCause().toString());throw e;}
 }
}
