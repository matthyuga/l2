package org.l2jmobius.gameserver.config.custom;

import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import org.l2jmobius.commons.util.ConfigReader;

/** Selects project content without removing reusable native skills, items or siege structures. */
public class WorldContentConfig
{
 public static boolean CUSTOM_WORLD_ONLY;
 public static String SPAWN_DIRECTORY;
 public static Set<String> SCRIPT_FOLDERS;
 public static void load()
 {
  ConfigReader config=new ConfigReader("./config/Custom/WorldContent.ini");
  CUSTOM_WORLD_ONLY=config.getBoolean("CustomWorldOnly",false);
  SPAWN_DIRECTORY=config.getString("CustomSpawnDirectory","data/lab/world-spawns");
  SCRIPT_FOLDERS=new HashSet<>(Arrays.asList(config.getString("CustomScriptFolders","AmberContract;ClanLab;ElvenPvpRoom;GiranSiegeLab;GroupAgite;LabCombatPilots;LabRosterSeeder;LabTelemetry;NormalNpcRoster;RaceCustomization;RacialProfileVerification;RealHumanPilots;SkillCatalog;SkillEnchantLab;SoloArenaGauntlet;SummonBuffs;Transmog;WorldDamageNumbers").split(";")));
 }
 public static boolean allowsScript(Path root,Path file)
 {
  if(!CUSTOM_WORLD_ONLY)return true;
  Path relative=root.toAbsolutePath().normalize().relativize(file.toAbsolutePath().normalize());
  if(relative.getNameCount()<2)return false;
  String top=relative.getName(0).toString();
  return top.equals("custom")&&SCRIPT_FOLDERS.contains(relative.getName(1).toString())
    ||top.equals("ai")&&relative.getFileName().toString().equals("AbstractNpcAI.java");
 }
}
