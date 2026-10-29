import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.Shutdown;
public class ActivatePvpShutdown {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  long clients=World.getPlayers().stream().filter(p->p.isOnline()&&p.getClient()!=null).count();
  if(clients!=0)throw new IllegalStateException("Connected clients remain: "+clients);
  Files.writeString(Path.of(dir,"activation-shutdown.txt"),"No connected clients. Graceful GameServer shutdown requested for PvP activation.\n");
  Shutdown.getInstance().startShutdown(null,3,false);
 }
}
