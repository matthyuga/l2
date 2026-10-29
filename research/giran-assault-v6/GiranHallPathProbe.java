import java.io.File;
import org.l2jmobius.gameserver.config.*;
import org.l2jmobius.gameserver.geoengine.*;
import org.l2jmobius.gameserver.geoengine.pathfinding.*;
/** Read-only native paths, without DB, characters or sockets. */
public class GiranHallPathProbe {
 public static void main(String[] args){ServerConfig.DATAPACK_ROOT=new File(".");GeoEngineConfig.load();if(args.length>0)GeoEngineConfig.GEODATA_PATH=java.nio.file.Path.of(args[0]);GeoEngineConfig.MAX_POSTFILTER_PASSES=0;var geo=GeoEngine.getInstance();var paths=PathFinding.getInstance();
  int[][] points={{113250,144790,-2832},{114650,145095,-2752},{115200,145035,-2560},{115700,145035,-2560},{116300,145095,-2720},{116650,145095,-2560},{117250,145095,-2560},{117902,145096,-2544}};
  for(int i=0;i<points.length-1;i++){int[] a=points[i],b=points[i+1];probe(geo,paths,a,b);}
  for(int[] a:new int[][]{{113250,144790,-2832},{115700,145035,-2560},{116650,145095,-2560},{116300,145095,-2720}})for(int[] b:new int[][]{{114650,145095,-2752},{116300,145300,-2720},{116650,145400,-2560},{117250,145300,-2560},{117902,145096,-2544}})probe(geo,paths,a,b);
  for(int[] a:new int[][]{{116650,145095,-2560},{117450,145500,-2640},{117450,144700,-2640},{117550,145096,-2640}})for(int[] b:new int[][]{{117450,145500,-2640},{117450,144700,-2640},{117550,145096,-2640},{117902,145096,-2544}})probe(geo,paths,a,b);
  for(int radius:new int[]{48,32,64,0})for(int i=0;i<8;i++){int x=117950+(int)(Math.cos(i*Math.PI/4)*radius),y=145096+(int)(Math.sin(i*Math.PI/4)*radius);probe(geo,paths,new int[]{117550,145096,-2640},new int[]{x,y,-2544});}
  int[][] stairs={{116650,145095,-2560},{117450,144700,-2640},{117530,145096,-2640},{117610,145096,-2608},{117706,145096,-2544},{117818,145096,-2512},{117950,145096,-2544}};
  for(int i=0;i<stairs.length-1;i++)probe(geo,paths,stairs[i],stairs[i+1]);
  for(int[] a:new int[][]{{117706,145096,-2544},{117818,145096,-2512},{117870,145048,-2520},{117902,145048,-2536}})for(int[] b:new int[][]{{117870,145048,-2520},{117902,145048,-2536},{117918,145064,-2544},{117950,145096,-2544}})probe(geo,paths,a,b);
  for(int[] a:new int[][]{{117706,145096,-2544},{117706,145064,-2528},{117774,145032,-2488},{117854,145032,-2488}})for(int[] b:new int[][]{{117706,145064,-2528},{117774,145032,-2488},{117854,145032,-2488},{117870,145048,-2520}})probe(geo,paths,a,b);
  for(int y=145016;y<=145176;y+=16){StringBuilder line=new StringBuilder("STAIR y="+y);for(int x=117550;x<=118046;x+=16){int z=geo.getHeight(x,y,-2544);line.append(" ").append(x).append(":").append(z).append("/").append(geo.checkNearestNswe(GeoEngine.getGeoX(x),GeoEngine.getGeoY(y),z,15)?"o":"b");}System.out.println(line);}
  for(int y=144600;y<=145600;y+=100){StringBuilder line=new StringBuilder("FLOOR y="+y);for(int x=115700;x<=118000;x+=100)line.append(" ").append(x).append(":").append(geo.getHeight(x,y,-2560));System.out.println(line);}
 }
 static void probe(GeoEngine geo,PathFinding paths,int[] a,int[] b){int z=geo.getHeight(a[0],a[1],a[2]),tz=geo.getHeight(b[0],b[1],b[2]);var p=paths.findPath(a[0],a[1],z,b[0],b[1],tz,0,true);System.out.println(java.util.Arrays.toString(a)+" -> "+java.util.Arrays.toString(b)+" z="+z+"/"+tz+" path="+(p==null?"NONE":p.size()));}
}
