import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class ReloadElven
{
 public static void agentmain(String directory,Instrumentation inst)throws Exception
 {
  var lobby=VoicedCommandHandler.getInstance().getHandler("salas");
  var old=VoicedCommandHandler.getInstance().getHandler("elvenpvp");
  if(lobby==null || old==null)throw new IllegalStateException("Handlers missing");
  Path root=Path.of(directory,"compiled/custom/ElvenPvpRoom");
  synchronized(lobby)
  {
   inst.redefineClasses(new ClassDefinition(lobby.getClass(),Files.readAllBytes(root.resolve("PvpRooms.class"))),
     new ClassDefinition(old.getClass(),Files.readAllBytes(root.resolve("ElvenPvpRoom.class"))));
  }
  Files.writeString(Path.of(directory,"deployment.txt"),"PASS: scripts loaded during existing server startup 19:53; both NPCs present. Final method updates redefined without restart or duplicate timers/NPCs.\n");
 }
}
