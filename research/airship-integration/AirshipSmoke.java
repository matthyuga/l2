import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
public class AirshipSmoke {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  StringBuilder out=new StringBuilder();Player p=null;
  try {
   var geo=GeoEngine.getInstance();int floor=geo.getHeight(152000,46700,12040);out.append("ship_floor="+floor+"\n");
   if(Math.abs(floor-12040)>40)throw new IllegalStateException("Missing ship deck");
   if(Math.abs(geo.getHeight(149000,46700,12040)-12016)>8)throw new IllegalStateException("Dock floor changed");
   if(Math.abs(geo.getHeight(148900,46100,-3400)+3400)>100)throw new IllegalStateException("Coliseum lower floor changed");
   var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
   var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
   p=ctor.newInstance(template,"airship-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
   p.setName("AirshipProbe");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(83020,147880,-3469);
   var handler=VoicedCommandHandler.getInstance().getHandler("muelle");if(handler==null)throw new IllegalStateException("Missing .muelle handler");
   handler.onCommand("muelle",p,"nave");p.onTeleported();Thread.sleep(1000);p.revalidateZone(true);
   out.append("ship_arrival="+p.getX()+","+p.getY()+","+p.getZ()+" instance="+p.getInstanceId()+"\n");
   if(p.getX()!=152000||p.getY()!=46700||Math.abs(p.getZ()-floor)>40||p.isTeleporting())throw new IllegalStateException("Ship teleport failed");
   if(!p.isInsideZone(ZoneId.PEACE))throw new IllegalStateException("Ship is not peace zone");
   int moves=0;for(int[] d:new int[][]{{64,0},{-64,0},{0,64},{0,-64}})if(geo.canMoveToTarget(152000,46700,floor+24,152000+d[0],46700+d[1],floor+24,0))moves++;
   out.append("walkable_cardinal_directions="+moves+"\n");if(moves<2)throw new IllegalStateException("Deck spawn boxed in");
   handler.onCommand("muelle",p,"");p.onTeleported();Thread.sleep(500);
   if(p.getX()!=149000||p.getY()!=46700)throw new IllegalStateException("Dock return failed");out.append("dock_return="+p.getX()+","+p.getY()+","+p.getZ()+"\n");
   handler.onCommand("muelle",p,"nave");p.onTeleported();Thread.sleep(500);handler.onCommand("muelle",p,"coliseo");p.onTeleported();
   if(p.getX()!=148900||p.getY()!=46100||p.getZ()>0)throw new IllegalStateException("Coliseum return from ship failed");
   out.append("coliseum_return="+p.getX()+","+p.getY()+","+p.getZ()+"\nPASS: real handler, deck geo, movement, peace zone, dock and Coliseum return. No client rendering or moving transport tested.\n");
  }catch(Throwable e){out.append("FAIL: "+e+"\n");throw e;}
  finally {if(p!=null){p.abortAttack();p.abortCast();p.deleteMe();p.setOnlineStatus(false,false);}Files.writeString(Path.of(directory,"server-smoke.txt"),out);}
 }
}
