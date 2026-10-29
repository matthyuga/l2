import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.PunishmentManager;
import org.l2jmobius.gameserver.mechanics.punishment.*;
import org.l2jmobius.gameserver.mechanics.sevensigns.SevenSigns;

public class LabServiceDiagnostic {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  StringBuilder report=new StringBuilder();
  for(Player p:World.getPlayers())if(p.getClient()!=null){
   report.append("PLAYER "+p.getName()+" GM="+p.isGM()+" chatBanned="+p.isChatBanned()+"\n");
   for(var m:p.getMacros().getAllMacroses().values()){report.append("MACRO "+m.getName()+" ");for(var c:m.getCommands())report.append(c.getType()+":"+c.getCmd()+" | ");report.append("\n");}
   for(var affect:new PunishmentAffect[]{PunishmentAffect.CHARACTER,PunishmentAffect.ACCOUNT,PunishmentAffect.IP}){
    Object key=affect==PunishmentAffect.CHARACTER?p.getObjectId():affect==PunishmentAffect.ACCOUNT?p.getAccountName():p.getIPAddress();
    var task=PunishmentManager.getInstance().getPunishment(key,affect,PunishmentType.CHAT_BAN);
    if(task!=null)report.append("CHAT_BAN "+affect+" reason="+task.getReason()+" expires="+task.getExpirationTime()+"\n");
   }
  }
  for(String cmd:new String[]{"ia","amenaza","agresor"})report.append("HANDLER "+cmd+"="+VoicedCommandHandler.getInstance().getHandler(cmd)+"\n");
  for(String field:new String[]{"_signsSealOwners","_signsDuskSealTotals","_signsDawnSealTotals"}){var f=SevenSigns.class.getDeclaredField(field);f.setAccessible(true);report.append(field+"="+f.get(SevenSigns.getInstance())+"\n");}
  Files.writeString(Path.of(directory,"diagnostic.txt"),report);
 }
}
