package custom.GiranSiegeLab;

import java.util.*;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.Door;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Explicit lab deployment through native Summon effects. No learned-skill or build changes. */
final class GiranChaosMachinery {
 final Set<Integer> deployed=new HashSet<>();int casts;
 static boolean machine(Summon pet){return pet!=null&&(pet.getId()==14737||pet.getId()==14768);}
 void clear(){deployed.clear();casts=0;}
 void deploy(List<Squad> squads){for(Squad s:squads)for(Pilot a:s.members){
  Player p=a.p;boolean golem=p.getName().equals("ArenaDagna"),cannon=p.getName().equals("ArenaBorin");
  if(!golem&&!cannon||deployed.contains(p.getObjectId())||p.isDead()||p.hasSummon())continue;
  int id=golem?13:299;var skill=SkillData.getInstance().getSkill(id,1);int item=golem?1459:1460,count=golem?300:120;
  GiranSiegeLab.supply(p,item,count);GiranSiegeLab.supply(p,golem?2131:2132,golem?8400:3600);
  if(!skill.checkCondition(p,p,false)||p.getCurrentMp()<skill.getMpInitialConsume())continue;
  if(p.getInventory().destroyItemByItemId(ItemProcessType.NONE,item,count,p,null)==null)continue;
  p.setCurrentMp(p.getCurrentMp()-skill.getMpInitialConsume());skill.applyEffects(p,p);
  if(machine(p.getSummon())){deployed.add(p.getObjectId());a.summonAttempts=2;GiranChaosSiege.LOG.info("GIRAN_CHAOS MACHINE deployed: "+p.getSummon().getName()+" owner="+p.getName()+";native Summon effect,materials,MP and upkeep;recipe unchanged");}
 }}
 void act(List<Squad> squads){deploy(squads);for(Squad s:squads)for(Pilot a:s.members){
  Player owner=a.p;Summon pet=owner.getSummon();if(!machine(pet)||pet.isDead()||owner.isDead())continue;
  Door target=GiranRules.castle().getDoors().stream().filter(d->GiranRules.doorAllowed(owner,d)&&pet.calculateDistance2D(d)<2500&&GeoEngine.getInstance().canSeeTarget(pet,d)).min(Comparator.comparingDouble(pet::calculateDistance2D)).orElse(null);
  if(target==null){pet.abortAttack();if(!pet.isCastingNow())pet.setFollowStatus(true);continue;}
  pet.setFollowStatus(false);pet.setTarget(target);
  // Summon commands require an A* path to the door's raised, closed center.
  // Siege weapons instead approach the accessible face and use native cast/attack execution.
  if(pet.getId()==14768){var shot=pet.getKnownSkill(4230);if(shot!=null&&!pet.isCastingNow()&&!pet.isSkillDisabled(shot)&&shot.checkCondition(pet,target,false)&&pet.getCurrentMp()>=shot.getMpConsume()+shot.getMpInitialConsume()){
   owner.setCurrentPetSkill(shot,true,true);pet.getAI().setIntentionIdle();pet.setTarget(target);pet.doCast(shot);if(pet.isCastingNow()){casts++;if(casts==1)GiranChaosSiege.LOG.info("GIRAN_CHAOS CANNON native cast started gate="+target.getId());}
  }}else{
   int reach=pet.getPhysicalAttackRange()+pet.getTemplate().getCollisionRadius()+target.getTemplate().getCollisionRadius();
   if(pet.calculateDistance2D(target)>reach){var face=SiegeAgenda.safe(target.getX()-85,target.getY(),pet.getZ());pet.setRunning();if(pet.getAI().getIntention()!=Intention.MOVE_TO||Math.hypot(pet.getXdestination()-face.getX(),pet.getYdestination()-face.getY())>32)pet.getAI().setIntentionMoveTo(face);}
   else if(!pet.isAttackingNow()&&!pet.isCastingNow()&&!pet.isOutOfControl()){pet.getAI().setIntentionIdle();pet.doAttack(target);}
  }
 }}
}
