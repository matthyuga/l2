import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.scripting.ScriptEngine;
import org.l2jmobius.gameserver.managers.ScriptManager;
public class LoadElvenFlag
{
 public static void agentmain(String directory,Instrumentation ignored)throws Exception
 {
  if(ScriptManager.getInstance().getScript("PvpFlaggingStopTask")==null)
   ScriptEngine.getInstance().executeScript(Path.of("custom/ElvenPvpRoom/PvpFlaggingStopTask.java"));
  if(ScriptManager.getInstance().getScript("PvpFlaggingStopTask")==null)throw new IllegalStateException("Missing native flag task");
  if(ScriptManager.getInstance().getScript("PvpRooms")==null)throw new IllegalStateException("Lobby quest not registered");
  Files.writeString(Path.of(directory,"flag-task.txt"),"PASS: native PvP flag task registered in isolated Elven folder; lobby Quest registered for NPC bypass. No core changes.\n");
 }
}
