package custom.ElvenPvpRoom;
import java.util.*;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.item.enums.*;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureSkillUse;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
/** Native consumables and summons, exclusively for the room's reserved lab actors. */
public final class PvpSiegeCombat {
 private static final Map<Player,Long> SUMMON_AT=new IdentityHashMap<>();
 private static final Map<Player,Map<String,Long>> COUNTS=new IdentityHashMap<>();
 private static final Map<Player,ConsumerEventListener> LISTENERS=new IdentityHashMap<>();
 public static synchronized void forget(Player p){SUMMON_AT.remove(p);COUNTS.remove(p);var listener=LISTENERS.remove(p);if(listener!=null)listener.unregisterMe();}
 private static synchronized void count(Player p,String key){COUNTS.computeIfAbsent(p,k->new TreeMap<>()).merge(key,1L,Long::sum);}
 public static synchronized String report(Player p){return String.valueOf(COUNTS.getOrDefault(p,Map.of()));}
 public static void castAccepted(Player p,Skill skill){count(p,"skill_accepted_"+skill.getId());}
 private static int grade(Player p){
  if(p.getActiveWeaponItem()==null)return -1;
  return switch(p.getActiveWeaponItem().getCrystalTypePlus().toString()){case "D"->1;case "C"->2;case "B"->3;case "A"->4;case "S"->5;default->0;};
 }
 public static void stock(Player p){
  if(!PvpSiegeRoster.owned(p))throw new IllegalStateException("Not a reserved room bot");
  synchronized(PvpSiegeCombat.class){if(!LISTENERS.containsKey(p)){var listener=new ConsumerEventListener(p,EventType.ON_CREATURE_SKILL_USE,(OnCreatureSkillUse e)->{if(e.getCaster()==p)count(p,"skill_executed_"+e.getSkill().getId());},PvpSiegeCombat.class);p.addListener(listener);LISTENERS.put(p,listener);}}
  for(int[] entry:new int[][]{{5592,50},{728,60},{1539,60},{2131,1200}})supply(p,entry[0],entry[1]);
  int grade=grade(p);if(grade>=0){supply(p,new int[]{1835,1463,1464,1465,1466,1467}[grade],4000);supply(p,new int[]{3947,3948,3949,3950,3951,3952}[grade],4000);if(p.getActiveWeaponItem().getItemType().toString().contains("BOW"))supply(p,new int[]{17,1341,1342,1343,1344,1345}[grade],4000);}
  for(Skill skill:p.getAllSkills())if(!skill.isPassive()&&skill.getItemConsumeId()>0)supply(p,skill.getItemConsumeId(),Math.max(100,Math.min(2000,skill.getItemConsumeCount()*5)));
 }
 private static void supply(Player p,int id,int amount){long have=p.getInventory().getInventoryItemCount(id,-1);if(have<amount)p.getInventory().addItem(ItemProcessType.NONE,id,(int)(amount-have),p,null);}
 public static void maintain(Player p){
  if(!PvpSiegeRoster.owned(p)||p.isDead())return;
  if(p.getCurrentMp()<p.getMaxMp()*.5)item(p,728,true);
  if(p.getCurrentHp()<p.getMaxHp()*.65&&!p.isAffectedBySkill(2037))item(p,1539,true);
  if(p.getCurrentCp()<p.getMaxCp()*.5)item(p,5592,true);
 }
 public static boolean item(Player p,int id,boolean potion){
  if(!PvpSiegeRoster.owned(p)||p.isOutOfControl()||p.isControlBlocked())return false;
  Item item=p.getInventory().getItemByItemId(id);if(item==null||item.getCount()==0)return false;
  if(p.getItemRemainingReuseTime(item.getObjectId())>0||(item.getReuseDelay()>0&&p.getReuseDelayOnGroup(item.getSharedReuseGroup())>0)||!item.getTemplate().checkCondition(p,p,false))return false;
  IItemHandler handler=ItemHandler.getInstance().getHandler(item.getEtcItem());if(handler==null)return false;
  WorldObject previous=p.getTarget();if(potion)p.setTarget(p);boolean accepted;
  try{accepted=handler.onItemUse(p,item,false);}finally{if(potion)p.setTarget(previous);}
  if(accepted){if(item.getReuseDelay()>0)p.addTimeStampItem(item,item.getReuseDelay());count(p,"item_used_"+id);}return accepted;
 }
 public static void shot(Player p,boolean magic){
  int grade=grade(p);if(grade<0||p.isChargedShot(magic?ShotType.BLESSED_SPIRITSHOTS:ShotType.SOULSHOTS))return;
  item(p,(magic?new int[]{3947,3948,3949,3950,3951,3952}:new int[]{1835,1463,1464,1465,1466,1467})[grade],false);
 }
 public static boolean summon(Player p){
  if(p.hasSummon()&&p.getSummon().isDead())p.getSummon().unSummon(p);
  if(p.hasSummon()){
   Skill tp=p.getKnownSkill(1262);
   if(tp!=null&&!p.isAffectedBySkill(1262)&&supportCast(p,tp)){count(p,"transfer_pain_accepted");return true;}
   return false;
  }
  long now=System.currentTimeMillis();if(now<SUMMON_AT.getOrDefault(p,0L))return false;
  for(Skill skill:p.getAllSkills().stream().filter(k->!k.isPassive()&&k.getName().startsWith("Summon ")&&!k.getName().contains("Cubic")&&!k.getName().contains("Siege")&&!k.getName().contains("Cannon")&&!k.getName().contains("Flag")).sorted(Comparator.comparingInt(k->k.getId()==1331||k.getId()==1332||k.getId()==1333?0:1)).toList()){
   if(supportCast(p,skill)){SUMMON_AT.put(p,now+20000);count(p,"summon_accepted_"+skill.getId());return true;}
  }
  SUMMON_AT.put(p,now+5000);return false;
 }
 private static boolean supportCast(Player p,Skill skill){
  if(p.isCastingNow()||p.isSkillDisabled(skill)||p.getCurrentMp()<skill.getMpConsume()+skill.getMpInitialConsume()||p.getCurrentHp()<=skill.getHpConsume())return false;
  if(skill.getItemConsumeId()>0&&p.getInventory().getInventoryItemCount(skill.getItemConsumeId(),-1)<skill.getItemConsumeCount())return false;
  p.setTarget(p);if(!skill.checkCondition(p,p,false))return false;shot(p,skill.isMagic());return p.useMagic(skill,true,true);
 }
 public static void orderSummon(Player p,Player enemy){
  if(!p.hasSummon()||p.getSummon().isDead())return;
  var pet=p.getSummon();if(pet.getInstanceId()!=p.getInstanceId())return;
  pet.setRunning();pet.setFollowStatus(false);
  if(pet.getAI().getIntention()!=Intention.ATTACK||pet.getAI().getAttackTarget()!=enemy){pet.setTarget(enemy);pet.getAI().setIntentionAttack(enemy);}
 }
}
