import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.BypassHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.network.serverpackets.SkillCatalogView;
public final class ProbeStickerDeliveryV4 {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception{
  List<String> report=new ArrayList<>();
  if(!SkillCatalogView.nativeWindowAction("voice .sticker 1"))throw new AssertionError("Native action not allowed");
  var bypass=BypassHandler.getInstance().getHandler("voice .sticker 1");
  if(bypass==null)throw new AssertionError("Voice bypass handler missing");
  report.add("native_action_allowed=true; bypass_handler="+bypass.getClass().getName());
  var p=World.getPlayers().stream().filter(x->x.getClient()!=null&&x.isOnline()&&x.getName().equals("Hellkevin")).findFirst().orElse(null);
  if(p==null){report.add("SKIPPED: intended player is not online; no emission.");}
  else{
   var handler=VoicedCommandHandler.getInstance().getHandler("sticker");var f=handler.getClass().getDeclaredField("lastUse");f.setAccessible(true);var times=(Map<?,?>)f.get(handler);
   if(times.containsKey(p.getObjectId()))report.add("SKIPPED: a user-triggered sticker cooldown is already active.");
   else{
    report.add("player_id="+p.getObjectId()+" spawned="+p.isSpawned()+" dead="+p.isDead()+" teleport="+p.isTeleporting()+" observer="+p.inObserverMode()+" invisible="+p.isInvisible());
    boolean result=bypass.onCommand("voice .sticker 1",p,null);
    report.add("bypass_result="+result+" accepted_cooldown_reserved="+times.containsKey(p.getObjectId()));
    report.add("LIMIT: server delivery path executed; actual drawing must be observed by user.");
   }
  }
  Files.write(Path.of(directory,"delivery-probe.txt"),report);
 }
}
