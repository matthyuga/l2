import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RefreshSiegeBrain {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");
  synchronized(host){Class<?> brain=host.getClass().getClassLoader().loadClass("custom.ElvenPvpRoom.PvpSiegeBrain");inst.redefineClasses(new ClassDefinition(brain,Files.readAllBytes(Path.of(dir,"compiled/custom/ElvenPvpRoom/PvpSiegeBrain.class"))));}
 }
}
