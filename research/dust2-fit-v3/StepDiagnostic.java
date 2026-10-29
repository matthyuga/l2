import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.data.xml.DoorData;
import org.l2jmobius.gameserver.data.xml.FenceData;
public class StepDiagnostic {
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  var g=GeoEngine.getInstance();int x=141384,y=55336,z=8072,tx=141384,ty=55320,tz=8080;
  int gx=g.getGeoX(x),gy=g.getGeoY(y),tgx=g.getGeoX(tx),tgy=g.getGeoY(ty);
  String s="start="+g.getHeight(x,y,z)+" end="+g.getHeight(tx,ty,tz)+" end_from_start="+g.getHeight(tx,ty,z)+" nswe="+g.checkNearestNsweAntiCornerCut(gx,gy,z,8)+" door="+DoorData.getInstance().checkIfDoorsBetween(x,y,z,tx,ty,tz,0,false)+" fence="+FenceData.getInstance().checkIfFenceBetween(x,y,z,tx,ty,tz,0)+" move="+g.canMoveToTarget(x,y,z,tx,ty,tz,0);
  Files.writeString(Path.of(dir,"step-diagnostic.txt"),s);
 }
}
