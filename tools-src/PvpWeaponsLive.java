import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.util.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.type.WeaponType;
import org.l2jmobius.gameserver.data.xml.NpcData;

/** One scoped native equipment update; does not restart a match or modify human Players. */
public class PvpWeaponsLive {
 static Class<?> find(Instrumentation i,String n){return Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals(n)).findFirst().orElseThrow();}
 public static void agentmain(String args,Instrumentation i){ThreadPool.execute(()->{try{
  var sceneClass=find(i,"custom.GiranSiegeLab.GiranChaosSiege");var sf=sceneClass.getDeclaredField("instance");sf.setAccessible(true);Object scene=sf.get(null);
  synchronized(scene){var roster=find(i,"custom.NormalNpcRoster.NormalNpcRoster");var pf=roster.getDeclaredField("PROFILES");pf.setAccessible(true);Object spec=null;
   for(Object candidate:(Object[])pf.get(null)){var name=candidate.getClass().getDeclaredField("name");name.setAccessible(true);if(name.get(candidate).equals("ArenaDarius")){spec=candidate;break;}}
   if(spec==null)throw new IllegalStateException("Darius recipe missing");var weapon=spec.getClass().getDeclaredField("weapon");weapon.setAccessible(true);if(weapon.getInt(spec)!=6370&&weapon.getInt(spec)!=6607)throw new IllegalStateException("Unexpected recipe weapon");
   Player p=World.getPlayer("ArenaDarius");boolean loaded=p==null;var gr=find(i,"custom.GiranSiegeLab.GiranRoster");Method load=gr.getDeclaredMethod("load",String.class),dispose=gr.getDeclaredMethod("dispose",Player.class);load.setAccessible(true);dispose.setAccessible(true);
   if(loaded)p=(Player)load.invoke(null,"Darius");
   try{if(p.getClient()!=null||!p.getAccountName().equals("telemetryarena4")||p.getBaseClass()!=89)throw new IllegalStateException("Reserved profile identity mismatch");
    var current=p.getActiveWeaponItem();if(current==null||current.getId()!=6370&&current.getId()!=6607)throw new IllegalStateException("Unexpected equipped weapon");p.abortAttack();p.abortCast();
    var item=p.getInventory().getItemByItemId(6607);if(item==null)item=p.getInventory().addItem(ItemProcessType.NONE,6607,1,p,null);if(item==null)throw new IllegalStateException("Missing item6607");item.setEnchantLevel(4);p.getInventory().equipItem(item);for(var owned:p.getInventory().getItems())if(owned.getId()==6370||owned.getId()==6607)owned.updateDatabase(true);p.storeMe();p.broadcastUserInfo();
    if(p.getActiveWeaponItem().getId()!=6607||p.getActiveWeaponItem().getItemType()==WeaponType.POLE)throw new IllegalStateException("Native equipment switch failed");weapon.setInt(spec,6607);
    var cache=roster.getDeclaredMethod("cacheNpcStats",spec.getClass(),Player.class);cache.setAccessible(true);cache.invoke(null,spec,p);var telemetry=find(i,"custom.LabTelemetry.LabTelemetry");telemetry.getMethod("captureProfileNow",Player.class).invoke(null,p);telemetry.getMethod("capturePilotStatsNow",Player.class).invoke(null,p);
    for(int id:new int[]{901100,901124}){var t=NpcData.getInstance().getTemplate(id);t.setBaseAttackType(WeaponType.SWORD);if(id==901124){var holder=t.getFakePlayerInfo();var hand=holder.getClass().getDeclaredField("_equipRHand");hand.setAccessible(true);hand.setInt(holder,6607);}}
    int poles=0;for(Player bot:World.getPlayers())if(bot.getName().startsWith("Arena")&&bot.isLabControlled()&&bot.getActiveWeaponItem()!=null&&bot.getActiveWeaponItem().getItemType()==WeaponType.POLE){poles++;System.err.println("PVP_WEAPON remaining pole="+bot.getName());}
    System.err.println("PVP_WEAPON PASS Darius=Heavens Divider Focus+4;native equip+DB+broadcast;recipe/NPC cache updated;remaining live Player poles="+poles+";human,parties and siege unchanged");
   }finally{if(loaded)dispose.invoke(null,p);}
  }
 }catch(Throwable e){System.err.println("PVP_WEAPON FAILED");e.printStackTrace();}});}
}
