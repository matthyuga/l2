import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.config.custom.WorldContentConfig;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.scripting.ScriptEngine;
public class WorldContentMaintenance {
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  if(World.getPlayers().stream().anyMatch(p->p.getClient()!=null))throw new IllegalStateException("Client connected during maintenance");
  WorldContentConfig.load();
  if(VoicedCommandHandler.getInstance().getHandler("agite")==null)ScriptEngine.getInstance().executeScript(Path.of("custom/GroupAgite/GroupAgite.java"));
  if(VoicedCommandHandler.getInstance().getHandler("agite")==null)throw new AssertionError("GroupAgite not registered");
  for(String line:Files.readAllLines(Path.of(dir,"reputation-before.tsv"))){String[] v=line.split("\t");var clan=ClanTable.getInstance().getClan(Integer.parseInt(v[0]));if(clan==null||!clan.getName().equals(v[1]))throw new AssertionError("Clan identity changed");clan.addReputationScore(Integer.parseInt(v[2])-clan.getReputationScore());clan.updateClanInDB();}
  Files.writeString(Path.of(dir,"maintenance-preservation.txt"),"PASS\nGroupAgite retained\nClan reputation restored from pre-maintenance backup (native restart had awarded castle points)\n");
 }
}
