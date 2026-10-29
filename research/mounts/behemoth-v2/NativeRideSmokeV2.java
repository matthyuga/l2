package custom.BehemothNativeRide;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
import org.l2jmobius.gameserver.network.serverpackets.Ride;
public final class NativeRideSmokeV2 {
 private static void check(boolean v,String s,List<String> checks){if(!v)throw new AssertionError(s);checks.add(s);}
 public static void run(BehemothNativeRide service)throws Exception {
  var checks=new ArrayList<String>();Player p=null;Throwable failure=null;
  try{
   var template=PlayerTemplateData.getInstance().getTemplate(0);var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,PlayerAppearance.class);ctor.setAccessible(true);p=ctor.newInstance(template,"behemoth-native-transient",new PlayerAppearance((byte)0,(byte)0,(byte)0,false));p.setName("NativeBehemothQA");p.setAccessLevel(0);p.setLabControlled(true);p.setDead(false);p.setOnlineStatus(true,false);p.setEnteredWorld();int x=83525,y=148585,z=GeoEngine.getInstance().getHeight(x,y,-3401);p.spawnMe(x,y,z);p.revalidateZone(true);p.setCurrentHp(p.getMaxHp());float height=p.getCollisionHeight();
   check(!p.isMounted()&&!BehemothSeatSync.isSeated(p),"normal initial state",checks);
   var npc=service.summon(p);check(npc.getTemplate().getFCollisionHeight()==54,"initial native dimensions",checks);
   service.mount(p);check(p.isMounted()&&p.getMountNpcId()==59091&&p.getMountType().ordinal()==1,"native strider Ride state with dedicated Behemoth id",checks);
   var ride=new Ride(p);var type=Ride.class.getDeclaredField("_rideType");type.setAccessible(true);var id=Ride.class.getDeclaredField("_rideNpcId");id.setAccessible(true);check(type.getInt(ride)==1&&id.getInt(ride)==1059091,"Ride packet uses type1 and custom model id",checks);
   check(!BehemothSeatSync.isSeated(p)&&!p.isMovementDisabled()&&!BehemothSeatSync.onMove(p,x+100,y,z),"normal player movement retained without remote NPC guard",checks);
   check(!npc.isSpawned(),"offered NPC removed after native mount",checks);
   check(p.getCollisionHeight()==54&&p.getCollisionRadius()==63,"mounted native collision resolves without missing template",checks);
   check(Double.isFinite(p.getRunSpeed())&&p.getRunSpeed()>0,"mounted movement speed resolves",checks);
   int stops=NativeRideMotion.arrivals();p.moveToLocation(p.getX()+80,p.getY(),p.getZ(),0);check(p.isMoving(),"native mounted movement starts",checks);NativeRideMotion.tick(p);check(NativeRideMotion.arrivals()==stops,"arrival guard does not stop a moving mount",checks);p.stopMove(null);NativeRideMotion.tick(p);check(NativeRideMotion.arrivals()==stops+1,"arrival sends an explicit normal StopMove packet",checks);NativeRideMotion.tick(p);check(NativeRideMotion.arrivals()==stops+1,"idle ticks do not repeat StopMove packets",checks);
   service.release(p,"QA");check(!p.isMounted()&&p.getMountNpcId()==0&&p.getCollisionHeight()==height&&!p.isMovementDisabled(),"dismount restores ordinary character state",checks);
   service.summon(p);service.mount(p);p.setDead(true);var tick=BehemothNativeRide.class.getDeclaredMethod("tick");tick.setAccessible(true);tick.invoke(service);check(!p.isMounted(),"death cleanup releases native ride",checks);p.setDead(false);p.setCurrentHp(p.getMaxHp());
   service.summon(p);service.mount(p);p.setOnlineStatus(false,false);tick.invoke(service);check(!p.isMounted(),"disconnect cleanup releases native ride",checks);p.setOnlineStatus(true,false);
   check(VoicedCommandHandler.getInstance().getHandler("behemoth")==service,"active command handler uses new native module",checks);
  }catch(Throwable e){failure=e;}
  finally{if(p!=null){service.release(p,"QA cleanup");service.onCommand("behemoth",p,"guardar");p.deleteMe();p.setOnlineStatus(false,false);}String rows=checks.stream().map(s->"\""+s+"\"").reduce((a,b)->a+","+b).orElse("");String error=failure==null?"null":"\""+failure.toString().replace("\\","\\\\").replace("\"","\\\"")+"\"";Files.writeString(Path.of("../../research/mounts/behemoth-v2/native-ride-smoke.json"),"{\"passed\":"+(failure==null)+",\"realNetworkClients\":false,\"persistentCharactersCreated\":false,\"checks\":["+rows+"],\"error\":"+error+"}");}
  if(failure!=null)throw new RuntimeException(failure);
 }
}
