package custom.ElvenPvpRoom;
import java.util.*;
import java.nio.file.*;
import java.io.*;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.geoengine.GeoEngine;

public final class PvpRoomConfig {
 public record ArenaMap(String id,String name,int minX,int maxX,int minY,int maxY,int minZ,int maxZ,List<Location> spawns){
  public boolean inside(Location p){return p.getX()>minX&&p.getX()<maxX&&p.getY()>minY&&p.getY()<maxY&&p.getZ()>minZ&&p.getZ()<maxZ;}
  public Location safe(Location p){
   if(p!=null&&inside(p)){
    int floor=GeoEngine.getInstance().getHeight(p.getX(),p.getY(),p.getZ());
    if(GeoEngine.getInstance().hasGeo(p.getX(),p.getY())&&Math.abs(floor-p.getZ())<100 && floor>minZ && floor<maxZ)return new Location(p.getX(),p.getY(),floor,p.getHeading());
   }
   Location first=spawns.get(0);return new Location(first.getX(),first.getY(),first.getZ(),first.getHeading());
  }
 }
 public final Map<String,ArenaMap> maps;
 public final long roundNanos,voteLeadNanos,voteNanos;
 public final boolean friendlyFire;
 public PvpRoomConfig(Path path)throws IOException{
  Properties p=new Properties();try(var reader=Files.newBufferedReader(path)){p.load(reader);}
  roundNanos=seconds(p,"RoundSeconds");voteLeadNanos=seconds(p,"VoteLeadSeconds");voteNanos=seconds(p,"VoteSeconds");
  if(voteNanos<=0||voteLeadNanos<voteNanos||roundNanos<=voteLeadNanos)throw new IllegalArgumentException("Invalid round/vote times");
  friendlyFire=Boolean.parseBoolean(p.getProperty("FriendlyFire","false"));
  Map<String,ArenaMap> loaded=new LinkedHashMap<>();
  for(String id:p.getProperty("Maps").split(",")){
   if(!id.matches("[a-z0-9_]+")||loaded.containsKey(id))throw new IllegalArgumentException("Invalid map id");
   int[] b=ints(p.getProperty(id+".Bounds"));if(b.length!=6||b[0]>=b[1]||b[2]>=b[3]||b[4]>=b[5])throw new IllegalArgumentException("Invalid perimeter "+id);
   List<Location> spawn=new ArrayList<>();
   for(String line:p.getProperty(id+".Spawns").split(";")){int[] xyz=ints(line);if(xyz.length!=3)throw new IllegalArgumentException("Invalid spawn");spawn.add(new Location(xyz[0],xyz[1],xyz[2]));}
   if(spawn.size()<4)throw new IllegalArgumentException("Four spawns required");
   ArenaMap map=new ArenaMap(id,p.getProperty(id+".Name"),b[0],b[1],b[2],b[3],b[4],b[5],List.copyOf(spawn));
   for(Location loc:spawn){var geo=GeoEngine.getInstance();if(!map.inside(loc)||!geo.hasGeo(loc.getX(),loc.getY())||Math.abs(geo.getHeight(loc.getX(),loc.getY(),loc.getZ())-loc.getZ())>80)throw new IllegalArgumentException("Unverified spawn "+id);}
   loaded.put(id,map);
  }
  if(!loaded.containsKey("elven"))throw new IllegalArgumentException("Elven required");
  maps=Collections.unmodifiableMap(loaded);
 }
 private static int[] ints(String line){return Arrays.stream(line.split(",")).map(String::trim).mapToInt(Integer::parseInt).toArray();}
 private static long seconds(Properties p,String key){return Math.multiplyExact(Long.parseLong(p.getProperty(key)),1_000_000_000L);}
}
