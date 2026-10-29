import java.io.File;import java.util.*;import org.l2jmobius.gameserver.config.*;import org.l2jmobius.gameserver.geoengine.*;
public class RoomPathProbe {
 record Cell(int x,int y,int z){}
 public static void main(String[] args){ServerConfig.DATAPACK_ROOT=new File(".");GeoEngineConfig.load();var geo=GeoEngine.getInstance();
  int sx=GeoEngine.getGeoX(116540),sy=GeoEngine.getGeoY(146655);Cell start=new Cell(sx,sy,geo.getNearestZ(sx,sy,-1866));Map<Cell,Cell> prev=new HashMap<>();ArrayDeque<Cell> q=new ArrayDeque<>();q.add(start);prev.put(start,start);Cell end=null;
  while(!q.isEmpty()){Cell c=q.remove();int wx=geo.getWorldX(c.x),wy=geo.getWorldY(c.y);if(Math.hypot(wx-116650,wy-145095)<80&&Math.abs(c.z+2560)<80){end=c;break;}for(int[] d:new int[][]{{1,0,1},{-1,0,2},{0,1,4},{0,-1,8}}){int x=c.x+d[0],y=c.y+d[1];if(geo.getWorldX(x)<115300||geo.getWorldX(x)>119200||geo.getWorldY(y)<143000||geo.getWorldY(y)>147500||!geo.checkNearestNswe(c.x,c.y,c.z,d[2]))continue;for(int z:new int[]{geo.getNearestZ(x,y,c.z),geo.getNextHigherZ(x,y,c.z+1)}){if(z-c.z>40||c.z-z>300||z<-2900||z>-1500)continue;Cell n=new Cell(x,y,z);if(!prev.containsKey(n)){prev.put(n,c);q.add(n);}}}}
  System.out.println("ROOM BFS visited="+prev.size()+" end="+end);if(end!=null){List<Cell> p=new ArrayList<>();for(Cell c=end;!c.equals(start);c=prev.get(c))p.add(c);p.add(start);Collections.reverse(p);int lastdx=0,lastdy=0,lastz=start.z;for(int i=0;i<p.size();i++){Cell c=p.get(i);int dx=i+1<p.size()?p.get(i+1).x-c.x:0,dy=i+1<p.size()?p.get(i+1).y-c.y:0;if(i==0||i==p.size()-1||dx!=lastdx||dy!=lastdy||Math.abs(c.z-lastz)>40){System.out.println(geo.getWorldX(c.x)+","+geo.getWorldY(c.y)+","+c.z);lastz=c.z;}lastdx=dx;lastdy=dy;}}
 }
}
