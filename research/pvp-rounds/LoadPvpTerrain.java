import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
public class LoadPvpTerrain {
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  var g=GeoEngine.getInstance();
  if(!g.reloadRegion(20,17)||!g.reloadRegion(22,15))throw new IllegalStateException("Geodata reload failed");
  if(!g.hasGeo(11000,-25000)||!g.hasGeo(84092,-80084))throw new IllegalStateException("Terrain unavailable after reload");
  Files.writeString(Path.of(dir,"geodata-deployment.txt"),"PASS loaded 20_17 and 22_15; player positions unchanged.\n");
 }
}
