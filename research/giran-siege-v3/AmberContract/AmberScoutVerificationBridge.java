package custom.AmberContract;

import java.util.*;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.holders.ItemHolder;

/** Opt-in verification helper; never accesses the human character. */
public final class AmberScoutVerificationBridge {
 private static final Map<Integer,Integer> levels=new HashMap<>();
 public static AmberServitor build(Player p){
  levels.put(p.getObjectId(),p.getAccessLevel().getLevel());p.setAccessLevel(100);if(!p.isGM())throw new IllegalStateException("Probe requires the configured GM level");p.getVariables().set(AmberContract.CONTRACT,true);
  AmberServitor a=new AmberServitor(NpcData.getInstance().getTemplate(AmberContract.SUMMON),p);a.setName("Amber");a.setTitle(p.getName());a.setShowSummonAnimation(false);a.setLifeTime(86400000);a.setItemConsume(new ItemHolder(0,0));a.setItemConsumeInterval(60000);a.setAttackRange(700);p.setPet(a);a.fullRestore();a.spawnMe(p.getX()+35,p.getY()+35,p.getZ());a.setRunning();a.setFollowStatus(true);a.setCurrentMp(0);
  p.getInventory().addItem(ItemProcessType.NONE,AmberContract.SHOTS,100,p,null);return a;
 }
 public static void enable(AmberServitor a,boolean b){a.assist.enable(b);}
 public static boolean enabled(AmberServitor a){return a.assist.enabled();}
 public static String timing(AmberServitor a){return " intention="+a.getAI().getIntention()+" attack="+a.getAI().getAttackTarget()+" sequence="+a.getAttackEndTime()+" disabled="+a.isAttackDisabled()+" ownerInvul="+a.getOwner().isInvul();}
 public static boolean eligible(AmberServitor a,Creature t){return a.assist.eligible(t);}
 public static boolean legal(AmberServitor a,Creature t){return AmberContract.validVictim(a.getOwner(),a,t);}
 public static String explain(AmberServitor a,Creature t){return "rejection="+AmberContract.targetRejection(a.getOwner(),a,t,false)+" spawned="+t.isSpawned()+" friend="+a.getOwner().isSiegeFriend(t)+" protected="+a.assist.protectedActor(t)+" LOS="+org.l2jmobius.gameserver.geoengine.GeoEngine.getInstance().canSeeTarget(a,t)+" distance="+a.calculateDistance3D(t)+" amber="+a.getX()+","+a.getY()+","+a.getZ()+" target="+t.getX()+","+t.getY()+","+t.getZ();}
 public static void cleanup(Player p){if(p.getSummon() instanceof AmberServitor a)a.unSummon(p);p.getVariables().remove(AmberContract.CONTRACT);Integer level=levels.remove(p.getObjectId());if(level!=null)p.setAccessLevel(level);AmberContract.session(p).cancel();AmberContract.SESSIONS.remove(p.getObjectId());}
}
