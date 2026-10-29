import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.actor.Player;
public class AuditLiveSiegeBots {
 static Object field(Object o,String n)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(o);}
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();Class<?> roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");Field owned=roster.getDeclaredField("OWNED");owned.setAccessible(true);
  Map<Integer,int[]> positions=new HashMap<>();Map<Integer,Double> hp=new HashMap<>();List<Player> players;
  synchronized(host){players=new ArrayList<>(((Map<Player,?>)owned.get(null)).keySet());for(Player p:players){positions.put(p.getObjectId(),new int[]{p.getX(),p.getY()});hp.put(p.getObjectId(),p.getCurrentHp()+p.getCurrentCp());}}
  Thread.sleep(6000);int moved=0,healthChanged=0,clan=0,solo=0;Set<Integer> parties=new HashSet<>(),classes=new HashSet<>(),instances=new HashSet<>();String status;
  synchronized(host){
   for(Player p:players){int[] at=positions.get(p.getObjectId());if(Math.hypot(p.getX()-at[0],p.getY()-at[1])>30)moved++;if(Math.abs(p.getCurrentHp()+p.getCurrentCp()-hp.get(p.getObjectId()))>1)healthChanged++;if(p.getClan()!=null)clan++;else solo++;classes.add(p.getPlayerClass().getId());instances.add(p.getInstanceId());if(p.isInParty())parties.add(p.getParty().getLeaderObjectId());if(p.getClient()!=null)throw new IllegalStateException("Borrowed real client");}
   Object bots=field(host,"bots");status=(String)bots.getClass().getMethod("status").invoke(bots);
  }
  if(players.size()!=24||instances.size()!=4||clan==0||solo==0||parties.size()<4||classes.size()<4||moved==0)throw new IllegalStateException("Live roster/movement check failed: count="+players.size()+" moved="+moved);
  Files.writeString(Path.of(directory,"live-audit.json"),"{\"status\":\"PASS\",\"bots\":"+players.size()+",\"rooms\":"+instances.size()+",\"with_clan\":"+clan+",\"without_clan\":"+solo+",\"classes\":"+classes.size()+",\"parties\":"+parties.size()+",\"moved_in_6s\":"+moved+",\"hp_cp_changed\":"+healthChanged+"}\n");
  Files.writeString(Path.of(directory,"live-status.txt"),status+"\n");
 }
}
