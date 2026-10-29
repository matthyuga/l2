import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class InspectGiranScreen {
 public static void agentmain(String output,Instrumentation unused)throws Exception{
  StringBuilder b=new StringBuilder();
  for(Player p:World.getPlayers())b.append("PLAYER ").append(p.getName()).append(" xyz=").append(p.getX()).append(",").append(p.getY()).append(",").append(p.getZ()).append(" heading=").append(p.getHeading()).append(" instance=").append(p.getInstanceId()).append(" online=").append(p.isOnline()).append('\n');
  Object h=VoicedCommandHandler.getInstance().getHandler("pantalla");
  var field=h.getClass().getDeclaredField("viewers");field.setAccessible(true);
  for(Object v:((Map<?,?>)field.get(h)).values()){
   var sf=v.getClass().getDeclaredField("screen");sf.setAccessible(true);Npc n=(Npc)sf.get(v);
   var vf=v.getClass().getDeclaredField("visible");vf.setAccessible(true);
   b.append("SCREEN id=").append(n.getObjectId()).append(" xyz=").append(n.getX()).append(',').append(n.getY()).append(',').append(n.getZ()).append(" visible=").append(vf.get(v)).append('\n');
  }
  Files.writeString(Path.of(output),b.toString());
 }
}
