import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.Location;
public class TestRoomRoutes {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory),folder=dir.resolve("compiled/custom/ElvenPvpRoom");Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();var lookup=MethodHandles.privateLookupIn(host.getClass(),MethodHandles.lookup());
  for(String name:List.of("RoomRoutePlanner","RoomRoutePlanner$Cell","RoomRoutePlanner$Open"))lookup.defineClass(Files.readAllBytes(folder.resolve(name+".class")));
  var field=host.getClass().getDeclaredField("config");field.setAccessible(true);Object config=field.get(host);Map<?,?> maps=(Map<?,?>)config.getClass().getField("maps").get(config);Object map=maps.get("elven");Class<?> planner=loader.loadClass("custom.ElvenPvpRoom.RoomRoutePlanner");
  var method=planner.getMethod("plan",Location.class,Location.class,map.getClass(),int.class);StringBuilder log=new StringBuilder();
  Location[] points={new Location(45150,52100,-2792),new Location(43673,49683,-3048),new Location(47401,51764,-2992),new Location(45443,48357,-3056)};
  for(int i=0;i<points.length;i++)for(int j=0;j<points.length;j++)if(i!=j){long begin=System.nanoTime();List<Location> route=(List<Location>)method.invoke(null,points[i],points[j],map,0);
   log.append(i).append(" -> ").append(j).append(" nodes=").append(route.size()).append(" ms=").append((System.nanoTime()-begin)/1000000).append('\n');for(Location p:route)log.append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append(';');log.append('\n');
  }
  Files.writeString(dir.resolve("fixed-routes.txt"),log);
 }
}
