import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class ApplySpatialBags {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){
   List<ClassDefinition> defs=new ArrayList<>();for(String name:List.of("PvpTacticalEngine","RoomSpatialTactics","PvpSiegeCombat"))defs.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom."+name),Files.readAllBytes(folder.resolve(name+".class"))));inst.redefineClasses(defs.toArray(ClassDefinition[]::new));
   var roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");var field=roster.getDeclaredField("OWNED");field.setAccessible(true);List<Player> actors;
   synchronized(roster){actors=new ArrayList<>(((Map<Player,?>)field.get(null)).keySet());}
   var stock=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeCombat").getMethod("stock",Player.class);StringBuilder log=new StringBuilder();
   for(Player p:actors){int before=p.getCurrentLoad();stock.invoke(null,p);log.append(p.getName()).append(" load ").append(before).append(" -> ").append(p.getCurrentLoad()).append(" max=").append(p.getMaxLoad()).append(" overloaded=").append(p.isOverloaded()).append(" penalty=").append(p.getWeightPenalty()).append('\n');}
   Files.writeString(dir.resolve("bags-audit.txt"),log);
   for(Player p:actors)if(p.isOverloaded())throw new IllegalStateException("Still overloaded: "+p.getName());
   Files.writeString(dir.resolve("bags-status.txt"),"PASS all "+actors.size()+" reserved actors below overload after native inventory adjustment; original quantities remain in roster snapshot.\n");
  }
 }
}
