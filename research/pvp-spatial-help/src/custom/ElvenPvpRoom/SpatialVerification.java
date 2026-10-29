package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
public final class SpatialVerification {
 public static void run(Path directory)throws Exception{
  PvpRoomConfig config=new PvpRoomConfig(Path.of("config/Custom/PvpRooms.properties"));
  var template=PlayerTemplateData.getInstance().getTemplate(0);
  var ctor=Player.class.getDeclaredConstructor(int.class,template.getClass(),String.class,PlayerAppearance.class);ctor.setAccessible(true);
  List<Player> scratch=new ArrayList<>();StringBuilder log=new StringBuilder();
  try{
   for(int i=0;i<12;i++){Player p=ctor.newInstance(-190000-i,template,"spatial-dry-check",new PlayerAppearance((byte)0,(byte)0,(byte)0,false));scratch.add(p);p.stopAllTimers();p.setOnlineStatus(true,false);p.setDead(false);}
   for(var map:config.maps.values())for(var mode:RoundState.Mode.values()){
    List<Player> placed=new ArrayList<>();Set<String> points=new HashSet<>();double min=Double.MAX_VALUE;
    for(Player actor:scratch){actor.setXYZInvisible(0,0,0);int team=mode.teams==0?0:1;Location point=RoomSpatialTactics.spawn(map,mode,team,actor,placed);
     if(!map.inside(point)||Math.abs(GeoEngine.getInstance().getHeight(point.getX(),point.getY(),point.getZ())-point.getZ())>5)throw new IllegalStateException("Invalid spawn "+map.id());
     for(Player other:placed)min=Math.min(min,Math.hypot(point.getX()-(double)other.getX(),point.getY()-(double)other.getY()));
     actor.setXYZInvisible(point.getX(),point.getY(),point.getZ());placed.add(actor);points.add(point.getX()+","+point.getY()+","+point.getZ());
    }
    if(points.size()!=12||min<60)throw new IllegalStateException("Spawn overlap "+map.id()+" "+mode+" unique="+points.size()+" clearance="+min);
    log.append("PASS ").append(map.id()).append(' ').append(mode).append(":12 distinct native-geodata spawns, minimum clearance=").append((int)min).append('\n');
   }
   for(boolean gm:new boolean[]{false,true})for(String page:new String[]{"","salas","bots","retirar","duelos","grupos","asedio","personaje","viajes"}){
    String html=RoomCommandHelp.render(gm,page);if(html.length()>8000||!html.endsWith("</html>"))throw new IllegalStateException("Invalid help page "+page);
    if(!gm&&html.contains("usar 8\""))throw new IllegalStateException("GM action exposed");
   }
   log.append("PASS 18 bounded HTML pages; permission-filtered catalogue. Scratch players never spawned, saved or registered.\n");
   Files.writeString(directory.resolve("spatial-tests.txt"),log);
  }finally{for(Player p:scratch){p.stopAllTimers();p.setOnlineStatus(false,false);}}
 }
}
