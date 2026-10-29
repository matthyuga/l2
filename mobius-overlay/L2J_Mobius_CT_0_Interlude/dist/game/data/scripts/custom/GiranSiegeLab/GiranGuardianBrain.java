package custom.GiranSiegeLab;

import java.util.*;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import custom.GiranSiegeLab.GiranGuardians.Guardian;

/** Local castle protection. No teleport, manufactured damage, buffs to stats, or aggression on friendly/neutral players. */
final class GiranGuardianBrain {
 private static final List<Location> ARES=List.of(
  new Location(114174,145058,-2648),new Location(113250,145095,-2832),
  new Location(114000,145095,-2648),new Location(114650,145095,-2648),new Location(114000,145095,-2648));
 private static final List<Location> NYX=List.of(
  new Location(117400,145064,-2640),new Location(116650,145095,-2560),
  new Location(117400,145064,-2640),new Location(117544,145064,-2640),
  new Location(117608,145064,-2592),new Location(117704,145064,-2528),new Location(117880,145064,-2528),
  new Location(117704,145064,-2528),new Location(117608,145064,-2592),new Location(117544,145064,-2640));
 private static final List<Location> ARES_INNER=List.of(new Location(115700,145095,-2560),new Location(116200,145095,-2560),new Location(116650,145095,-2560),new Location(116200,145095,-2560));
 static boolean innerPost(Guardian g){return g.getId()==903200&&g.getX()>115430&&GiranRules.castle().getDoors().stream().filter(d->d.getId()==23220005||d.getId()==23220006).allMatch(d->!d.isOpen()&&!d.isDead());}
 static List<Location> route(Guardian g){return g.getId()==903200?(innerPost(g)?ARES_INNER:ARES):NYX;}
 static Location post(Guardian g){return innerPost(g)?ARES_INNER.get(0):g.home;}
 static boolean enemy(Guardian g,Creature t){
  var c=GiranRules.castle();Player p=t==null?null:SiegeAgenda.owner(t);
  return c!=null&&c.getSiege().isInProgress()&&p!=null&&!p.isAlikeDead()&&!t.isAlikeDead()&&p.getClan()!=null
   &&c.getSiege().checkIsAttacker(p.getClan())&&!GiranRules.defender(p)&&g.isAutoAttackable(t)
   &&c.checkIfInZone(t.getX(),t.getY(),t.getZ());
 }
 static boolean engageable(Guardian g,Creature t){return enemy(g,t)&&!t.isInvul()&&!t.isInvisible()
  &&System.currentTimeMillis()>=g.holdingUntil&&g.calculateDistance2D(t)<=1600&&t.calculateDistance2D(post(g))<=2000
  &&(!t.isPlayable()||!t.asPlayable().isSilentMovingAffected()||g.calculateDistance2D(t)<=250)
  &&GeoEngine.getInstance().canSeeTarget(g,t);}
 static boolean friendly(Creature t){if(t==null)return false;var c=GiranRules.castle();Player p=SiegeAgenda.owner(t);
  return p!=null&&GiranRules.defender(p)||t instanceof Defender&&c.checkIfInZone(t.getX(),t.getY(),t.getZ())||t instanceof Door d&&d.getCastle()==c;}
 static boolean harmingDefender(Creature t){return t.hasAI()&&(friendly(t.getAI().getAttackTarget())||friendly(t.getAI().getCastTarget()));}
 static double score(Guardian g,Creature t){return (SiegeAgenda.engraving(t)?6000:0)+(harmingDefender(t)?2200:0)
  +(g.getId()==903201&&t.getX()>117500?700:0)+(g.focus==t?150:0)+300*(1-t.getCurrentHp()/Math.max(1,t.getMaxHp()))-g.calculateDistance2D(t)*.4;}
 static Creature choose(Guardian g){List<Creature> choices=new ArrayList<>();World.forEachVisibleObjectInRange(g,Creature.class,1200,t->{if(engageable(g,t))choices.add(t);});
  if(g.focus!=null&&engageable(g,g.focus)&&!choices.contains(g.focus))choices.add(g.focus);
  return choices.stream().max(Comparator.comparingDouble(t->score(g,t))).orElse(null);}
 static void clear(Guardian g){g.abortAttack();g.abortCast();g.clearAggroList();g.getAttackByList().clear();g.focus=null;g.setTarget(null);g.destination=null;g.lastMove=0;g.pauseUntil=0;g.nextSkill=0;if(!g.isAlikeDead())g.getAI().setIntentionActive();}
 static void act(Guardian g,long now){
  if(g.isAlikeDead()||now<g.holdingUntil||g.isControlBlocked())return;
  Creature target=choose(g);
  if(target!=null){g.returning=false;if(g.focus!=target){clear(g);g.focus=target;g.addDamageHate(target,0,100);}
   g.setRunning();g.setTarget(target);if(!g.isCastingNow()&&(g.getAI().getIntention()!=Intention.ATTACK||g.getAI().getAttackTarget()!=target))g.getAI().setIntentionAttack(target);return;}
  if(g.focus!=null||g.getAI().getIntention()==Intention.ATTACK||g.isCastingNow())clear(g);
  if(g.returning){Location post=post(g);if(g.calculateDistance3D(post)>80){g.setRunning();move(g,post,now);return;}g.returning=false;g.patrolIndex=0;}
  g.setWalking();List<Location> route=route(g);Location next=route.get(g.patrolIndex%route.size());next=SiegeAgenda.safe(next.getX(),next.getY(),next.getZ());
  if(g.calculateDistance3D(next)<=40){if(g.pauseUntil==0){g.patrolArrivals++;g.pauseUntil=now+1000+(g.getId()==903201?1000:0);g.getAI().setIntentionActive();}else if(now>=g.pauseUntil){g.pauseUntil=0;g.patrolIndex=(g.patrolIndex+1)%route.size();g.destination=null;}return;}
  if(now>=g.pauseUntil)move(g,next,now);
 }
 private static void move(Guardian g,Location next,long now){if(g.isMovementDisabled()||g.isCastingNow())return;
  if(g.destination==null||Math.hypot(g.destination.getX()-next.getX(),g.destination.getY()-next.getY())>20||Math.abs(g.destination.getZ()-next.getZ())>20||!g.isMoving()&&now-g.lastMove>=3000){g.destination=next;g.lastMove=now;g.getAI().setIntentionMoveTo(next);}}
 static void fight(Guardian g,long now){
  Creature t=g.getAI().getAttackTarget();if(g.isAlikeDead()||g.isCastingNow()||g.isControlBlocked()||g.isAllSkillsDisabled()||GiranGuardians.instance.verificationPaused)return;
  if(!engageable(g,t)){clear(g);g.returning=true;return;}
  g.focus=t;g.setTarget(t);g.setRunning();
  if(g.getId()==903200){if(now>=g.nextSkill){if(self(g,78,t,now))return;for(int id:new int[]{261,1,6})if(cast(g,id,t,now)){g.nextSkill=now+3000;return;}}
   if(g.isAttackDisabled())return;double range=g.getPhysicalAttackRange()+g.getTemplate().getCollisionRadius()+t.getTemplate().getCollisionRadius();
   if(g.calculateDistance2D(t)>range){g.getAI().moveToPawn(t,(int)range);return;}g.doAttack(t);
  }else {
   if(self(g,337,t,now))return;
   for(int id:new int[]{1064,1074,1341,1291,1239})if((id!=1064&&id!=1074&&id!=1341||!t.isAffectedBySkill(id))&&cast(g,id,t,now))return;
   if(g.calculateDistance2D(t)>550&&!g.isMovementDisabled())g.getAI().moveToPawn(t,550);
  }
 }
 private static boolean self(Guardian g,int id,Creature target,long now){if(g.isAffectedBySkill(id))return false;Skill skill=g.getKnownSkill(id);if(!available(g,skill))return false;
  g.stopMove(null);g.setTarget(g);g.doCast(skill);g.setTarget(target);if(g.isCastingNow()){g.lastSkill=id;g.casts++;return true;}return false;}
 private static boolean available(Guardian g,Skill s){return s!=null&&!g.isSkillDisabled(s)&&g.getCurrentMp()>=s.getMpConsume()+s.getMpInitialConsume()
  &&g.getCurrentHp()>s.getHpConsume()&&(!s.isMagic()||!g.isMuted())&&(s.isMagic()||!g.isPhysicalMuted());}
 private static boolean cast(Guardian g,int id,Creature t,long now){Skill s=g.getKnownSkill(id);if(!available(g,s)||g.calculateDistance2D(t)>Math.max(40,s.getCastRange()<0?s.getAffectRange():s.getCastRange())+30)return false;
  g.stopMove(null);g.setTarget(t);g.doCast(s);if(g.isCastingNow()){g.lastSkill=id;g.casts++;return true;}return false;}
}
