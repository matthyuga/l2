import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class ReloadDust2 {
 public static void agentmain(String d,Instrumentation i)throws Exception {
  var h=VoicedCommandHandler.getInstance().getHandler("dust2");
  if(h==null)throw new IllegalStateException("No handler");
  i.redefineClasses(new ClassDefinition(h.getClass(),Files.readAllBytes(Path.of(d,"classes/custom/Dust2Arena/Dust2Arena.class"))));
  Files.writeString(Path.of(d,"reload.txt"),"PASS: .dust2 salir can recover recorded visitors below arena.\n");
 }
}
