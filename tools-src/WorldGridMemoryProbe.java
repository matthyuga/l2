import java.lang.instrument.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.WorldRegion;
public class WorldGridMemoryProbe {
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  i.redefineModule(Object.class.getModule(),Set.of(),Map.of(),Map.of("java.util.concurrent",Set.of(WorldGridMemoryProbe.class.getModule())),Set.of(),Map.of());
  Field all=World.class.getDeclaredField("_worldRegions");all.setAccessible(true);WorldRegion[][][] grid=(WorldRegion[][][])all.get(null);
  Field visible=field("_visibleObjects"),doors=field("_doors"),fences=field("_fences"),cache=field("_surroundingRegionCache"),near=field("_surroundingRegions"),active=field("_activeNeighbors");
  Field map=ConcurrentHashMap.newKeySet().getClass().getSuperclass().getDeclaredField("map");map.setAccessible(true);
  long[] sizes=new long[6];sizes[0]=i.getObjectSize(grid);long total=0,occupied=0,nonemptyCache=0;
  for(WorldRegion[][] plane:grid){sizes[0]+=i.getObjectSize(plane);for(WorldRegion[] column:plane){sizes[0]+=i.getObjectSize(column);for(WorldRegion region:column){if(region==null)continue;total++;sizes[1]+=i.getObjectSize(region);boolean used=false;
   for(Field f:List.of(visible,doors,fences)){Collection<?> set=(Collection<?>)f.get(region);used|=!set.isEmpty();sizes[2]+=i.getObjectSize(set);sizes[3]+=i.getObjectSize(map.get(set));}
   Map<?,?> neighbors=(Map<?,?>)cache.get(region);if(!neighbors.isEmpty())nonemptyCache++;sizes[3]+=i.getObjectSize(neighbors);sizes[4]+=i.getObjectSize(near.get(region));sizes[5]+=i.getObjectSize(active.get(region));if(used)occupied++;
  }}}
  String[] names={"world_matrix_arrays","region_objects","collection_views","map_headers","neighbor_arrays","neighbor_counters"};StringBuilder s=new StringBuilder("component,bytes\n");long sum=0;for(int n=0;n<sizes.length;n++){s.append(names[n]+","+sizes[n]+"\n");sum+=sizes[n];}s.append("total_structural_bytes,"+sum+"\nregions,"+total+"\nregions_with_objects_doors_or_fences,"+occupied+"\nregions_with_neighbor_cache_entries,"+nonemptyCache+"\n");Files.writeString(Path.of(dir,"world-grid-native.csv"),s.toString());
 }
 static Field field(String name)throws Exception{Field f=WorldRegion.class.getDeclaredField(name);f.setAccessible(true);return f;}
}
