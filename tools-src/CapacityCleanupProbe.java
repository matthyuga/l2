import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.data.sql.CharSummonTable;
import org.l2jmobius.gameserver.managers.CastleManager;
public class CapacityCleanupProbe {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  Path root=Path.of(dir);Set<Integer> ids=new HashSet<>();for(Path path:List.of(root,root.resolve("protected"))){String line=Files.readAllLines(path.resolve("created-ids.txt")).get(1);for(String id:line.substring(line.indexOf('[')+1,line.indexOf(']')).split(","))ids.add(Integer.parseInt(id.trim()));}
  long objects=ids.stream().filter(id->World.findObject(id)!=null).count();
  long pets=CharSummonTable.getInstance().getPets().keySet().stream().filter(ids::contains).count(),servitors=CharSummonTable.getInstance().getServitors().keySet().stream().filter(ids::contains).count();
  var anchor=Arrays.stream(inst.getAllLoadedClasses()).filter(c->c.getName().equals("custom.SoloArenaGauntlet.SoloArenaGauntlet")).findFirst().orElseThrow();
  boolean free=(Boolean)anchor.getMethod("tryClaimPilot").invoke(null);if(free)anchor.getMethod("releasePilot").invoke(null);
  boolean siege=CastleManager.getInstance().getCastleById(3).getSiege().isInProgress();
  String result="temporary_world_objects="+objects+"\ntemporary_pet_refs="+pets+"\ntemporary_servitor_refs="+servitors+"\npilot_lock_free="+free+"\nsiege_active="+siege+"\nworld_players="+World.getPlayers().size()+"\n";
  Files.writeString(root.resolve("native-cleanup.txt"),result);System.err.println("CAPACITY_CLEANUP_PROBE "+result.replace('\n',' '));
  if(objects!=0||pets!=0||servitors!=0||!free||siege)throw new IllegalStateException("Native cleanup incomplete");
 }
}
