import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.custom.HairColorHsl;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;

public class HslPersistenceProbe {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  int id=-1,checks=0;Player probe=null,loaded=null;String before=null;boolean captured=false;
  try {
   try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT charId,online FROM characters WHERE char_name='BodySexProbe'")){try(var rs=ps.executeQuery()){if(!rs.next()||rs.getInt(2)!=0)throw new IllegalStateException("Reserved offline probe unavailable");id=rs.getInt(1);if(rs.next())throw new IllegalStateException("Probe is not unique");}}
   if(World.getPlayer(id)!=null)throw new IllegalStateException("Probe is in world");checks++;
   var ctor=Player.class.getDeclaredConstructor(int.class,org.l2jmobius.gameserver.entity.actor.templates.PlayerTemplate.class,String.class,PlayerAppearance.class);ctor.setAccessible(true);
   probe=ctor.newInstance(id,PlayerTemplateData.getInstance().getTemplate(0),"_hsl_detached_probe",new PlayerAppearance((byte)0,(byte)2,(byte)0,false));probe.stopVitalityTask();
   before=probe.getVariables().getString(HairColorHsl.VARIABLE,null);captured=true;
   int color=0x319bdb;Object packet=new Object();if(HairColorHsl.read(packet,HairColorHsl.encode(color,2))!=2)throw new AssertionError();checks++;
   HairColorHsl.finish(packet,probe);if(probe.getVariables().getInt(HairColorHsl.VARIABLE,-1)!=color)throw new AssertionError("Variable missing");checks++;
   if(HairColorHsl.selection(id,2)!=HairColorHsl.encode(color,2))throw new AssertionError("Selection SQL persistence failed");checks++;
   loaded=ctor.newInstance(id,PlayerTemplateData.getInstance().getTemplate(0),"_hsl_detached_reload",new PlayerAppearance((byte)0,(byte)2,(byte)0,false));loaded.stopVitalityTask();
   if(HairColorHsl.wire(loaded,2)!=HairColorHsl.encode(color,2))throw new AssertionError("Reload/UserInfo wire failed");checks++;
   if(probe.getAppearance().getHairColor()!=2||loaded.getAppearance().getHairColor()!=2)throw new AssertionError("Legacy color changed");checks++;
  } finally {
   if(captured&&probe!=null){if(before==null)probe.getVariables().remove(HairColorHsl.VARIABLE);else probe.getVariables().set(HairColorHsl.VARIABLE,before);probe.getVariables().saveNow();}
   if(probe!=null)probe.stopVitalityTask();if(loaded!=null)loaded.stopVitalityTask();
  }
  try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT val FROM character_variables WHERE charId=? AND var=?")){ps.setInt(1,id);ps.setString(2,HairColorHsl.VARIABLE);try(var rs=ps.executeQuery()){String actual=rs.next()?rs.getString(1):null;if(!java.util.Objects.equals(before,actual))throw new AssertionError("Probe cleanup mismatch");checks++;}}
  Files.writeString(Path.of(directory,"persistence-proof.txt"),"PASS "+checks+" real-server checks: encoded create state, independent RGB variable, committed SQL selection value, fresh PlayerVariables reload, unchanged A-D value, exact reserved-probe cleanup. No world spawn or user character modified.\n");
 }
}
