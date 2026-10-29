import java.io.File;import java.util.*;
import org.l2jmobius.gameserver.config.*;import org.l2jmobius.gameserver.geoengine.*;
public class GiranStairProbe{
 record Cell(int x,int y,int z){}
 public static void main(String[] args){ServerConfig.DATAPACK_ROOT=new File(".");GeoEngineConfig.load();if(args.length>0)GeoEngineConfig.GEODATA_PATH=java.nio.file.Path.of(args[0]);var geo=GeoEngine.getInstance();int sx=GeoEngine.getGeoX(116650),sy=GeoEngine.getGeoY(145096);Cell start=new Cell(sx,sy,geo.getNearestZ(sx,sy,-2560));Map<Cell,Cell> prev=new HashMap<>();ArrayDeque<Cell> q=new ArrayDeque<>();q.add(start);prev.put(start,start);Cell end=null;
  while(!q.isEmpty()){Cell c=q.remove();int wx=geo.getWorldX(c.x),wy=geo.getWorldY(c.y);if(Math.hypot(wx-117950,wy-145096)<=80&&c.z>=-2544&&c.z<=-2499){end=c;break;}for(int[] d:new int[][]{{1,0,1},{-1,0,2},{0,1,4},{0,-1,8}}){int x=c.x+d[0],y=c.y+d[1];if(geo.getWorldX(x)<116400||geo.getWorldX(x)>119300||geo.getWorldY(y)<143400||geo.getWorldY(y)>146800||!geo.checkNearestNswe(c.x,c.y,c.z,d[2]))continue;for(int z:new int[]{geo.getNearestZ(x,y,c.z),geo.getNextHigherZ(x,y,c.z+1)}){if(z-c.z>40||c.z-z>300)continue;Cell n=new Cell(x,y,z);if(!prev.containsKey(n)){prev.put(n,c);q.add(n);}}}}
  System.out.println("STEPS BFS visited="+prev.size()+" end="+end);if(end!=null){List<Cell> path=new ArrayList<>();for(Cell c=end;!c.equals(start);c=prev.get(c))path.add(c);path.add(start);Collections.reverse(path);for(Cell c:path)System.out.println(geo.getWorldX(c.x)+","+geo.getWorldY(c.y)+","+c.z);}
 }
}
