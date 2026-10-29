import java.io.File;
import org.l2jmobius.gameserver.config.*;
import org.l2jmobius.gameserver.geoengine.*;
import org.l2jmobius.gameserver.geoengine.pathfinding.*;
/** Read-only native terrain/path probe; no server, DB, sockets or player loads. */
public class GiranCampPathProbe {
 public static void main(String[] args){ServerConfig.DATAPACK_ROOT=new File(".");GeoEngineConfig.load();GeoEngineConfig.MAX_POSTFILTER_PASSES=0;var geo=GeoEngine.getInstance();var paths=PathFinding.getInstance();
  for(int[] q:new int[][]{{111700,147500,111400,145350},{111800,147400,111400,145350},{111400,147100,111400,145350},{109600,146100,111400,145350},{110000,142000,111400,144400},{110000,146200,111400,145350},{111200,144100,112400,144790}}){int z=geo.getHeight(q[0],q[1],-2832),tz=geo.getHeight(q[2],q[3],-2832);var p=paths.findPath(q[0],q[1],z,q[2],q[3],tz,0,true);System.out.println(java.util.Arrays.toString(q)+" z="+z+"/"+tz+" open="+geo.checkNearestNswe(GeoEngine.getGeoX(q[0]),GeoEngine.getGeoY(q[1]),z,15)+" path="+(p==null?"NONE":p.size()));}
 }
}
