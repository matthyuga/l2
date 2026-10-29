package custom.GiranSiegeLab;

import java.util.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.Door;
import org.l2jmobius.gameserver.entity.item.enums.ShotType;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.CastleManager;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import custom.GiranSiegeLab.GiranSiegeLab.Pilot;

/** NPC/door-only native combat. Never targets a player, pet, merchant or conquest artifact. */
final class SiegeSquadBrain {
 static final Set<Integer> GUARDS=Set.of(35150,35151,35152,35153,35155,35156,35163,35164,35165,35166,35167,35168,35169,903200,903201);
 static boolean allowed(Creature target,Player p){
  if(target==null||target.isDead()||target.getInstanceId()!=p.getInstanceId())return false;
  var c=CastleManager.getInstance().getCastleById(3);
  if(!c.getSiege().isInProgress()||!c.getSiege().checkIsAttacker(p.getClan()))return false;
  boolean permitted=target instanceof Door?c.getDoors().contains(target):target instanceof Tower tower?tower.getCastle()==c:target instanceof Npc n&&GUARDS.contains(n.getId())&&c.checkIfInZone(n.getX(),n.getY(),n.getZ());
  return permitted&&target.isAutoAttackable(p);
 }
 static void act(Pilot a,Player commander,String mode){
  Player p=a.p;long now=System.currentTimeMillis();
  if(p.isOutOfControl()||p.isControlBlocked())return;
  if(hp(p)<.65&&!p.isAffectedBySkill(2037))item(p,1539,true);
  if(p.getCurrentMp()<p.getMaxMp()*.5)item(p,728,true);
  if(p.isCastingNow())return;
  if(mode.equals("retirada")){if(p.hasSummon())p.getSummon().setFollowStatus(true);go(a,GiranSiegeLab.camp(a.squad.id,a.slot));return;}
  for(Pilot ally:a.squad.members)if(ally.p.isDead()&&!ally.p.isReviveRequested()&&cast(a,1016,ally.p,true))return;
  Player patient=a.squad.members.stream().map(b->b.p).filter(q->!q.isDead()).min(Comparator.comparingDouble(SiegeSquadBrain::hp)).orElse(p);
  if(hp(patient)<.65)for(int id:new int[]{1401,1218,1217})if(cast(a,id,patient,true))return;
  if(hp(p)<.25&&cast(a,110,p,false))return;
  if(p.hasSummon()&&p.getSummon().isDead())p.getSummon().unSummon(p);
  if(!p.hasSummon()&&now>a.pendingSummon&&a.summonAttempts<2){
   for(int id:new int[]{1333,1129,1128,1225,1226,1227,1228}){
    Skill s=p.getKnownSkill(id);if(s!=null&&s.getName().contains("Summon")&&!s.getName().contains("Cubic")&&cast(a,id,p,false)){a.summonAttempts++;a.pendingSummon=now+20000;return;}
   }
  }
  if(p.hasSummon()&&cast(a,1262,p,false))return;
  Creature target=commander.getTarget() instanceof Creature t&&allowed(t,p)?t:null;
  if(target==null&&mode.equals("asalto"))target=World.getVisibleObjectsInRange(p,Creature.class,1600).stream().filter(t->allowed(t,p)&&GeoEngine.getInstance().canSeeTarget(p,t)).min(Comparator.comparingDouble(t->p.calculateDistance2D(t))).orElse(null);
  if(target==null||p.calculateDistance2D(commander)>1800){p.abortAttack();if(p.hasSummon())p.getSummon().setFollowStatus(true);formation(a,commander);return;}
  if(p.hasSummon()){
   Summon pet=p.getSummon();pet.setRunning();pet.setFollowStatus(false);
   if(pet.getTarget()!=target||!pet.isAttackingNow()){pet.setTarget(target);pet.getAI().setIntentionAttack(target);}
  }
  if(!(target instanceof Door)){
   int[] ids=a.magic()?new int[]{1239,1230,1235,1148,1234,1245}:a.role.equals("DAGGER")?new int[]{263,11,12}:a.role.equals("FRONT")?new int[]{347,48,261}:new int[]{343,101};
   for(int id:ids)if(cast(a,id,target,true))return;
  }
  // Leave native autoattack intention running instead of restarting it every tick.
  shot(p,false);if(p.getTarget()!=target||!p.isAttackingNow()){p.setTarget(target);p.getAI().setIntentionAttack(target);}
 }
 static double hp(Creature c){return c.getCurrentHp()/Math.max(1,c.getMaxHp());}
 static void formation(Pilot a,Player commander){int x=commander.getX()-150-a.squad.id*90,y=commander.getY()+(a.slot-2)*100;go(a,new Location(x,y,commander.getZ()));}
 static void go(Pilot a,Location loc){if(System.currentTimeMillis()-a.lastMove>1500&&a.p.calculateDistance2D(loc.getX(),loc.getY(),loc.getZ())>100){a.p.getAI().setIntentionMoveTo(loc);a.lastMove=System.currentTimeMillis();}}
 static boolean cast(Pilot a,int id,Creature target,boolean repeat){
  Player p=a.p;Skill s=p.getKnownSkill(id);long now=System.currentTimeMillis();
  if(s==null||s.isPassive()||p.isCastingNow()||now<a.reuse.getOrDefault(id,0L))return false;
  if(p.isSkillDisabled(s)||p.getCurrentMp()<s.getMpConsume()+s.getMpInitialConsume()||p.getCurrentHp()<=s.getHpConsume())return false;
  if(!repeat&&target.isAffectedBySkill(id))return false;
  if(target!=p&&(p.calculateDistance2D(target)>Math.max(40,s.getCastRange()<0?s.getAffectRange():s.getCastRange())+30||!GeoEngine.getInstance().canSeeTarget(p,target)))return false;
  if(s.getItemConsumeId()>0&&p.getInventory().getInventoryItemCount(s.getItemConsumeId(),-1)<s.getItemConsumeCount())return false;
  a.reuse.put(id,now+1200);p.setTarget(target);if(!s.checkCondition(p,target,false))return false;shot(p,s.isMagic());return p.useMagic(s,true,true);
 }
 static void shot(Player p,boolean magic){if(!p.isChargedShot(magic?ShotType.BLESSED_SPIRITSHOTS:ShotType.SOULSHOTS))item(p,magic?3952:1467,false);}
 static boolean item(Player p,int id,boolean potion){
  Item it=p.getInventory().getItemByItemId(id);if(it==null||it.getCount()==0||p.isOutOfControl()||p.isControlBlocked())return false;
  if(p.getItemRemainingReuseTime(it.getObjectId())>0||(it.getReuseDelay()>0&&p.getReuseDelayOnGroup(it.getSharedReuseGroup())>0)||!it.getTemplate().checkCondition(p,p,false))return false;
  IItemHandler handler=ItemHandler.getInstance().getHandler(it.getEtcItem());if(handler==null)return false;
  WorldObject previous=p.getTarget();if(potion)p.setTarget(p);boolean accepted;
  try{accepted=handler.onItemUse(p,it,false);}finally{if(potion)p.setTarget(previous);}
  if(accepted&&it.getReuseDelay()>0)p.addTimeStampItem(it,it.getReuseDelay());return accepted;
 }
}
