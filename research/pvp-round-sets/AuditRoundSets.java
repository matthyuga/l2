import java.lang.instrument.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.managers.ScriptManager;
public class AuditRoundSets{
 @SuppressWarnings("unchecked")
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){
   Class<?> roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");Field owned=roster.getDeclaredField("OWNED");owned.setAccessible(true);
   List<Player> active=new ArrayList<>(),ready=new ArrayList<>();
   synchronized(roster){for(Player p:((Map<Player,?>)owned.get(null)).keySet()){if(p.getClient()!=null)throw new IllegalStateException("Borrowed real client");(p.getInstanceId()==0?ready:active).add(p);}}
   Set<Integer> identities=new HashSet<>();for(Player p:active)identities.add(p.getObjectId());for(Player p:ready)if(!identities.add(p.getObjectId()))throw new IllegalStateException("Duplicate actor");
   if(active.size()!=6||ready.size()!=6)throw new IllegalStateException("Unexpected roster count active="+active.size()+" ready="+ready.size());
   Field f=host.getClass().getDeclaredField("bots");f.setAccessible(true);Object bots=f.get(host);String status=(String)bots.getClass().getMethod("status").invoke(bots);
   if(ScriptManager.getInstance().getScript("PvpRoundRooms")!=host)throw new IllegalStateException("Lobby registry changed");
   StringBuilder out=new StringBuilder("PASS six active and six staged, disjoint native identities; production lobby registry intact.\n"+status+"\n");
   for(Player p:active)out.append("ACTIVE ").append(p.getObjectId()).append(' ').append(p.getName()).append(" instance=").append(p.getInstanceId()).append('\n');
   for(Player p:ready)out.append("READY ").append(p.getObjectId()).append(' ').append(p.getName()).append(" instance=").append(p.getInstanceId()).append('\n');
   Files.writeString(Path.of(directory,"live-audit.txt"),out);
  }
 }
}
