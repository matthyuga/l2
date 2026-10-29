import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

public final class InspectStickerState {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  List<String> rows=new ArrayList<>();var h=VoicedCommandHandler.getInstance().getHandler("sticker");
  rows.add("handler="+(h==null?"null":h.getClass().getName()));
  for(var p:World.getPlayers())if(p.getClient()!=null)rows.add("player="+p.getName()+" online="+p.isOnline()+" spawned="+p.isSpawned()+" dead="+p.isDead()+" teleport="+p.isTeleporting()+" observer="+p.inObserverMode()+" invisible="+p.isInvisible());
  Files.write(Path.of(directory,"player-state.txt"),rows);
 }
}
