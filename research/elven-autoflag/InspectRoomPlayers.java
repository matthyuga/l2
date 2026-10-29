import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
public class InspectRoomPlayers {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  StringBuilder b=new StringBuilder();int count=0;
  for(var p:World.getPlayers())if(p.getClient()!=null && p.isOnline()){
   count++;b.append("Character: ").append(p.getName()).append("; id=").append(p.getObjectId()).append("; instance=").append(p.getInstanceId()).append("; position=").append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append("; flag=").append(p.getPvpFlag()).append('\n');
  }
  b.append("Connected clients: ").append(count).append('\n');Files.writeString(Path.of(directory,"connected-client-room-state.txt"),b);
 }
}
