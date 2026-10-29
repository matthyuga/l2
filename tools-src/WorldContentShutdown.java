import java.lang.instrument.Instrumentation;
import org.l2jmobius.gameserver.Shutdown;
import org.l2jmobius.gameserver.entity.World;
public class WorldContentShutdown {
 public static void agentmain(String unused,Instrumentation i){
  if(World.getPlayers().stream().anyMatch(p->p.getClient()!=null))throw new IllegalStateException("A client connected during maintenance preparation");
  Shutdown.getInstance().startShutdown(null,5,false);
 }
}
