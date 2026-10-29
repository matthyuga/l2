import java.lang.instrument.Instrumentation;
import java.lang.reflect.Field;
import java.nio.file.*;
import java.util.Map;
import org.l2jmobius.gameserver.config.custom.WorldContentConfig;
import org.l2jmobius.gameserver.managers.DimensionalRiftManager;
public class DisabledRiftRuntimeProbe {
 public static void agentmain(String dir,Instrumentation unused)throws Exception{
  if(!WorldContentConfig.CUSTOM_WORLD_ONLY)throw new AssertionError("Expected custom world");
  var r=DimensionalRiftManager.getInstance();
  for(int[] p:new int[][]{{83020,147880,-3469},{116650,145470,-2560},{148900,45500,-3408}}){
   if(r.checkIfInRiftZone(p[0],p[1],p[2],false)||r.checkIfInRiftZone(p[0],p[1],p[2],true)||r.checkIfInPeaceZone(p[0],p[1],p[2]))throw new AssertionError("Disabled Rift still active");
  }
  Field f=DimensionalRiftManager.class.getDeclaredField("_rooms");f.setAccessible(true);if(!((Map<?,?>)f.get(r)).isEmpty())throw new AssertionError("Classic rooms loaded");
  Files.writeString(Path.of(dir,"rift-runtime-verification.txt"),"PASS\nlogin_rift_query_safe=true\nclassic_rooms_not_loaded=true\ncustom_world_enabled=true\n");
 }
}
