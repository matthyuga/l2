package custom.ElvenPvpRoom;
import java.util.*;
import org.l2jmobius.gameserver.entity.Location;
/** Verified spawn sectors also serve as optional route portals; each connecting leg is planned. */
public final class RoomRouteNetwork {
 private RoomRouteNetwork(){}
 public static List<Location> plan(Location start,Location goal,PvpRoomConfig.ArenaMap map,int instance){
  List<Location> direct=RoomRoutePlanner.plan(start,goal,map,instance);if(!direct.isEmpty())return direct;
  List<Location> portals=new ArrayList<>(map.spawns());portals.sort(Comparator.comparingDouble(p->Math.hypot(p.getX()-start.getX(),p.getY()-start.getY())));
  for(Location portal:portals){
   if(Math.hypot(portal.getX()-start.getX(),portal.getY()-start.getY())<80||Math.hypot(portal.getX()-goal.getX(),portal.getY()-goal.getY())<80)continue;
   List<Location> first=RoomRoutePlanner.plan(start,portal,map,instance);if(first.isEmpty())continue;
   List<Location> second=RoomRoutePlanner.plan(portal,goal,map,instance);if(second.isEmpty())continue;
   List<Location> result=new ArrayList<>(first);result.addAll(second);return List.copyOf(result);
  }
  return List.of();
 }
}
