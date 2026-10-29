import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.nio.file.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.custom.ModularAppearance;
import org.l2jmobius.gameserver.custom.ModularAppearance.Profile;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class AuditModularMenu {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  int id;
  try(var con=DatabaseFactory.getConnection();var ps=con.prepareStatement("SELECT charId FROM characters WHERE char_name='BodySexProbe' AND account_name='modular-test' AND online=0");var rs=ps.executeQuery()){if(!rs.next())throw new IllegalStateException("Reserved probe missing");id=rs.getInt(1);}
  Player p=Player.load(id);if(p==null||p.getClient()!=null)throw new IllegalStateException("Probe not detached");p.stopVitalityTask();
  var menu=VoicedCommandHandler.getInstance().getHandler("cuerpo");if(menu==null)throw new IllegalStateException(".cuerpo missing");
  String original=ModularAppearance.state(p);Class<?> type=menu.getClass(),selection=Class.forName(type.getName()+"$Selection",false,type.getClassLoader());
  var constructor=selection.getDeclaredConstructor(Player.class);constructor.setAccessible(true);
  Field profile=selection.getDeclaredField("profile"),origin=selection.getDeclaredField("origin"),page=selection.getDeclaredField("page");for(Field f:new Field[]{profile,origin,page})f.setAccessible(true);
  var show=type.getDeclaredMethod("show",Player.class,selection,boolean.class);show.setAccessible(true);int checks=0;
  for(int race=0;race<9;race++)for(int body=0;body<9;body++)for(boolean female:new boolean[]{false,true})for(int pag=0;pag<2;pag++)for(boolean confirm:new boolean[]{false,true}){
   Object state=constructor.newInstance(p);profile.set(state,new Profile(true,body,female));origin.setInt(state,race);page.setInt(state,pag);show.invoke(null,p,state,confirm);checks++;
  }
  if(!ModularAppearance.state(p).equals(original))throw new IllegalStateException("Rendering menu changed saved state");
  if(p.isGM())throw new IllegalStateException("Probe should have no GM access");
  menu.onCommand("cuerpo",p,"body 1");menu.onCommand("cuerpo",p,"apply invalid");
  if(!ModularAppearance.state(p).equals(original))throw new IllegalStateException("Authorization guard failed");checks+=2;
  Files.writeString(Path.of(directory,"menu-verification.txt"),"PASS: "+checks+" menu render/length/authorization checks using reserved offline probe; no user characters changed.\n");p.stopVitalityTask();
 }
}
