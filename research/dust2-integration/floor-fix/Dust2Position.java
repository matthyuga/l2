import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
public class Dust2Position {
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  StringBuilder b=new StringBuilder();
  for(var p:World.getPlayers())if(p.getClient()!=null)b.append(p.getName()+" server="+p.getX()+","+p.getY()+","+p.getZ()+" client="+p.getClientX()+","+p.getClientY()+","+p.getClientZ()+" instance="+p.getInstanceId()+" floor_current="+GeoEngine.getInstance().getHeight(p.getX(),p.getY(),p.getZ())+" floor_arena="+GeoEngine.getInstance().getHeight(p.getX(),p.getY(),8200)+" teleport="+p.isTeleporting()+"\n");
  Files.writeString(Path.of(dir,"position.txt"),b);
 }
}
