import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
public class L2EntryStatusProbe {
 public static void agentmain(String dir,Instrumentation unused)throws Exception{
  long clients=0,spawned=0,registered=0;
  for(var p:World.getPlayers())if(p.getClient()!=null){clients++;if(p.isSpawned())spawned++;if(p.getWorldRegion()!=null&&p.getWorldRegion().getVisibleObjects().contains(p))registered++;}
  Files.writeString(Path.of(dir,"client-entry-status.txt"),"utc="+java.time.Instant.now()+"\nplayers_with_client="+clients+"\nspawned_players_with_client="+spawned+"\nplayers_in_region_collection="+registered+"\n");
 }
}
