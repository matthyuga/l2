import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.RoomTeleportSync;
import org.l2jmobius.gameserver.network.serverpackets.TeleportToLocation;
public class CheckClientRoomBoundary {
 static void require(boolean ok,String s){if(!ok)throw new IllegalStateException(s);}
 static void place(Player p,int x,int y,int z){
  RoomTeleportSync.arm(p,p.getInstanceId());p.stopMove(null);p.abortAttack();p.abortCast();p.setTarget(null);p.getAI().setIntentionActive();
  p.setXYZ(x,y,z);p.setClientX(x);p.setClientY(y);p.setClientZ(z);p.setCursorKeyMovement(false);p.setLastServerPosition(x,y,z);p.revalidateZone(true);
  p.broadcastPacket(new TeleportToLocation(p,x,y,z,p.getHeading()));p.broadcastInfo();
 }
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  StringBuilder b=new StringBuilder();
  try {
   Player p=World.getPlayer(268473899);require(p!=null && p.getName().equals("Hellkevin") && p.getClient()!=null && p.isOnline(),"Connected player unavailable");
   int room=p.getInstanceId();require(room>0 && p.getPvpFlag()==1 && !p.isDead(),"Not in live PvP room");
   int originX=p.getX(),originY=p.getY();
   int floor=GeoEngine.getInstance().getHeight(49240,52100,-2792);
   require(floor>-3800 && floor<-2000,"Unsafe test boundary floor");
   boolean invul=p.isInvul();
   place(p,49240,52100,floor);Thread.sleep(1500);
   require(p.getInstanceId()==room && p.getPvpFlag()==1 && !p.isDead(),"Boundary countdown lost room/flag or player died");
   require(p.isInvul()==invul && !p.isTeleportProtected(),"Boundary added protection");
   place(p,49100,52100,GeoEngine.getInstance().getHeight(49100,52100,floor));Thread.sleep(700);
   require(p.getInstanceId()==room && p.getPvpFlag()==1 && Math.abs(p.getX()-originX)<100 && Math.abs(p.getY()-originY)<100,"Cancellation did not retain flag and return to last interior point");
   b.append("PASS connected-client boundary countdown and cancellation; retained flag and last interior position; no added protection.\n");
   long begin=System.nanoTime();place(p,49240,52100,floor);
   Thread.sleep(3500);require(p.getInstanceId()==room && p.getPvpFlag()==1,"Boundary exited before four seconds");
   while(p.getInstanceId()==room && System.nanoTime()-begin<6_000_000_000L)Thread.sleep(25);
   long elapsed=(System.nanoTime()-begin)/1_000_000;
   require(p.getInstanceId()==0 && Math.abs(p.getX()-83425)<100 && Math.abs(p.getY()-148585)<100,"Boundary did not return client to Giran");
   b.append("PASS connected-client boundary completed to Giran in ").append(elapsed).append(" ms; flag=").append(p.getPvpFlag()).append(".\n");
   Thread.sleep(7000);
   require(p.getInstanceId()==0 && Math.abs(p.getX()-83425)<100 && Math.abs(p.getY()-148585)<100,"Giran exit rubberbanded after sync window");
   b.append("PASS Giran remained stable beyond synchronization timeout.\n");
   VoicedCommandHandler.getInstance().getHandler("salas").onCommand("salas",p,"entrar");Thread.sleep(2000);
   require(p.getInstanceId()==room && p.getPvpFlag()==1,"Final arena re-entry failed");
   b.append("PASS returned Hellkevin to Elven with flag active. Visual bar still depends on user confirmation.\n");
  }catch(Throwable t){b.append("FAIL ").append(t).append('\n');throw t;}
  finally{Files.writeString(Path.of(dir,"client-boundary-verification.txt"),b);}
 }
}
