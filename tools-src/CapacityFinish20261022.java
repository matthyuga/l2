import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.Shutdown;
/** Clean native shutdown after the isolated run; reload restores normal script registration. */
public class CapacityFinish20261022 {
 public static void agentmain(String path,Instrumentation ignored)throws Exception{
  Path root=Path.of(path);
  if(!Files.exists(root.resolve("DONE"))||!Files.exists(root.resolve("cleanup-verification.json")))throw new IllegalStateException("Test and verification must finish first");
  if(!Files.readString(root.resolve("cleanup-verification.json")).contains("\"pass\": true"))throw new IllegalStateException("Cleanup verification failed");
  if(!World.getPlayers().isEmpty())throw new IllegalStateException("Players remain online; no shutdown");
  Shutdown.getInstance().startShutdown(null,1,false);
 }
}
