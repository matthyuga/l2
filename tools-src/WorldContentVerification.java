import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.config.custom.WorldContentConfig;
import org.l2jmobius.gameserver.config.custom.StartingLocationConfig;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.*;
import org.l2jmobius.gameserver.entity.spawns.AutoSpawnHandler;
public class WorldContentVerification {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  if(!WorldContentConfig.CUSTOM_WORLD_ONLY)throw new AssertionError("World profile disabled");
  if(World.getPlayers().stream().anyMatch(p->p.getClient()!=null))throw new IllegalStateException("Client connected; idle diagnostic cancelled");
  int npcs=0;for(var obj:World.getVisibleObjects())if(obj instanceof Npc n){if(!WorldContentProbe.ours(n.getId()))throw new AssertionError("Classic NPC still present: "+n.getId());npcs++;}
  if(npcs!=8)throw new AssertionError("Our NPC count: "+npcs);
  if(!ScriptManager.getInstance().getQuests().isEmpty())throw new AssertionError("Classic quests loaded");
  if(!RaidBossSpawnManager.getInstance().getBosses().isEmpty()||!RaidBossSpawnManager.getInstance().getSpawns().isEmpty())throw new AssertionError("Classic raids loaded");
  if(AutoSpawnHandler.getInstance().size()!=0)throw new AssertionError("Classic random spawns loaded");
  for(String command:new String[]{"giran","arena","agite","clanlab","raza","skills","enchantskills"})if(VoicedCommandHandler.getInstance().getHandler(command)==null)throw new AssertionError("Missing project command: "+command);
  for(int id=1;id<=9;id++){if(id==3)continue;var siege=CastleManager.getInstance().getCastleById(id).getSiege();var scheduled=siege.getClass().getDeclaredField("_scheduledStartSiegeTask");scheduled.setAccessible(true);if(scheduled.get(siege)!=null)throw new AssertionError("Unused castle schedule initialized: "+id);}
  var roster=Arrays.stream(inst.getAllLoadedClasses()).filter(c->c.getName().equals("custom.NormalNpcRoster.NormalNpcRoster")).findFirst().orElseThrow();var ready=roster.getDeclaredField("READY");ready.setAccessible(true);if(!ready.getBoolean(null))throw new AssertionError("Roster not ready");
  if(!StartingLocationConfig.CUSTOM_STARTING_LOC||StartingLocationConfig.CUSTOM_STARTING_LOC_X!=83020||StartingLocationConfig.CUSTOM_STARTING_LOC_Y!=147880)throw new AssertionError("Giran start disabled");
  Files.writeString(Path.of(dir,"runtime-verification.txt"),"PASS\nclassic_npcs=0\nour_npcs=8\nclassic_quests=0\nclassic_raids=0\nclassic_random_spawns=0\nunused_castle_schedules=0\nproject_commands=7\nroster_ready=true\nnew_characters_start_in_giran=true\nexplicit_gc_requested=true\n");
  System.gc();
 }
}
