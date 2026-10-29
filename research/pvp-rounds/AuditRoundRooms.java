import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
public class AuditRoundRooms {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  int cleaned=0;
  for(Player p:new ArrayList<>(World.getPlayers()))if(p.getName().startsWith("RoundProbe")){
   if(!p.isLabControlled()||p.getClient()!=null)throw new IllegalStateException("Unexpected real player matches probe name");
   RoomCombatRules.leave(p);p.setOnlineStatus(true,false);p.abortAttack();p.abortCast();p.stopAllEffects();p.deleteMe();p.setOnlineStatus(false,false);cleaned++;
  }
  var flags=PvpFlagTaskManager.class.getDeclaredField("FORCED");flags.setAccessible(true);
  var owners=(Map<Player,?>)flags.get(null);
  var members=RoomCombatRules.class.getDeclaredField("MEMBERS");members.setAccessible(true);
  long probes=World.getPlayers().stream().filter(p->p.getName().startsWith("RoundProbe")).count();
  long offline=owners.keySet().stream().filter(p->!p.isOnline()).count();int rules=((Map<?,?>)members.get(null)).size();
  if(probes!=0||offline!=0||rules!=0)throw new IllegalStateException("Probe/owner/combat membership leak");
  Files.writeString(Path.of(dir,"final-runtime-audit.json"),"{\"status\":\"PASS\",\"residual_probes_cleaned\":"+cleaned+",\"probes_remaining\":"+probes+",\"offline_flag_owners\":"+offline+",\"round_combat_members\":"+rules+"}\n");
 }
}
