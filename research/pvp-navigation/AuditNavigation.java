import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class AuditNavigation {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();Class<?> mode=loader.loadClass("custom.ElvenPvpRoom.RoundState$Mode");var get=host.getClass().getDeclaredMethod("botParticipants",mode);get.setAccessible(true);
  var owned=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster").getMethod("owned",Player.class);var report=loader.loadClass("custom.ElvenPvpRoom.PvpTacticalEngine").getMethod("report",Player.class);var nativeReport=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeCombat").getMethod("report",Player.class);
  StringBuilder log=new StringBuilder();
  for(int sample=0;sample<3;sample++){
   synchronized(host){log.append("SAMPLE ").append(sample).append('\n');for(Object m:mode.getEnumConstants())for(Player p:(List<Player>)get.invoke(host,m))if((boolean)owned.invoke(null,p)){
    log.append(p.getName()).append(" xyz=").append(p.getLocation()).append(" dead=").append(p.isDead()).append(" summon=").append(p.hasSummon()?p.getSummon().getName():"none").append(" cubics=").append(p.getCubics().keySet()).append(' ').append(report.invoke(null,p)).append(" native=").append(nativeReport.invoke(null,p)).append('\n');
   }}
   Files.writeString(Path.of(directory,"live-navigation-audit.txt"),log);if(sample<2)Thread.sleep(20000);
  }
 }
}
