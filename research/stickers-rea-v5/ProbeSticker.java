import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public final class ProbeSticker {
 public static void agentmain(String dir, Instrumentation ignored) throws Exception {
  var out=new StringBuilder();
  for(var p:World.getPlayers()) if(p.getClient()!=null && p.getName().equalsIgnoreCase("Hellkevin")) {
   out.append(p.getName()).append(" online=").append(p.isOnline()).append("\n");
   VoicedCommandHandler.getInstance().getHandler("sticker").onCommand("sticker",p,"1");
  }
  Files.writeString(Path.of(dir,"probe.txt"),out.toString());
 }
}
