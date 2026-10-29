import java.lang.instrument.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.managers.ScriptManager;
public class AuditTacticsLive{
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();Class<?> engine=loader.loadClass("custom.ElvenPvpRoom.PvpTacticalEngine"),mode=loader.loadClass("custom.ElvenPvpRoom.RoundState$Mode");
  if(!engine.getField("enabled").getBoolean(null))throw new IllegalStateException("Tactical engine disabled");
  var participants=host.getClass().getDeclaredMethod("botParticipants",mode);participants.setAccessible(true);List<Player> actors=new ArrayList<>();
  synchronized(host){for(Object m:mode.getEnumConstants())actors.addAll((List<Player>)participants.invoke(host,m));}
  Class<?> roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");actors.removeIf(p->{try{return !(boolean)roster.getMethod("owned",Player.class).invoke(null,p);}catch(Exception e){throw new RuntimeException(e);}});
  Thread.sleep(6000);StringBuilder out=new StringBuilder();int active=0;
  synchronized(host){
   for(Player p:actors){String report=(String)engine.getMethod("report",Player.class).invoke(null,p);if(report.contains("ticks="))active++;if(p.getClient()!=null)throw new IllegalStateException("Real client in bot scope");
    var target=p.getAI().getAttackTarget();if(target!=null&&target.asPlayer()!=null&&!(boolean)roster.getMethod("owned",Player.class).invoke(null,target.asPlayer()))throw new IllegalStateException("Non-owned autoattack target");
    out.append(p.getName()).append(" instance=").append(p.getInstanceId()).append(" dead=").append(p.isDead()).append(' ').append(report).append(" native=").append(loader.loadClass("custom.ElvenPvpRoom.PvpSiegeCombat").getMethod("report",Player.class).invoke(null,p)).append('\n');
   }
   if(ScriptManager.getInstance().getScript("PvpRoundRooms")!=host)throw new IllegalStateException("Lobby registration mismatch");
  }
  if(actors.isEmpty()||active==0)throw new IllegalStateException("No tactical bot activity");
  Files.writeString(Path.of(directory,"live-audit.txt"),"PASS tactical activity "+active+"/"+actors.size()+" bots; production registry intact; no real-client or non-owned autoattack target observed.\n"+out);
 }
}
