import java.lang.instrument.*;
import java.nio.file.*;
import java.util.jar.JarFile;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.network.clientpackets.ValidatePosition;
import org.l2jmobius.gameserver.network.clientpackets.MoveToLocation;
public class DeployRoomSync {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  Path s=Path.of(directory);Object handler=VoicedCommandHandler.getInstance().getHandler("salas");
  if(handler==null)throw new IllegalStateException("Lobby missing");
  inst.appendToSystemClassLoaderSearch(new JarFile(s.resolve("support.jar").toFile()));
  Class.forName("org.l2jmobius.gameserver.managers.RoomTeleportSync",true,ClassLoader.getSystemClassLoader());
  synchronized(handler){inst.redefineClasses(
   new ClassDefinition(ValidatePosition.class,Files.readAllBytes(s.resolve("compiled/org/l2jmobius/gameserver/network/clientpackets/ValidatePosition.class"))),
   new ClassDefinition(MoveToLocation.class,Files.readAllBytes(s.resolve("compiled/org/l2jmobius/gameserver/network/clientpackets/MoveToLocation.class"))),
   new ClassDefinition(handler.getClass(),Files.readAllBytes(s.resolve("compiled/custom/ElvenPvpRoom/PvpRooms.class")))
  );}
  Files.writeString(s.resolve("deployment.txt"),"PASS: registered lobby and two packet callbacks redefined; new synchronization helper appended. No restart, immunity or resource restoration.\n");
 }
}
