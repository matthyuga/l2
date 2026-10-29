import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
public class VigiliaSmoke {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  StringBuilder out=new StringBuilder();Player p=null;
  try {
   var geo=GeoEngine.getInstance();int[][] starts={{146500,52000,12080},{147400,52000,12080}};
   int[][] walks={{145304,51608,12080,145320,51608,12080},{145304,51608,12080,145304,51624,12080},{145320,51608,12080,145336,51608,12080},{145320,51608,12080,145320,51624,12080},{145336,51608,12080,145352,51608,12080},{145336,51608,12080,145336,51624,12080},{145352,51608,12080,145368,51608,12080},{145352,51608,12080,145352,51624,12080},{145368,51608,12080,145384,51608,12080},{145368,51608,12080,145368,51624,12080},{145384,51608,12080,145400,51608,12080},{145384,51608,12080,145384,51624,12080},{145400,51608,12080,145416,51608,12080},{145400,51608,12080,145400,51624,12080},{145416,51608,12080,145432,51608,12080},{145416,51608,12080,145416,51624,12080},{145432,51608,12080,145448,51608,12080},{145432,51608,12080,145432,51624,12080},{145448,51608,12080,145464,51608,12080},{145448,51608,12080,145448,51624,12080},{145464,51608,12080,145480,51608,12080},{145464,51608,12080,145464,51624,12080},{145480,51608,12080,145496,51608,12080},{145480,51608,12080,145480,51624,12080}},walls={{145128,51624,12392,145128,51640,12392},{145848,51624,12392,145848,51640,12392},{145144,51640,12392,145160,51640,12392},{145800,51640,12080,145800,51656,12080},{145816,51640,12392,145832,51640,12392},{145816,51640,12080,145816,51656,12080},{147704,51640,12104,147704,51656,12104},{145192,51656,12400,145208,51656,12400},{145192,51656,12400,145192,51672,12400},{145208,51656,12400,145208,51672,12400},{145256,51656,12080,145256,51672,12080},{145272,51656,12080,145272,51672,12080},{145288,51656,12080,145288,51672,12080},{145304,51656,12080,145304,51672,12080},{145320,51656,12080,145320,51672,12080},{145336,51656,12080,145336,51672,12080}};
   for(int[] e:walks)if(!geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Open edge blocked "+java.util.Arrays.toString(e));
   for(int[] e:walls)if(geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Wall open "+java.util.Arrays.toString(e));
   out.append("open_edges=24 closed_edges=16\n");
   if(Math.abs(geo.getHeight(152000,46700,12040)-12040)>40||Math.abs(geo.getHeight(149000,46700,12040)-12016)>8||Math.abs(geo.getHeight(148900,46100,-3400)+3400)>100)throw new IllegalStateException("Prior floors changed");
   var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
   var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
   p=ctor.newInstance(template,"vigilia-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
   p.setName("VigiliaProbe");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(83020,147880,-3469);
   var handler=VoicedCommandHandler.getInstance().getHandler("muelle");if(handler==null)throw new IllegalStateException("Missing handler");
   String[] actions={"dragon","dragon proa"};
   for(int i=0;i<starts.length;i++) {
    int[] q=starts[i];if(geo.getHeight(q[0],q[1],q[2]-24)!=q[2]-24)throw new IllegalStateException("Spawn floor mismatch "+actions[i]);
    handler.onCommand("muelle",p,actions[i]);p.onTeleported();Thread.sleep(300);p.revalidateZone(true);
    if(p.getX()!=q[0]||p.getY()!=q[1]||Math.abs(p.getZ()-(q[2]-24))>40||p.isTeleporting())throw new IllegalStateException("Arrival mismatch "+actions[i]);
    if(!p.isInsideZone(ZoneId.PEACE))throw new IllegalStateException("Peace zone absent");
    var rz=org.l2jmobius.gameserver.managers.ZoneManager.getInstance().getZone(p,org.l2jmobius.gameserver.entity.zone.type.RespawnZone.class);
    if(rz==null||!"gludio_sky".equals(rz.getRespawnPoint(p)))throw new IllegalStateException("Safe respawn absent");
    int moves=0;for(int[] d:new int[][]{{64,0},{-64,0},{0,64},{0,-64}})if(geo.canMoveToTarget(q[0],q[1],q[2],q[0]+d[0],q[1]+d[1],q[2],0))moves++;
    if(moves<2)throw new IllegalStateException("Arrival boxed in "+actions[i]);
    out.append(actions[i]+"="+p.getX()+","+p.getY()+","+p.getZ()+" moves="+moves+" peace=true respawn=gludio_sky\n");
   }
   handler.onCommand("muelle",p,"coliseo");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=148900||p.getY()!=46100||p.getZ()>0)throw new IllegalStateException("Coliseum return failed");
   handler.onCommand("muelle",p,"");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=149000||p.getY()!=46700)throw new IllegalStateException("Dock return failed");
   handler.onCommand("muelle",p,"nave");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=152000||p.getY()!=46700)throw new IllegalStateException("Old airship travel changed");
   handler.onCommand("muelle",p,"aurelia");p.onTeleported();Thread.sleep(300);
   if(p.getX()!=153400||p.getY()!=55800)throw new IllegalStateException("Aurelia travel changed");
   if(Math.abs(geo.getHeight(156000,55000,11296)-11296)>16||Math.abs(geo.getHeight(156000,55000,10792)-10792)>16)throw new IllegalStateException("Aurelia interior floors changed");
   out.append("PASS: two Vigilia arrivals, movement, peace/respawn, Aurelia + original airship/dock/Coliseum, 24 open and 16 closed edges. Transient probe only. Client rendering/physics and moving transport not tested.\n");
  }catch(Throwable e){out.append("FAIL: "+e+"\n");throw e;}
  finally {if(p!=null){p.abortAttack();p.abortCast();p.deleteMe();p.setOnlineStatus(false,false);}Files.writeString(Path.of(directory,"server-smoke.txt"),out);}
 }
}
