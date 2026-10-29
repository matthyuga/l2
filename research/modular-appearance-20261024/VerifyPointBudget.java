import java.util.*;
import org.l2jmobius.gameserver.custom.ModularAppearance;
import org.l2jmobius.gameserver.custom.ModularAppearance.Profile;
public class VerifyPointBudget {
 public static void main(String[] args){int checks=0;
  for(int body=0;body<9;body++)for(boolean female:new boolean[]{false,true}){
   Profile profile=new Profile(true,body,female);int total=0;
   for(int stat=0;stat<6;stat++){int bonus=ModularAppearance.bonus(profile,stat);if(Math.abs(bonus)>3)throw new AssertionError("Excessive contribution");if(ModularAppearance.bonus(new Profile(false,body,female),stat)!=0)throw new AssertionError("Legacy profile changed");total+=bonus;checks+=2;}
   if(total!=0)throw new AssertionError("Unbalanced contribution");checks++;
  }
  if(!Arrays.equals(ModularAppearance.sexBonuses(false),new int[]{1,-1,1,1,-1,-1})||!Arrays.equals(ModularAppearance.sexBonuses(true),new int[]{-1,1,-1,-1,1,1}))throw new AssertionError("Sex bonuses do not match agreement");checks++;
  try{new Profile(true,9,false);throw new AssertionError("Invalid dwarf mystic accepted");}catch(IllegalArgumentException expected){checks++;}
  System.out.println("PASS: "+checks+" point-budget, legacy, sex and invalid-body checks");
 }
}
