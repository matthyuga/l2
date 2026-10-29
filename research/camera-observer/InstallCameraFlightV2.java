import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;
import custom.CameraFlight.CameraFlight;
public class InstallCameraFlightV2 {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception{
  Path output=Path.of(directory,"flight-stable-install.txt");
  var handlers=VoicedCommandHandler.getInstance();
  var old=handlers.getHandler("camvuelo");
  if(old!=null){
   if(!old.getClass().getName().equals("CameraFlightTrial"))throw new IllegalStateException("Unexpected flight handler");
   var stop=old.getClass().getDeclaredMethod("stop",String.class);stop.setAccessible(true);stop.invoke(old,"upgrade to persistent module");
   handlers.removeHandler(old);
  }
  org.l2jmobius.gameserver.scripting.ScriptEngine.getInstance().executeScript(Path.of("E:/l2-local/server/game/data/scripts/custom/CameraFlight/CameraFlight.java"));
  var installed=handlers.getHandler("camvuelo");
  if(installed==null||!installed.getClass().getName().equals("custom.CameraFlight.CameraFlight"))throw new IllegalStateException("Flight not registered");
  if(installed.onCommand("camvuelo",null,"on"))throw new IllegalStateException("Null caller accepted");
  String report="PASS runtime handler registered; null caller rejected; auto-login listener constructor completed.\n";
  if(World.getPlayer(268436061)==null){
   Player p=Player.load(268436061);
   if(p==null||p.isGM()||!"nexuscamera".equals(p.getAccountName())||!"NexusCam".equals(p.getName())||p.isMounted())throw new IllegalStateException("Offline smoke identity failed");
   boolean invul=p.isInvul(),invisible=p.isInvisible(),paralyzed=p.isParalyzed();
   int x=p.getX(),y=p.getY(),z=p.getZ();p.setOnlineStatus(true,false);
   try{
    var configure=installed.getClass().getDeclaredMethod("configure",Player.class);configure.setAccessible(true);configure.invoke(null,p);
    if(!p.isFlying()||!p.isMounted()||p.isMovementDisabled()||p.getMoveSpeed()<=0||!p.isInvul()||!p.isInvisible()||p.isGM())throw new IllegalStateException("Stable flight flags failed");
    report+="PASS stable native configure: flight/mount/protections, movable, no GM; speed="+p.getMoveSpeed()+"\n";
    p.setMount(0,0);
    if(p.isFlying()||p.isMounted()||p.getX()!=x||p.getY()!=y||p.getZ()!=z)throw new IllegalStateException("Stable cleanup failed");
    report+="PASS stable native mount cleanup; position unchanged.\n";
   }finally{p.setMount(0,0);p.setInvul(invul);p.setInvisible(invisible);p.setParalyzed(paralyzed);p.deleteMe();p.setOnlineStatus(false,true);}
  }else report+="Online pilot present; offline smoke skipped.\n";
  for(String name:new String[]{"camdiag","cammovil"}){
   var probe=handlers.getHandler(name);if(probe!=null)handlers.removeHandler(probe);
  }
  Files.writeString(output,report+"Temporary input/mobility probe commands removed. Existing core classes were not redefined.\n");
 }
}
