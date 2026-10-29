import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.zone.ZoneId;
public class Dust2Smoke {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  StringBuilder out=new StringBuilder();Player p=null;
  try {
   var geo=GeoEngine.getInstance();
   int[][] starts={{141672,60696,7872},{141528,60696,7872},{141384,60696,7872},{141672,60168,7872},{141240,60696,7872},{141528,60168,7872},{141384,60168,7872},{141240,60168,7872},{141096,60168,7872},{140856,60360,7872},{141672,60360,7872},{141528,60360,7872},{141384,60360,7872},{141240,60360,7872},{141816,60360,7880},{141816,60192,7880},{141240,60552,7872},{141384,60552,7872},{141528,60552,7872},{141672,60552,7872},{139752,55944,8256},{139752,55800,8256},{139752,55656,8256},{139896,55656,8256},{139896,55800,8256},{139896,55944,8256},{140040,55656,8256},{140040,55800,8256},{140040,55944,8256},{140184,55656,8256},{140184,55800,8256},{140184,55944,8256},{140328,55656,8232},{140328,55800,8232},{140328,55944,8232},{139608,55920,8256},{139608,55776,8256},{139464,55800,8256},{139464,55944,8256},{139464,55656,8256}};
   for(int[] s:starts)if(geo.getHeight(s[0],s[1],s[2])!=s[2]-24)throw new IllegalStateException("Spawn floor mismatch "+java.util.Arrays.toString(s));
   out.append("spawn_floors_verified="+starts.length+"\n");
   int[][] walks={{137656,55480,8272,137672,55480,8272},{137656,55480,8272,137656,55496,8272},{137672,55480,8272,137688,55480,8272},{137672,55480,8272,137672,55496,8272},{137688,55480,8272,137704,55480,8272},{137688,55480,8272,137688,55496,8272},{137704,55480,8272,137720,55480,8272},{137704,55480,8272,137704,55496,8272}},walls={{138088,55496,8272,138104,55496,8272},{138104,55512,8264,138120,55512,8264},{138872,55512,8264,138888,55512,8264},{140792,55560,8112,140808,55560,8112},{140808,55576,8104,140824,55576,8104},{140824,55592,8096,140840,55592,8096},{140840,55608,8088,140856,55608,8088},{140856,55624,8080,140872,55624,8080}},layers={{139592,55720,8568},{139592,55720,8232},{139592,55736,8568},{139592,55736,8232},{139592,55752,8568},{139592,55752,8232},{139656,55752,8432},{139656,55752,8232},{139592,55768,8568},{139592,55768,8232}};
   for(int[] e:walks)if(!geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Open movement blocked "+java.util.Arrays.toString(e));
   for(int[] e:walls)if(geo.canMoveToTarget(e[0],e[1],e[2],e[3],e[4],e[5],0))throw new IllegalStateException("Wall traversable "+java.util.Arrays.toString(e));
   for(int[] e:layers)if(geo.getHeight(e[0],e[1],e[2])!=e[2])throw new IllegalStateException("Layer mismatch "+java.util.Arrays.toString(e));
   out.append("open_edges_verified="+walks.length+" blocked_edges_verified="+walls.length+" multilayer_queries="+layers.length+"\n");
   if(Math.abs(geo.getHeight(152000,46700,12040)-12040)>40||Math.abs(geo.getHeight(149000,46700,12040)-12016)>8||Math.abs(geo.getHeight(148900,46100,-3400)+3400)>100)throw new IllegalStateException("Existing dock/airship/Coliseum floors changed");
   var template=org.l2jmobius.gameserver.data.xml.PlayerTemplateData.getInstance().getTemplate(0);
   var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
   p=ctor.newInstance(template,"dust2-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
   p.setName("Dust2Probe");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();p.spawnMe(83020,147880,-3469);
   var handler=VoicedCommandHandler.getInstance().getHandler("dust2");if(handler==null)throw new IllegalStateException("Missing .dust2 handler");
   handler.onCommand("dust2",p,"");p.onTeleported();Thread.sleep(500);p.revalidateZone(true);
   int[] ct=starts[0];if(p.getX()!=ct[0]||p.getY()!=ct[1]||Math.abs(p.getZ()-(ct[2]-24))>40||p.isTeleporting())throw new IllegalStateException("CT arrival failed");
   if(!p.isInsideZone(ZoneId.PEACE))throw new IllegalStateException("Dust2 peace zone missing");
   var rz=org.l2jmobius.gameserver.managers.ZoneManager.getInstance().getZone(p,org.l2jmobius.gameserver.entity.zone.type.RespawnZone.class);
   if(rz==null||!"gludio_sky".equals(rz.getRespawnPoint(p)))throw new IllegalStateException("Dust2 safe respawn missing");
   out.append("ct_arrival="+p.getX()+","+p.getY()+","+p.getZ()+" peace=true respawn=gludio_sky\n");
   handler.onCommand("dust2",p,"t");p.onTeleported();Thread.sleep(500);int[] t=starts[20];
   if(p.getX()!=t[0]||p.getY()!=t[1]||Math.abs(p.getZ()-(t[2]-24))>40)throw new IllegalStateException("T arrival failed");
   out.append("t_arrival="+p.getX()+","+p.getY()+","+p.getZ()+"\n");
   handler.onCommand("dust2",p,"salir");p.onTeleported();Thread.sleep(500);
   if(p.getX()!=83020||p.getY()!=147880)throw new IllegalStateException("Original-location return failed");
   out.append("return="+p.getX()+","+p.getY()+","+p.getZ()+"\nPASS: real handler, 40 spawn floors, movement, blocked walls, distinct height layers, peace/respawn, CT/T, original-location return, existing airship/dock/Coliseum floors. No persistent character or client rendering test.\n");
  }catch(Throwable e){out.append("FAIL: "+e+"\n");throw e;}
  finally {if(p!=null){p.abortAttack();p.abortCast();p.deleteMe();p.setOnlineStatus(false,false);}Files.writeString(Path.of(directory,"server-smoke.txt"),out);}
 }
}
