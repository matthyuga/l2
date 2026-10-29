import java.lang.instrument.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.WorldRegion;
public class LazyRegionGridProbe {
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  i.redefineModule(Object.class.getModule(),Set.of(),Map.of(),Map.of("java.util.concurrent",Set.of(LazyRegionGridProbe.class.getModule())),Set.of(),Map.of());
  Field all=World.class.getDeclaredField("_worldRegions");all.setAccessible(true);WorldRegion[][][] grid=(WorldRegion[][][])all.get(null);
  Field[] sets={field("_visibleObjects"),field("_doors"),field("_fences")};
  Field cache=null;try{cache=field("_surroundingRegionCache");}catch(NoSuchFieldException expected){}
  Field near=field("_surroundingRegions"),active=field("_activeNeighbors");
  Field map=ConcurrentHashMap.newKeySet().getClass().getSuperclass().getDeclaredField("map");map.setAccessible(true);
  long[] sizes=new long[6],allocated=new long[3];sizes[0]=i.getObjectSize(grid);long total=0,occupied=0;
  for(WorldRegion[][] plane:grid){sizes[0]+=i.getObjectSize(plane);for(WorldRegion[] column:plane){sizes[0]+=i.getObjectSize(column);for(WorldRegion region:column){if(region==null)continue;total++;sizes[1]+=i.getObjectSize(region);boolean used=false;
   for(int n=0;n<sets.length;n++){Collection<?> set=(Collection<?>)sets[n].get(region);if(set!=null){allocated[n]++;used|=!set.isEmpty();sizes[2]+=i.getObjectSize(set);sizes[3]+=i.getObjectSize(map.get(set));}}
   if(cache!=null)sizes[3]+=i.getObjectSize(cache.get(region));sizes[4]+=i.getObjectSize(near.get(region));sizes[5]+=i.getObjectSize(active.get(region));if(used)occupied++;
  }}}
  String[] names={"world_matrix_arrays","region_objects","collection_views","map_headers","neighbor_arrays","neighbor_counters"};StringBuilder s=new StringBuilder("component,bytes\n");long sum=0;for(int n=0;n<sizes.length;n++){s.append(names[n]+","+sizes[n]+"\n");sum+=sizes[n];}
  s.append("total_structural_bytes,"+sum+"\nregions,"+total+"\nregions_with_objects_doors_or_fences,"+occupied+"\n");
  for(int n=0;n<sets.length;n++)s.append("allocated"+sets[n].getName()+","+allocated[n]+"\n");
  Files.writeString(Path.of(dir,"world-grid-native.csv"),s.toString());
 }
 static Field field(String name)throws Exception{Field f=WorldRegion.class.getDeclaredField(name);f.setAccessible(true);return f;}
}
