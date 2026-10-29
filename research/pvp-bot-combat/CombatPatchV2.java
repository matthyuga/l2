import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class CombatPatchV2 {
 @SuppressWarnings("unchecked")
 public static void agentmain(String arg,Instrumentation inst)throws Exception{
  String[] args=arg.split("\\|");Path dir=Path.of(args[0]);Object host=VoicedCommandHandler.getInstance().getHandler("salas");
  ClassLoader loader=host.getClass().getClassLoader();Class<?> roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");
  Field f=roster.getDeclaredField("OWNED");f.setAccessible(true);List<Player> players;
  synchronized(host){players=new ArrayList<>(((Map<Player,?>)f.get(null)).keySet());}
  if(args[1].equals("deploy")){
   synchronized(host){
    Path classes=dir.resolve("compiled/custom/ElvenPvpRoom");
    loader.loadClass("custom.ElvenPvpRoom.PvpSiegeCombat");
    inst.redefineClasses(new ClassDefinition(roster,Files.readAllBytes(classes.resolve("PvpSiegeRoster.class"))),new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom.PvpSiegeBrain"),Files.readAllBytes(classes.resolve("PvpSiegeBrain.class"))));
    Class<?> combat=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeCombat");
    for(Player p:players){combat.getMethod("stock",Player.class).invoke(null,p);p.abortAttack();}
    Files.writeString(dir.resolve("deployment.txt"),"PASS combat helper defined; brain and roster redefined; stocked "+players.size()+" owned bots. No lobby reload, real-player relocation or resource change.\n");
   }
  }
  Class<?> combat=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeCombat");
  StringBuilder out=new StringBuilder();
  synchronized(host){for(Player p:players){out.append(p.getName()).append(" class=").append(p.getPlayerClass()).append(" mage=").append(p.isMageClass()).append(" dead=").append(p.isDead()).append(" instance=").append(p.getInstanceId()).append(" MP=").append(Math.round(p.getCurrentMp())).append('/').append(p.getMaxMp()).append(" summon=").append(p.hasSummon()).append(" TP=").append(p.isAffectedBySkill(1262)).append(" weapon=").append(p.getActiveWeaponItem()==null?"none":p.getActiveWeaponItem().getCrystalTypePlus()).append(" stats=").append(combat.getMethod("report",Player.class).invoke(null,p)).append('\n');}}
  Files.writeString(dir.resolve(args[1].equals("deploy")?"initial.txt":"live-audit.txt"),out.toString());
 }
}
