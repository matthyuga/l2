import custom.ElvenPvpRoom.RoomTacticalPolicy;
import custom.ElvenPvpRoom.RoomTacticalPolicy.Role;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import java.nio.file.*;
public final class RoleCompatibilityCheck{
 public static void main(String[] args)throws Exception{
  int checked=0;StringBuilder out=new StringBuilder();
  for(PlayerClass c:PlayerClass.values())if(c.getId()>=88&&c.getId()<=118){
   String weapon=switch(c.name()){case "SAGITTARIUS","MOONLIGHT_SENTINEL","GHOST_SENTINEL"->"BOW";case "ADVENTURER","WIND_RIDER","GHOST_HUNTER"->"DAGGER";default->"SWORD";};
   Role role=RoomTacticalPolicy.role(c.name(),weapon,c.isMage());out.append(c).append('=').append(role).append('\n');checked++;
   if(c.name().equals("EVA_SAINT")&&role!=Role.HEALER||c.name().equals("EVA_TEMPLAR")&&role!=Role.TANK)throw new AssertionError("Wrong Mobius EVA class mapping");
  }
  if(checked!=31)throw new AssertionError("Expected31thirdclasses, got"+checked);
  Files.writeString(Path.of(args[0]),"PASS31nativeadvancedclassnames resolved\n"+out);System.out.println("PASS31nativeclassmappings");
 }
}
