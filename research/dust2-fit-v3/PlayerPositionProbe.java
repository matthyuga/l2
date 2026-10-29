import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
public class PlayerPositionProbe {
 public static void agentmain(String dir,Instrumentation i)throws Exception {
  StringBuilder out=new StringBuilder();
  for(var p:World.getPlayers())if(p.getClient()!=null)out.append(p.getName()+" "+p.getX()+" "+p.getY()+" "+p.getZ()+" heading="+p.getHeading()+" radius="+p.getCollisionRadius()+" height="+p.getCollisionHeight()+"\n");
  Files.writeString(Path.of(dir,"player-position.txt"),out);
 }
}
