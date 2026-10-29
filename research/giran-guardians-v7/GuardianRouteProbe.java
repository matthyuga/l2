import java.io.File;import org.l2jmobius.gameserver.config.*;import org.l2jmobius.gameserver.geoengine.*;import org.l2jmobius.gameserver.geoengine.pathfinding.*;
public class GuardianRouteProbe {
 public static void main(String[] args){ServerConfig.DATAPACK_ROOT=new File(".");GeoEngineConfig.load();GeoEngineConfig.MAX_POSTFILTER_PASSES=0;var geo=GeoEngine.getInstance();var paths=PathFinding.getInstance();
  int[][] ares={{114174,145058,-2648},{113250,145095,-2832},{114000,145095,-2648},{114650,145095,-2648},{114000,145095,-2648},{114174,145058,-2648}};
  int[][] nyx={{117400,145064,-2640},{116650,145095,-2560},{117400,145064,-2640},{117544,145064,-2640},{117608,145064,-2592},{117704,145064,-2528},{117880,145064,-2528},{117704,145064,-2528},{117608,145064,-2592},{117544,145064,-2640},{117400,145064,-2640}};
  for(int[][] route:new int[][][]{ares,nyx,new int[][]{{116540,146655,-1866},{115700,145095,-2560},{117400,145064,-2640}}})for(int i=0;i<route.length-1;i++){int[] a=route[i],b=route[i+1];int z=geo.getNearestZ(GeoEngine.getGeoX(a[0]),GeoEngine.getGeoY(a[1]),a[2]),tz=geo.getNearestZ(GeoEngine.getGeoX(b[0]),GeoEngine.getGeoY(b[1]),b[2]);var path=paths.findPath(a[0],a[1],z,b[0],b[1],tz,0,true);System.out.println(java.util.Arrays.toString(a)+" -> "+java.util.Arrays.toString(b)+" z="+z+"/"+tz+" path="+(path==null?"NONE":path.size()));}
 }
}
