import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

/** Exercise the actual registered command using a transient, non-DB player. */
public class GludioTravelProbe {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  StringBuilder report=new StringBuilder();Player p=null;
  try {
   var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
   var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
   p=ctor.newInstance(template,"gludio-route-transient",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
   p.setName("GludioRouteProbe");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(83020,147880,-3469);p.revalidateZone(true);
   var handler=VoicedCommandHandler.getInstance().getHandler("muelle");if(handler==null)throw new IllegalStateException("No .muelle handler registered");
   report.append("handler="+handler.getClass().getName()+"\nfrom="+p.getX()+","+p.getY()+","+p.getZ()+"\n");
   handler.onCommand("muelle",p,"");
   report.append("after_command="+p.getX()+","+p.getY()+","+p.getZ()+" instance="+p.getInstanceId()+" pending="+p.isTeleporting()+"\n");
   if(p.getX()!=149000||p.getY()!=46700||Math.abs(p.getZ()-12016)>40)throw new IllegalStateException("Command did not reach dock");
   // Appearing.runImpl calls this when the client's map load is complete.
   p.onTeleported();Thread.sleep(1500);
   report.append("after_appearing="+p.getX()+","+p.getY()+","+p.getZ()+" instance="+p.getInstanceId()+" pending="+p.isTeleporting()+"\n");
   if(p.getX()!=149000||p.getY()!=46700||p.getZ()<11000||p.isTeleporting())throw new IllegalStateException("Redirected after Appearing");
   handler.onCommand("muelle",p,"coliseo");p.onTeleported();
   report.append("coliseum_return="+p.getX()+","+p.getY()+","+p.getZ()+"\n");
   if(p.getX()!=148900||p.getY()!=46100||p.getZ()>0)throw new IllegalStateException("Coliseum return failed");
   report.append("PASS: actual .muelle Giran -> dock -> Appearing -> Coliseum, transient character, no client map rendering tested.\n");
  } catch(Throwable error){report.append("FAIL: "+error+"\n");throw error;}
  finally {
   if(p!=null){p.abortAttack();p.abortCast();p.deleteMe();p.setOnlineStatus(false,false);}
   Files.writeString(Path.of(directory,"travel-probe.txt"),report);
  }
 }
}
