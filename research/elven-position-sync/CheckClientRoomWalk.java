import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.Map;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.RoomTeleportSync;
import org.l2jmobius.gameserver.network.serverpackets.TeleportToLocation;
public class CheckClientRoomWalk {
 static void require(boolean b,String s){if(!b)throw new IllegalStateException(s);}
 static Object field(Object o,String n)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(o);}
 static long timer(Object h,Player p)throws Exception{Object v=((Map<?,?>)field(h,"visits")).get(p.getObjectId());return v==null?-1:((Number)field(v,"exitStarted")).longValue();}
 static String state(Player p){return "instance="+p.getInstanceId()+" flag="+p.getPvpFlag()+" xyz="+p.getX()+","+p.getY()+","+p.getZ();}
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  StringBuilder b=new StringBuilder();
  try{
   var p=World.getPlayer(268473899);require(p!=null && p.getClient()!=null && p.isOnline() && p.getName().equals("Hellkevin"),"Connected player unavailable");
   var h=VoicedCommandHandler.getInstance().getHandler("salas");
   h.onCommand("salas",p,"entrar");require(p.getInstanceId()>0 && p.getPvpFlag()==1,"Entry rejected");int room=p.getInstanceId();
   var geo=GeoEngine.getInstance();int y=0,iz=0,oz=0;
   for(int sy=46728;sy<53800;sy+=64){int a=geo.getHeight(49136,sy,-3000),c=geo.getHeight(49264,sy,-3000);if(a>-3800 && a<-2000 && c>-3800 && c<-2000 && geo.canMoveToTarget(49136,sy,a,49264,sy,c,room)){y=sy;iz=a;oz=c;break;}}
   require(y!=0,"No safe east crossing");b.append("Crossing y=").append(y).append(" insideZ=").append(iz).append(" outsideZ=").append(oz).append('\n');
   RoomTeleportSync.arm(p,room);p.stopMove(null);p.abortAttack();p.abortCast();p.getAI().setIntentionActive();
   p.setXYZ(49136,y,iz);p.setClientX(p.getX());p.setClientY(p.getY());p.setClientZ(p.getZ());p.setCursorKeyMovement(false);p.setLastServerPosition(p.getX(),p.getY(),p.getZ());p.revalidateZone(true);
   p.broadcastPacket(new TeleportToLocation(p,p.getX(),p.getY(),p.getZ(),p.getHeading()));p.broadcastInfo();
   Thread.sleep(2200);b.append("Before walk ").append(state(p)).append(" timer=").append(timer(h,p)).append('\n');
   require(p.getInstanceId()==room && p.getX()<49200 && timer(h,p)==0,"Pre-walk sync failed");
   p.getAI().setIntentionMoveTo(new Location(49264,y,oz));long limit=System.nanoTime()+4_000_000_000L;
   while(timer(h,p)==0 && System.nanoTime()<limit)Thread.sleep(25);
   b.append("After outward walk ").append(state(p)).append(" timer=").append(timer(h,p)).append('\n');require(timer(h,p)>0,"Walking did not start countdown");
   Thread.sleep(800);require(p.getPvpFlag()==1 && p.getInstanceId()==room,"Countdown lost flag/instance");
   p.getAI().setIntentionMoveTo(new Location(49136,y,iz));limit=System.nanoTime()+2_500_000_000L;
   while(timer(h,p)>0 && System.nanoTime()<limit)Thread.sleep(25);
   b.append("After inward walk ").append(state(p)).append(" timer=").append(timer(h,p)).append('\n');
   require(p.getInstanceId()==room && p.getX()<49200 && timer(h,p)==0 && p.getPvpFlag()==1,"Walking back did not cancel countdown");
   b.append("PASS actual server movement across safe boundary and cancellation, with client connected.\n");
   // Command exit uses the same four-second deadline and gives the user an uninterrupted bar.
   h.onCommand("salas",p,"salir");long start=System.nanoTime();Thread.sleep(3500);
   require(p.getInstanceId()==room && p.getPvpFlag()==1,"Command exit completed before four seconds");
   while(p.getInstanceId()==room && System.nanoTime()-start<6_000_000_000L)Thread.sleep(25);
   require(p.getInstanceId()==0 && Math.abs(p.getX()-83425)<100 && Math.abs(p.getY()-148585)<100,"Command did not exit to Giran");
   b.append("PASS command exit returned to Giran after ").append((System.nanoTime()-start)/1_000_000).append(" ms.\n");
   Thread.sleep(7000);require(p.getInstanceId()==0 && Math.abs(p.getX()-83425)<100,"Exit sync unstable");
   h.onCommand("salas",p,"entrar");Thread.sleep(1500);require(p.getInstanceId()==room && p.getPvpFlag()==1,"Final re-entry rejected/unstable");
   b.append("PASS stable Giran exit and final Elven re-entry.\n");
  }catch(Throwable t){b.append("FAIL ").append(t).append('\n');throw t;}
  finally{Files.writeString(Path.of(dir,"client-walk-verification.txt"),b);}
 }
}
