import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class AuditSpatial {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  Class<?> mode=loader.loadClass("custom.ElvenPvpRoom.RoundState$Mode"),engine=loader.loadClass("custom.ElvenPvpRoom.PvpTacticalEngine"),roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");
  var participants=host.getClass().getDeclaredMethod("botParticipants",mode);participants.setAccessible(true);
  var report=engine.getMethod("report",Player.class);var owned=roster.getMethod("owned",Player.class);
  Map<Player,double[]> previous=new IdentityHashMap<>();Map<Player,Integer> moves=new IdentityHashMap<>(),respawns=new IdentityHashMap<>();StringBuilder log=new StringBuilder();
  synchronized(host){for(Object m:mode.getEnumConstants())for(Player p:(List<Player>)participants.invoke(host,m))if((boolean)owned.invoke(null,p)){previous.put(p,new double[]{p.getX(),p.getY(),p.isDead()?1:0});log.append("BEFORE ").append(p.getName()).append(' ').append(report.invoke(null,p)).append('\n');}}
  for(int sample=0;sample<16;sample++){
   Thread.sleep(2000);
   synchronized(host){for(var entry:previous.entrySet()){
    Player p=entry.getKey();double[] old=entry.getValue();double distance=Math.hypot(p.getX()-old[0],p.getY()-old[1]);
    if(old[2]>0&&!p.isDead()){respawns.merge(p,1,Integer::sum);log.append("RESPAWN ").append(p.getName()).append(" xyz=").append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append('\n');}
    else if(old[2]==0&&!p.isDead()&&distance>20&&distance<600)moves.merge(p,1,Integer::sum);
    old[0]=p.getX();old[1]=p.getY();old[2]=p.isDead()?1:0;
   }}
  }
  synchronized(host){for(Player p:previous.keySet())log.append("AFTER ").append(p.getName()).append(" native_move_samples=").append(moves.getOrDefault(p,0)).append(" respawns=").append(respawns.getOrDefault(p,0)).append(" xyz=").append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append(' ').append(report.invoke(null,p)).append('\n');}
  Files.writeString(Path.of(directory,"live-spatial-audit.txt"),log);
 }
}
