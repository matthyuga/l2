import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
public class ReadCameraState {
 public static void agentmain(String file, Instrumentation ignored) throws Exception {
  var p=World.getPlayer(268436061);
  Files.writeString(Path.of(file),p==null?"offline\n":"observer="+p.inObserverMode()+" paralyzed="+p.isParalyzed()+" movementDisabled="+p.isMovementDisabled()+" moving="+p.isMoving()+" intention="+p.getAI().getIntention()+" xyz="+p.getX()+","+p.getY()+","+p.getZ()+"\n");
 }
}
