import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
public class InspectSiegeBots {
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  StringBuilder b=new StringBuilder();
  for(Player p:World.getPlayers())if(p.getClient()!=null||"hellgames-room-bots".equals(p.getAccountName()))b.append(p.getName()).append(" instance=").append(p.getInstanceId()).append(" xyz=").append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append(" ai=").append(p.getAI().getIntention()).append(" moving=").append(p.isMoving()).append(" target=").append(p.getTarget()==null?"none":p.getTarget().getName()).append(" speed=").append(p.getMoveSpeed()).append(" hp=").append(p.getCurrentHp()).append(" dead=").append(p.isDead()).append('\n');
  try(var c=DatabaseFactory.getConnection();var q=c.createStatement();var rs=q.executeQuery("SELECT p.char_id,c.char_name,c.classid,c.class_index,c.clanid,c.online,p.role_name,(SELECT COUNT(*) FROM character_subclasses s WHERE s.charId=c.charId) subs FROM lab_normal_npc_profiles p JOIN characters c ON c.charId=p.char_id ORDER BY c.clanid=0,c.classid,p.npc_template_id")){
   while(rs.next())b.append("PROFILE ").append(rs.getInt(1)).append(' ').append(rs.getString(2)).append(" class=").append(rs.getInt(3)).append(" slot=").append(rs.getInt(4)).append(" clan=").append(rs.getInt(5)).append(" online=").append(rs.getInt(6)).append(" role=").append(rs.getString(7)).append(" subs=").append(rs.getInt(8)).append('\n');
  }
  Files.writeString(Path.of(dir,"baseline.txt"),b);
 }
}
