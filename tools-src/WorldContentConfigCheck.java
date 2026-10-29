import java.nio.file.Path;
import org.l2jmobius.gameserver.config.custom.WorldContentConfig;
public class WorldContentConfigCheck {
 public static void main(String[] a){
  WorldContentConfig.load();if(!WorldContentConfig.CUSTOM_WORLD_ONLY)throw new AssertionError("Project profile disabled");
  Path root=Path.of("data/scripts");
  for(String file:new String[]{"custom/GiranSiegeLab/GiranGuardians.java","custom/NormalNpcRoster/NormalNpcRoster.java","custom/AmberContract/AmberContract.java","custom/ClanLab/ClanLab.java"})if(!WorldContentConfig.allowsScript(root,root.resolve(file)))throw new AssertionError(file);
  for(String file:new String[]{"quests/QuestMasterHandler.java","ai/bosses/Valakas/Valakas.java","custom/MissQueen/MissQueen.java","events/TvT/TvT.java","vehicles/BoatGiranTalking.java","village_master/VillageMaster.java"})if(WorldContentConfig.allowsScript(root,root.resolve(file)))throw new AssertionError(file);
  WorldContentConfig.CUSTOM_WORLD_ONLY=false;if(!WorldContentConfig.allowsScript(root,root.resolve("quests/QuestMasterHandler.java")))throw new AssertionError("Classic fallback disabled");
  System.out.println("PASS: project scripts retained;classic scripts excluded;fallback available");
 }
}
