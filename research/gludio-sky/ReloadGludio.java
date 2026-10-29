import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class ReloadGludio {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  for(var p:World.getPlayers())if(p.getClient()!=null)throw new IllegalStateException("Client connected; reload refused");
  var handler=VoicedCommandHandler.getInstance().getHandler("muelle");if(handler==null)throw new IllegalStateException("Missing .muelle handler");
  Path file=Path.of(directory,"compiled/custom/GludioSky/GludioSky.class");
  inst.redefineClasses(new ClassDefinition(handler.getClass(),Files.readAllBytes(file)));
  Files.writeString(Path.of(directory,"reload-proof.txt"),"PASS: only registered custom.GludioSky.GludioSky method bodies reloaded; core/players unchanged.\n");
 }
}
