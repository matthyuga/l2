package custom.GiranSiegeLab;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import org.l2jmobius.gameserver.ai.Intention;
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

/** Native siege combat with rival-clan targeting and leader conquest; neutral actors stay protected. */
final class SiegeSquadBrain {
 static final Set<Integer> GUARDS=Set.of(35150,35151,35152,35153,35155,35156,35163,35164,35165,35166,35167,35168,35169,903200,903201);
 static boolean allowed(Creature target,Player p){
  if(target==null||target.isDead()||target.getInstanceId()!=p.getInstanceId())return false;
  var c=CastleManager.getInstance().getCastleById(3);
  if(!c.getSiege().isInProgress())return false;
  if(target.isPlayable())return GiranRules.hostile(p,target);
  if(!c.getSiege().checkIsAttacker(p.getClan()))return false;
  boolean permitted=target instanceof Door d?GiranRules.doorAllowed(p,d):target instanceof Tower tower?tower.getCastle()==c:target instanceof Npc n&&GUARDS.contains(n.getId())&&c.checkIfInZone(n.getX(),n.getY(),n.getZ());
  return permitted&&target.isAutoAttackable(p);
 }
 static void act(Pilot a,Player commander,String mode){
  mode=GiranOrders.effective(a.squad,commander,mode);
  Player p=a.p;long now=System.currentTimeMillis();
  if(now<a.nextThink||now<a.squad.launchAt)return;a.nextThink=now+ThreadLocalRandom.current().nextInt(750,1300);
  if(p.isOutOfControl()||p.isControlBlocked())return;
  if(hp(p)<.65&&!p.isAffectedBySkill(2037))item(p,1539,true);
  if(p.getCurrentMp()<p.getMaxMp()*.5)item(p,728,true);
  if(p.isCastingNow())return;
  if(p.isClanLeader()&&GiranRules.castle().getSiege().checkIsAttacker(p.getClan())&&now>a.nextHeadquarters){
   a.nextHeadquarters=now+15000;var flags=GiranRules.castle().getSiege().getFlag(p.getClan());if((flags==null||flags.stream().noneMatch(f->!f.isDead()&&f.isSpawned()))&&p.calculateDistance2D(GiranSiegeLab.camp(a.squad.id,a.slot))<250&&cast(a,247,p,false))return;
  }
  if(mode.equals("retirada")){if(p.hasSummon())p.getSummon().setFollowStatus(true);go(a,GiranSiegeLab.spawnPoint(p,a.squad.id,a.slot));return;}
  for(Pilot ally:a.squad.members)if(ally.p.isDead()&&!ally.p.isReviveRequested()&&cast(a,1016,ally.p,true))return;
  Player patient=a.squad.members.stream().map(b->b.p).filter(q->!q.isDead()).min(Comparator.comparingDouble(SiegeSquadBrain::hp)).orElse(p);
  if(hp(patient)<.65)for(int id:new int[]{1401,1218,1217})if(cast(a,id,patient,true))return;
  if(hp(p)<.25&&cast(a,110,p,false))return;
  if(p.hasSummon()&&p.getSummon().isDead())p.getSummon().unSummon(p);
  if(!p.hasSummon()&&now>a.pendingSummon&&a.summonAttempts<2&&!GiranChaosSiege.machineCarrier(p)){
   if(a.role.equals("SUMMONER"))for(Skill s:p.getAllSkills().stream().filter(k->k.getName().startsWith("Summon ")&&!k.getName().contains("Cubic")&&!k.getName().contains("Siege")&&!k.getName().contains("Cannon")).sorted(Comparator.comparingInt(k->k.getId()==1331||k.getId()==1332||k.getId()==1333?0:1)).toList())if(cast(a,s.getId(),p,false)){a.summonAttempts++;a.pendingSummon=now+20000;return;}
   for(int id:new int[]{1333,1129,1128,1225,1226,1227,1228}){
    Skill s=p.getKnownSkill(id);if(s!=null&&s.getName().contains("Summon")&&!s.getName().contains("Cubic")&&cast(a,id,p,false)){a.summonAttempts++;a.pendingSummon=now+20000;return;}
   }
  }
  if(p.hasSummon()&&cast(a,1262,p,false))return;
  Player captain=a.squad.leader;if(captain==null)return;
  Creature target=a.squad.focus;
  boolean attacker=GiranRules.castle().getSiege().checkIsAttacker(p.getClan())&&!GiranRules.defender(p);
  Creature local=SiegeAgenda.escortTarget(a);
  if(local!=null&&(target==null||!(target instanceof Door)||SiegeAgenda.attackingParty(local,a.squad)||SiegeAgenda.engraving(local)||SiegeTactics.defenderTarget(local)&&p.calculateDistance2D(local)<600))target=local;
  if(target!=null&&SiegeTactics.truce(p,target))target=null;
  if(a.squad.conquest&&p.isClanLeader()&&attacker&&!SiegeTactics.leaderMustFight(a,target)){
   Creature artifact=GiranRules.castle().getArtefacts().iterator().next();
   if(!SiegeTactics.escortBusy(a.squad)&&p.calculateDistance3D(artifact)<=85&&p.getZ()>=artifact.getZ()&&p.getZ()-artifact.getZ()<=45&&cast(a,246,artifact,true))return;
   p.abortAttack();if(p.hasSummon()){p.getSummon().abortAttack();p.getSummon().setFollowStatus(true);}
   if(SiegeTactics.escortBusy(a.squad)){if(p.getAI().getIntention()==Intention.MOVE_TO)p.getAI().setIntentionActive();return;}
   if(a.squad.goal!=null)go(a,new Location(a.squad.goal.getX(),a.squad.goal.getY(),a.squad.goal.getZ()),24);return;
  }
  if(p==captain&&attacker&&target!=null&&target.isPlayable()&&!SiegeTactics.defenderTarget(target)&&!SiegeAgenda.attackingParty(target,a.squad)&&!SiegeAgenda.engraving(target)&&hp(p)>.35)target=null;
  boolean breaching=target instanceof Door&&allowed(target,p)&&p.calculateDistance2D(target)<1400&&GeoEngine.getInstance().canSeeTarget(p,target);
  boolean covering=target!=null&&(target.isPlayable()||SiegeTactics.defenderTarget(target))&&allowed(target,p)&&p.calculateDistance2D(captain)<=3000&&p.calculateDistance2D(target)<=1400&&GeoEngine.getInstance().canSeeTarget(p,target);
  if(p!=captain&&p.calculateDistance2D(captain)>650&&!breaching&&!covering){p.abortAttack();formation(a,captain);return;}
  if(target==null||!allowed(target,p)||p.calculateDistance2D(target)>1300||!GeoEngine.getInstance().canSeeTarget(p,target)){
   p.abortAttack();if(p.hasSummon()){p.getSummon().abortAttack();p.getSummon().setFollowStatus(true);}
   if(p!=captain)formation(a,captain);else if(a.squad.goal!=null)go(a,new Location(a.squad.goal.getX(),a.squad.goal.getY(),a.squad.goal.getZ()));return;
  }
  if(p.hasSummon()&&!GiranChaosMachinery.machine(p.getSummon())){
   Summon pet=p.getSummon();pet.setRunning();pet.setFollowStatus(false);
   if(pet.getAI().getAttackTarget()!=target||pet.getAI().getIntention()!=Intention.ATTACK){pet.setTarget(target);pet.getAI().setIntentionAttack(target);}
  }
  if(!(target instanceof Door)||a.magic()){
   if(a.magic()&&target.isCastingNow()&&!target.isAffectedBySkill(1064)&&cast(a,1064,target,false))return;
   int[] ids=a.magic()?new int[]{1239,1230,1235,1148,1234,1245}:a.role.equals("DAGGER")?new int[]{263,11,12}:a.role.equals("FRONT")?new int[]{347,48,261}:new int[]{343,101};
   for(int id:ids)if(cast(a,id,target,true))return;
  }
  // Leave native autoattack intention running instead of restarting it every tick.
  shot(p,false);if(p.getAI().getAttackTarget()!=target||p.getAI().getIntention()!=Intention.ATTACK){p.setTarget(target);p.getAI().setIntentionAttack(target);}
 }
 static double hp(Creature c){return c.getCurrentHp()/Math.max(1,c.getMaxHp());}
 static void formation(Pilot a,Player commander){double angle=commander.getHeading()*Math.PI/32768;int back=a.magic()?230:130;int side=(a.slot-2)*95;int x=commander.getX()-(int)(Math.cos(angle)*back+Math.sin(angle)*side),y=commander.getY()-(int)(Math.sin(angle)*back-Math.cos(angle)*side);Location loc=SiegeAgenda.safe(x,y,commander.getZ());if(Math.abs(loc.getZ()-commander.getZ())>128)loc=new Location(commander);go(a,loc);}
 static void go(Pilot a,Location loc){go(a,loc,100);}
 static void go(Pilot a,Location loc,int arrival){long now=System.currentTimeMillis();
  if(a.p.calculateDistance2D(a.progressX,a.progressY,a.p.getZ())>30){a.progressX=a.p.getX();a.progressY=a.p.getY();a.lastProgress=now;}
  boolean changed=a.lastDestination==null||Math.hypot(a.lastDestination.getX()-loc.getX(),a.lastDestination.getY()-loc.getY())>32||Math.abs(a.lastDestination.getZ()-loc.getZ())>40;
  boolean stuck=now-a.lastProgress>12000;
  if(now-a.lastMove>1000&&(a.p.calculateDistance2D(loc.getX(),loc.getY(),loc.getZ())>arrival||Math.abs(a.p.getZ()-loc.getZ())>40)&&(changed||stuck||a.p.getAI().getIntention()!=Intention.MOVE_TO)){
   if(stuck){int side=a.slot%2==0?96:-96;Location retry=SiegeAgenda.safe(a.p.getX()+side,a.p.getY()+96,a.p.getZ());if(GeoEngine.getInstance().canMoveToTarget(a.p.getX(),a.p.getY(),a.p.getZ(),retry.getX(),retry.getY(),retry.getZ(),0))loc=retry;a.lastProgress=now;}
   a.p.getAI().setIntentionMoveTo(loc);a.lastMove=now;a.lastDestination=loc;
  }
 }
 static boolean cast(Pilot a,int id,Creature target,boolean repeat){
  Player p=a.p;Skill s=p.getKnownSkill(id);long now=System.currentTimeMillis();
  if(s==null||s.isPassive()||p.isCastingNow()||now<a.reuse.getOrDefault(id,0L))return false;
  if(SiegeTactics.unsafeArea(a,s,target))return false;
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
