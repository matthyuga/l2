import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
public class AirshipDeployAgent {
 public static void agentmain(String args,Instrumentation inst)throws Exception {
  String[] parts=args.split("\\|",2);Path dir=Path.of(parts[0]);
  long connected=World.getPlayers().stream().filter(p->p.getClient()!=null).count();
  Files.writeString(dir.resolve("server-status.txt"),"connected_clients="+connected+"\n");
  if(parts.length>1 && parts[1].equals("shutdown")) {
   if(connected!=0)throw new IllegalStateException("Connected clients: refuse deployment shutdown");
   Files.writeString(dir.resolve("shutdown-request.txt"),"Graceful shutdown requested, no connected clients.\n");
   org.l2jmobius.gameserver.Shutdown.getInstance().startShutdown(null,5,false);
  }
 }
}
