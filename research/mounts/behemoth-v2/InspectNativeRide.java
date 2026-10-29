import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
public final class InspectNativeRide {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  var p=World.getPlayer("Hellkevin");String state=p==null?"offline":("moving="+p.isMoving()+", mounted="+p.isMounted()+", mountId="+p.getMountNpcId()+", guard="+BehemothSeatSync.isSeated(p)+", xyz="+p.getX()+","+p.getY()+","+p.getZ());
  Files.writeString(Path.of(directory,"native-motion-snapshot.txt"),state+"\n");
 }
}
