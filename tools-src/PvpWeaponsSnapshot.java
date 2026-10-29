import java.lang.instrument.*;
import java.util.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.actor.instance.Monster;
import org.l2jmobius.gameserver.entity.actor.Npc;

/** Refresh only Darius's NPC sheet from the validated cache, without spawning an actor. */
public class PvpWeaponsSnapshot {
 public static void agentmain(String unused,Instrumentation i){ThreadPool.execute(()->{Monster npc=null;try{
  var roster=Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals("custom.NormalNpcRoster.NormalNpcRoster")).findFirst().orElseThrow();
  npc=new Monster(NpcData.getInstance().getTemplate(901124));roster.getMethod("applyPreparedStats",Npc.class).invoke(null,npc);
  System.err.println("PVP_WEAPON SNAPSHOT PASS Darius NPC sheet refreshed from native cached Player stats;no spawn or combat event");
 }catch(Throwable e){System.err.println("PVP_WEAPON SNAPSHOT FAILED");e.printStackTrace();}finally{if(npc!=null)npc.deleteMe();}});}
}
