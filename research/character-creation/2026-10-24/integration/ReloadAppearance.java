import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
public class ReloadAppearance {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  for(var p:World.getPlayers())if(p.getClient()!=null)throw new IllegalStateException("Client connected; appearance reload refused");
  String name="org.l2jmobius.gameserver.network.clientpackets.CharacterCreate";
  Class<?> type=Class.forName(name);if(!inst.isModifiableClass(type))throw new IllegalStateException("Class not modifiable");
  inst.redefineClasses(new ClassDefinition(type,Files.readAllBytes(Path.of(directory,"compiled",name.replace('.','/')+".class"))));
  Files.writeString(Path.of(directory,"server-reload-proof.txt"),"PASS: CharacterCreate redefined in live GameServer; no connected player clients; no database writes.\n");
 }
}
