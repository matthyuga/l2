package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.managers.InstanceManager;
/** Actual native walking in an isolated empty instance. No actor is teleported after the initial placement. */
public final class NativeNavigationTrial {
 public static void run(Path directory)throws Exception{
  PvpRoomConfig config=new PvpRoomConfig(Path.of("config/Custom/PvpRooms.properties"));var map=config.maps.get("elven");
  List<Player> actors=new ArrayList<>();var instance=InstanceManager.getInstance().createDynamicInstance(0);StringBuilder log=new StringBuilder();
  Location[] starts={map.spawns().get(1),map.spawns().get(0)},goals={map.spawns().get(0),map.spawns().get(1)};boolean[] arrived={false,false};
  try{
   for(int i=0;i<2;i++){Player p=PvpSiegeRoster.acquire();actors.add(p);p.teleToLocation(starts[i],instance.getId(),0);p.onTeleported();p.setTeleportProtection(false);p.setSpawnProtection(false);p.setRunning();log.append("START ").append(p.getName()).append(' ').append(p.getLocation()).append(" goal=").append(goals[i]).append('\n');}
   long started=System.nanoTime(),last=0;
   while(System.nanoTime()-started<100_000_000_000L){
    for(int i=0;i<actors.size();i++)if(!arrived[i]){
     Player p=actors.get(i);arrived[i]=Math.hypot(p.getX()-goals[i].getX(),p.getY()-goals[i].getY())<60&&Math.abs(p.getZ()-goals[i].getZ())<64;
     if(arrived[i]){p.stopMove(null);log.append("ARRIVED ").append(p.getName()).append(" seconds=").append((System.nanoTime()-started)/1000000000).append(' ').append(p.getLocation()).append('\n');}
     else RoomNavigator.follow(p,goals[i],0,map);
    }
    if(System.nanoTime()-last>5_000_000_000L){last=System.nanoTime();for(Player p:actors)log.append("SAMPLE ").append(p.getName()).append(' ').append(p.getLocation()).append(' ').append(RoomNavigator.report(p)).append('\n');Files.writeString(directory.resolve("native-walk-progress.txt"),log);}
    if(arrived[0]&&arrived[1])break;Thread.sleep(250);
   }
   Files.writeString(directory.resolve("native-walk.txt"),log);
   if(!arrived[0]||!arrived[1])throw new IllegalStateException("Native staircase trial incomplete: "+Arrays.toString(arrived));
   Files.writeString(directory.resolve("native-walk-status.txt"),"PASS both reserved actors walked Elven lower -> upper and upper -> lower using persistent native waypoints; no teleport after initial placement.\n");
  }finally{
   for(Player p:actors){RoomNavigator.forget(p);PvpSiegeRoster.release(p);}InstanceManager.getInstance().destroyInstance(instance.getId());
   Files.writeString(directory.resolve("native-walk-cleanup.txt"),"Reserved trial actors retired; isolated instance destroyed.\n");
  }
 }
}
