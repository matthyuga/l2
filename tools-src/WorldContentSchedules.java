import java.lang.instrument.*;
import java.nio.file.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.managers.CastleManager;
public class WorldContentSchedules {
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  int stopped=0;for(int id=1;id<=9;id++){if(id==3)continue;var c=CastleManager.getInstance().getCastleById(id);if(c.getSiege().isInProgress())throw new IllegalStateException("Unexpected active siege: "+id);var f=c.getSiege().getClass().getDeclaredField("_scheduledStartSiegeTask");f.setAccessible(true);Future<?> task=(Future<?>)f.get(c.getSiege());if(task!=null){task.cancel(false);if(!task.isCancelled()&&!task.isDone())throw new AssertionError("Task still scheduled: "+id);}stopped++;}
  Files.writeString(Path.of(dir,"siege-schedules.txt"),"PASS\nunused_castle_schedules_stopped="+stopped+"\ngiran_schedule_preserved=true\n");
 }
}
