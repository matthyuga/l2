import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
public final class InspectBehemoth {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  StringBuilder out=new StringBuilder();Player p=World.getPlayer("Hellkevin");
  if(p!=null)out.append("Player ").append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append(" geoZ=").append(GeoEngine.getInstance().getHeight(p.getX(),p.getY(),p.getZ())).append(" seated=").append(BehemothSeatSync.isSeated(p)).append(" movementDisabled=").append(p.isMovementDisabled()).append('\n');
  else out.append("Player offline\n");
  for(Class<?> c:inst.getAllLoadedClasses())if(c.getName().equals("custom.BehemothTransport.BehemothTransport")){var field=c.getDeclaredField("instance");field.setAccessible(true);Object module=field.get(null);if(module==null)continue;field=c.getDeclaredField("owned");field.setAccessible(true);synchronized(module){for(Object trip:((Map<?,?>)field.get(module)).values()){var f=trip.getClass().getDeclaredField("npc");f.setAccessible(true);Npc n=(Npc)f.get(trip);out.append("NPC id=").append(n.getId()).append(" xyz=").append(n.getX()).append(',').append(n.getY()).append(',').append(n.getZ()).append(" geoZ=").append(GeoEngine.getInstance().getHeight(n.getX(),n.getY(),n.getZ())).append(" height=").append(n.getTemplate().getFCollisionHeight()).append(" radius=").append(n.getTemplate().getFCollisionRadius()).append('\n');}}}
  Files.writeString(Path.of(directory,"live-height-inspection.txt"),out);
 }
}
