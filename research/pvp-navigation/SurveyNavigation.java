import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.geoengine.pathfinding.PathFinding;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class SurveyNavigation {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();Class<?> mode=loader.loadClass("custom.ElvenPvpRoom.RoundState$Mode");var get=host.getClass().getDeclaredMethod("botParticipants",mode);get.setAccessible(true);
  List<Player> actors=new ArrayList<>();synchronized(host){for(Object m:mode.getEnumConstants())actors.addAll((List<Player>)get.invoke(host,m));}
  StringBuilder log=new StringBuilder();var geo=GeoEngine.getInstance();
  for(Player p:actors){
   log.append("ACTOR ").append(p.getName()).append(" class=").append(p.getPlayerClass()).append(" xyz=").append(p.getLocation()).append(" client=").append(p.getClient()!=null).append(" dead=").append(p.isDead()).append(" disabled=").append(p.isMovementDisabled()).append(" AI=").append(p.getAI().getIntention()).append(" target=").append(p.getTarget()==null?"none":p.getTarget().getName()).append(" summon=").append(p.hasSummon()?p.getSummon().getName():"none").append('\n');
   if(p.getClient()!=null)continue;
   log.append("TACTICS ").append(loader.loadClass("custom.ElvenPvpRoom.PvpTacticalEngine").getMethod("report",Player.class).invoke(null,p)).append('\n');
   log.append("SUMMON_SKILLS ");for(var s:p.getAllSkills())if(s.getName().startsWith("Summon ")&&!s.getName().contains("Siege"))log.append(s.getId()).append(':').append(s.getName()).append("[item=").append(s.getItemConsumeId()).append('x').append(s.getItemConsumeCount()).append("] ");log.append('\n');
   for(Player q:actors)if(q!=p&&q.getClient()==null&&q.getInstanceId()==p.getInstanceId()&&!q.isDead()&&(Math.abs(q.getZ()-p.getZ())>100||q.getName().equals("ArenaMalrik"))){
    var path=PathFinding.getInstance().findPath(p.getX(),p.getY(),p.getZ(),q.getX(),q.getY(),q.getZ(),p.getInstanceId(),true);
    log.append("ROUTE ").append(p.getName()).append(" -> ").append(q.getName()).append(" distance=").append((int)p.calculateDistance2D(q)).append(" dz=").append(q.getZ()-p.getZ()).append(" LOS=").append(geo.canSeeTarget(p,q)).append(" direct=").append(geo.canMoveToTarget(p.getX(),p.getY(),p.getZ(),q.getX(),q.getY(),q.getZ(),p.getInstanceId())).append(" nodes=").append(path==null?-1:path.size());
    if(path!=null)for(var n:path)log.append(" (").append(n.getX()).append(',').append(n.getY()).append(',').append(n.getZ()).append(')');log.append('\n');
   }
  }
  Files.writeString(Path.of(directory,"navigation-survey.txt"),log);
 }
}
