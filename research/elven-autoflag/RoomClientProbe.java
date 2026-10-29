import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class RoomClientProbe {
 public static void agentmain(String args,Instrumentation inst)throws Exception {
  String[] a=args.split("\\|",2);Path dir=Path.of(a[0]);String action=a[1];
  var p=World.getPlayer(268473899);
  if(p==null || !p.getName().equals("Hellkevin") || p.getClient()==null || !p.isOnline())throw new IllegalStateException("Intended connected player unavailable");
  if(!action.equals("entrar") && !action.equals("salir") && !action.equals("estado"))throw new IllegalArgumentException("Unknown probe action");
  String before="instance="+p.getInstanceId()+" flag="+p.getPvpFlag()+" xyz="+p.getX()+","+p.getY()+","+p.getZ();
  if(!action.equals("estado"))VoicedCommandHandler.getInstance().getHandler("salas").onCommand("salas",p,action);
  String after="instance="+p.getInstanceId()+" flag="+p.getPvpFlag()+" xyz="+p.getX()+","+p.getY()+","+p.getZ()+" dead="+p.isDead()+" teleporting="+p.isTeleporting();
  Files.writeString(dir.resolve("client-"+action+"-state.txt"),"Before: "+before+"\nAfter: "+after+"\n");
 }
}
