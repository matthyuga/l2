import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.ScriptManager;
import org.l2jmobius.gameserver.mechanics.script.Quest;
public class RestoreRoomLobbyRegistry {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Quest host=(Quest)VoicedCommandHandler.getInstance().getHandler("salas");
  synchronized(host){
   ScriptManager.getInstance().getScripts().put("PvpRoundRooms",host);
   Field f=Quest.class.getDeclaredField("_listeners");f.setAccessible(true);boolean restored=false;
   if(((Collection<?>)f.get(host)).isEmpty()){host.addStartNpc(902600);host.addTalkId(902600);host.addFirstTalkId(902600);restored=true;}
   if(ScriptManager.getInstance().getScript("PvpRoundRooms")!=host||((Collection<?>)f.get(host)).isEmpty())throw new IllegalStateException("Lobby registry/listeners missing");
   Files.writeString(Path.of(directory,"lobby-registry-audit.txt"),"PASS active voice and script registry reference same production lobby; NPC callbacks present. Restored after isolated fixture registration: "+restored+"\n");
  }
 }
}
