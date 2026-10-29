import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class TraceRoomInstance {
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  Path p=Path.of(dir);byte[] original=Files.readAllBytes(p.resolve("WorldObject.original.class"));
  try {
   inst.redefineClasses(new ClassDefinition(WorldObject.class,Files.readAllBytes(p.resolve("instance-trace-classes/org/l2jmobius/gameserver/entity/WorldObject.class"))));
   var player=World.getPlayer(268473899);if(player==null || player.getClient()==null)throw new IllegalStateException("Client unavailable");
   VoicedCommandHandler.getInstance().getHandler("salas").onCommand("salas",player,"entrar");
   StringBuilder b=new StringBuilder();
   for(int i=0;i<25;i++){b.append(i*100).append("ms instance=").append(player.getInstanceId()).append(" xyz=").append(player.getX()).append(',').append(player.getY()).append(',').append(player.getZ()).append(" flag=").append(player.getPvpFlag()).append('\n');Thread.sleep(100);}
   Files.writeString(p.resolve("instance-timeline.txt"),b);
  }finally {inst.redefineClasses(new ClassDefinition(WorldObject.class,original));Files.writeString(p.resolve("instance-trace-restored.txt"),"Original WorldObject bytecode restored; no trace installed in runtime JAR.\n");}
 }
}
