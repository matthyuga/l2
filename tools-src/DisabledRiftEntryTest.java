import java.lang.reflect.*;
import java.util.*;
import org.l2jmobius.gameserver.config.custom.WorldContentConfig;
import org.l2jmobius.gameserver.managers.DimensionalRiftManager;
import org.l2jmobius.gameserver.mechanics.sevensigns.DimensionalRiftRoom;
public class DisabledRiftEntryTest {
 static void check(boolean b,String s){if(!b)throw new AssertionError(s);}
 public static void main(String[] args)throws Exception{
  WorldContentConfig.CUSTOM_WORLD_ONLY=true;
  var m=DimensionalRiftManager.getInstance();
  for(int[] p:new int[][]{{83020,147880,-3469},{116650,145470,-2560},{148900,45500,-3408},{-82000,243000,-3700},{0,0,0}}){
   check(!m.checkIfInRiftZone(p[0],p[1],p[2],false),"Disabled login query");
   check(!m.checkIfInRiftZone(p[0],p[1],p[2],true),"Disabled zone query");
   check(!m.checkIfInPeaceZone(p[0],p[1],p[2]),"Disabled peace query");
  }
  m.teleportToWaitingRoom(null);m.start(null,(byte)1,null);m.reload();
  check(!m.isAllowedEnter((byte)1)&&m.getFreeRooms((byte)1).isEmpty(),"Disabled entry remains unavailable");
  WorldContentConfig.CUSTOM_WORLD_ONLY=false;
  check(!m.checkIfInRiftZone(0,0,0,false)&&!m.checkIfInPeaceZone(0,0,0),"Missing definitions are safe");
  check(!m.isAllowedEnter((byte)9)&&m.getFreeRooms((byte)9).isEmpty(),"Missing type is safe");
  Field f=DimensionalRiftManager.class.getDeclaredField("_rooms");f.setAccessible(true);
  @SuppressWarnings("unchecked") Map<Byte,Map<Byte,DimensionalRiftRoom>> rooms=(Map<Byte,Map<Byte,DimensionalRiftRoom>>)f.get(m);
  rooms.put((byte)0,new HashMap<>());
  rooms.get((byte)0).put((byte)1,new DimensionalRiftRoom((byte)0,(byte)1,0,1000,0,1000,-100,100,0,0,0,false));
  rooms.get((byte)0).put((byte)0,new DimensionalRiftRoom((byte)0,(byte)0,0,300,0,300,-100,100,0,0,0,false));
  check(m.checkIfInRiftZone(500,500,0,false),"Classic combat zone");
  check(!m.checkIfInRiftZone(100,100,0,false)&&m.checkIfInRiftZone(100,100,0,true)&&m.checkIfInPeaceZone(100,100,0),"Classic waiting zone semantics");
  check(!m.checkIfInRiftZone(1500,1500,0,true)&&!m.checkIfInRiftZone(500,500,500,true),"Classic outside XY/Z");
  System.out.println("PASS: disabled-world login queries, inactive operations, missing definitions and classic combat/waiting/outside zone semantics");
 }
}
