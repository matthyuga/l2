import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureSkillUse;
public class VerifyPotions {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  ClassLoader loader=VoicedCommandHandler.getInstance().getHandler("salas").getClass().getClassLoader();var roster=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeRoster");var combat=loader.loadClass("custom.ElvenPvpRoom.PvpSiegeCombat");Player p=(Player)roster.getMethod("acquire").invoke(null);List<Long> cp=new java.util.concurrent.CopyOnWriteArrayList<>();
  var listener=new ConsumerEventListener(p,EventType.ON_CREATURE_SKILL_USE,(OnCreatureSkillUse e)->{if(e.getCaster()==p&&e.getSkill().getId()==2166)cp.add(System.nanoTime());},VerifyPotions.class);p.addListener(listener);
  try{
   p.setCurrentCp(p.getMaxCp()*.10);p.setCurrentMp(p.getMaxMp()*.35);double beforeCp=p.getCurrentCp(),beforeMp=p.getCurrentMp();long start=System.nanoTime();
   while(System.nanoTime()-start<4_000_000_000L){combat.getMethod("maintain",Player.class).invoke(null,p);Thread.sleep(100);}
   long min=Long.MAX_VALUE;for(int i=1;i<cp.size();i++)min=Math.min(min,(cp.get(i)-cp.get(i-1))/1000000);
   String text="actor="+p.getName()+" CP="+beforeCp+" -> "+p.getCurrentCp()+" MP="+beforeMp+" -> "+p.getCurrentMp()+" native_CP_uses="+cp.size()+" minimum_interval_ms="+(cp.size()<2?-1:min)+" report="+combat.getMethod("report",Player.class).invoke(null,p)+"\n";
   Files.writeString(Path.of(directory,"potions.txt"),text);if(cp.size()<2||min<480||p.getCurrentMp()<=beforeMp)throw new IllegalStateException("Native potion cadence check failed");
   Files.writeString(Path.of(directory,"potions-status.txt"),"PASS potion recovery and native500ms CP reuse under100ms polling; no reuse bypass.\n");
  }finally{listener.unregisterMe();roster.getMethod("release",Player.class).invoke(null,p);}
 }
}
