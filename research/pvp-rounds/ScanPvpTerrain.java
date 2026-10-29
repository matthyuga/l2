import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
public class ScanPvpTerrain {
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  var g=GeoEngine.getInstance();StringBuilder b=new StringBuilder("map,x,y,z,east,south\n");
  int[][] areas={{6000,18000,-30000,-16000,-3600},{74000,90000,-88000,-72000,-3500}};
  for(int a=0;a<areas.length;a++){int[] r=areas[a];
   for(int x=r[0];x<=r[1];x+=256)for(int y=r[2];y<=r[3];y+=256){
    int z=g.getHeight(x,y,r[4]);boolean east=g.canMoveToTarget(x,y,z,x+256,y,g.getHeight(x+256,y,z),0);
    boolean south=g.canMoveToTarget(x,y,z,x,y+256,g.getHeight(x,y+256,z),0);
    if(g.hasGeo(x,y))b.append(a==0?"primeval":"saints").append(',').append(x).append(',').append(y).append(',').append(z).append(',').append(east?1:0).append(',').append(south?1:0).append('\n');
   }
  }
  Files.writeString(Path.of(dir,"terrain.csv"),b);
 }
}
