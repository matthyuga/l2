import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.Map;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class AuditElvenFlag {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  long probes=World.getPlayers().stream().filter(p->p.getName().equals("ElvenBoundaryProbe") || p.getName().equals("ElvenSecondProbe")).count();
  var f=PvpFlagTaskManager.class.getDeclaredField("FORCED");f.setAccessible(true);
  var owners=(Map<Player,?>)f.get(null);
  long offline=owners.keySet().stream().filter(p->!p.isOnline()).count();
  Object handler=VoicedCommandHandler.getInstance().getHandler("salas");
  var hosts=handler.getClass().getDeclaredField("hosts");hosts.setAccessible(true);
  int hostCount=((Object[])hosts.get(handler)).length;
  if(probes!=0 || offline!=0 || hostCount!=2)throw new IllegalStateException("Probe/owner/lobby cleanup mismatch");
  Files.writeString(Path.of(directory,"final-audit.json"),"{\"transient_probes_remaining\":"+probes+",\"offline_owners\":"+offline+",\"lobby_hosts\":"+hostCount+",\"status\":\"PASS\"}\n");
 }
}
