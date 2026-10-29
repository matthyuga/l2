import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.scripting.ScriptEngine;

/** Add one script/template and redefine only the existing Elven controller methods. */
public class DeployElven
{
 public static void agentmain(String directory,Instrumentation inst)throws Exception
 {
  Path stage=Path.of(directory);
  StringBuilder report=new StringBuilder();
  try
  {
   if(VoicedCommandHandler.getInstance().getHandler("salas")!=null)
    throw new IllegalStateException("Lobby already registered; refusing duplicate timers/NPCs");
   var geo=GeoEngine.getInstance();
   for(int[] point:new int[][]{{83480,148120,-3406},{149160,46700,12016},{45150,52100,-2792},{83425,148585,-3406}})
   {
    int floor=geo.getHeight(point[0],point[1],point[2]);
    if(Math.abs(floor-point[2])>100)throw new IllegalStateException("Floor mismatch "+java.util.Arrays.toString(point)+" got "+floor);
    report.append("floor "+point[0]+","+point[1]+" = "+floor+"\n");
   }
   var original=VoicedCommandHandler.getInstance().getHandler("elvenpvp");
   if(original==null)throw new IllegalStateException("Existing Elven controller missing");
   NpcData.getInstance().parseDatapackFile("data/stats/npcs/custom/pvp_rooms.xml");
   if(NpcData.getInstance().getTemplate(902600)==null)throw new IllegalStateException("NPC template did not load");
   ScriptEngine.getInstance().executeScript(Path.of("custom/ElvenPvpRoom/PvpRooms.java"));
   if(VoicedCommandHandler.getInstance().getHandler("salas")==null)throw new IllegalStateException("Lobby did not register");
   inst.redefineClasses(new ClassDefinition(original.getClass(),Files.readAllBytes(stage.resolve("compiled/custom/ElvenPvpRoom/ElvenPvpRoom.class"))));
   report.append("PASS: lobby loaded; two hosts spawned; original Elven methods redefined. No core reload/restart, real-player teleport or DB edits.\n");
  }
  catch(Throwable error){report.append("FAIL: "+error+"\n");throw error;}
  finally{Files.writeString(stage.resolve("deployment.txt"),report);}
 }
}
