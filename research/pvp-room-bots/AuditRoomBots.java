import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
public class AuditRoomBots {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  long bots=World.getPlayers().stream().filter(p->"hellgames-room-bots".equals(p.getAccountName())).count();
  var f=PvpFlagTaskManager.class.getDeclaredField("FORCED");f.setAccessible(true);var owners=(Map<Player,?>)f.get(null);
  long botOwners=owners.keySet().stream().filter(p->"hellgames-room-bots".equals(p.getAccountName())).count();
  var m=RoomCombatRules.class.getDeclaredField("MEMBERS");m.setAccessible(true);int memberships=((Map<?,?>)m.get(null)).size();
  Object handler=org.l2jmobius.gameserver.handler.VoicedCommandHandler.getInstance().getHandler("salas");
  String active=handler==null?"none":handler.getClass().getName();
  if(bots!=0||botOwners!=0||memberships!=0)throw new IllegalStateException("Bot cleanup incomplete");
  Files.writeString(Path.of(directory,"final-runtime-audit.json"),"{\"status\":\"PASS\",\"bots_remaining\":"+bots+",\"bot_flag_owners\":"+botOwners+",\"round_combat_members\":"+memberships+",\"active_lobby\":\""+active+"\"}\n");
 }
}
