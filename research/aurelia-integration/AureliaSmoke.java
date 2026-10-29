import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
public class AureliaSmoke {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  StringBuilder out=new StringBuilder();Player p=null;
  try {
   var geo=GeoEngine.getInstance();int[][] starts={{153400,55800,12064},{156000,55000,11320},{156000,55000,10816},{151700,55000,11696}};
   int[][] walks={{152008,53512,11312,152024,53512,11312},{152008,53512,11312,152008,53528,11312},{152024,53512,11312,152040,53512,11312},{152024,53512,11312,152024,53528,11312},{152040,53512,11312,152056,53512,11312},{152040,53512,11312,152040,53528,11312},{152056,53512,11312,152072,53512,11312},{152056,53512,11312,152056,53528,11312},{152072,53512,11312,152088,53512,11312},{152072,53512,11312,152072,53528,11312},{152088,53512,11312,152104,53512,11312},{152088,53512,11312,152088,53528,11312},{152104,53512,11312,152120,53512,11312},{152104,53512,11312,152104,53528,11312},{152120,53512,11312,152136,53512,11312},{152120,53512,11312,152120,53528,11312},{152120,53512,11160,152136,53512,11160},{152136,53512,11312,152152,53512,11312},{152136,53512,11312,152136,53528,11312},{152152,53512,11312,152168,53512,11312},{152152,53512,11312,152152,53528,11312},{152152,53512,11152,152168,53512,11152},{152168,53512,11312,152184,53512,11312},{152168,53512,11312,152168,53528,11312}},walls={{152488,53512,11312,152504,53512,11312},{152712,53512,12064,152712,53528,12064},{152728,53512,12064,152744,53512,12064},{152776,53512,12064,152776,53528,12064},{152792,53512,12064,152808,53512,12064},{152792,53512,12064,152792,53528,12064},{152824,53512,12064,152840,53512,12064},{153480,53512,11312,153496,53512,11312},{153496,53512,11312,153512,53512,11312},{154488,53512,11312,154504,53512,11312},{154488,53512,10816,154504,53512,10816},{154504,53512,11312,154520,53512,11312},{155480,53512,11312,155496,53512,11312},{155480,53512,10816,155496,53512,10816},{155496,53512,11312,155512,53512,11312},{155496,53512,10816,155512,53512,10816}};
   for(int[] e:walks)if(!geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Open edge blocked "+java.util.Arrays.toString(e));
   for(int[] e:walls)if(geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Wall open "+java.util.Arrays.toString(e));
   out.append("open_edges=24 closed_edges=16\n");
   if(Math.abs(geo.getHeight(152000,46700,12040)-12040)>40||Math.abs(geo.getHeight(149000,46700,12040)-12016)>8||Math.abs(geo.getHeight(148900,46100,-3400)+3400)>100)throw new IllegalStateException("Prior floors changed");
   var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
   var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
   p=ctor.newInstance(template,"aurelia-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
   p.setName("AureliaProbe");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(83020,147880,-3469);
   var handler=VoicedCommandHandler.getInstance().getHandler("muelle");if(handler==null)throw new IllegalStateException("Missing handler");
   String[] actions={"aurelia","aurelia a","aurelia b","aurelia puente"};
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
   out.append("PASS: four Aurelia arrivals, movement, peace/respawn, original airship/dock/Coliseum, 24 open and 16 closed edges. Transient probe only. Client rendering/physics and moving transport not tested.\n");
  }catch(Throwable e){out.append("FAIL: "+e+"\n");throw e;}
  finally {if(p!=null){p.abortAttack();p.abortCast();p.deleteMe();p.setOnlineStatus(false,false);}Files.writeString(Path.of(directory,"server-smoke.txt"),out);}
 }
}
