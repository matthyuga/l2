package custom.GiranSiegeLab;

import java.nio.file.*;
import java.util.*;
import java.util.function.*;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.geoengine.pathfinding.PathFinding;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Real Player targets, skills and damage. Temporary fixtures never load Hellkevin or complete conquest. */
final class GiranTacticsVerification {
 private static final Logger LOG=Logger.getLogger(GiranTacticsVerification.class.getName());
 @FunctionalInterface interface Wait {void until(BooleanSupplier condition,String why,long timeout)throws Exception;}
 static void run(List<Squad> squads,BiConsumer<Boolean,String> check,Wait wait)throws Exception {
  Player defender=squads.get(0).members.get(0).p;var c=GiranRules.castle();
  try {
   parkAll(squads);SiegeTactics.reset();
   GiranThroneServices.instance.ensure();check.accept(GiranThroneServices.instance.actors.size()==2,"Two additional throne services");
   for(Npc npc:GiranThroneServices.instance.actors){check.accept(npc.getId()==50010?npc instanceof Merchant:npc instanceof SchemeBuffer,"Native service handler "+npc.getName());
    check.accept(c.checkIfInZone(npc.getX(),npc.getY(),npc.getZ())&&SiegeAgenda.open(npc.getX(),npc.getY(),npc.getZ()),"Service on walkable castle floor "+npc.getName());
    check.accept(Files.exists(Path.of(npc.getHtmlPath(npc.getId(),0))),"Original service menu exists "+npc.getName());
    long originals=World.getVisibleObjects().stream().filter(o->o instanceof Npc n&&n.getId()==npc.getId()&&n.calculateDistance2D(148900,46700,-3400)<300).count();check.accept(originals==1,"Original Coliseum service remains "+npc.getName());
    Location hall=SiegeAgenda.safe(116650,145095,-2560);GiranSiegeLab.move(defender,hall);defender.getAI().setIntentionMoveTo(new Location(npc));
    wait.until(()->defender.calculateDistance2D(npc)<100&&Math.abs(defender.getZ()-npc.getZ())<=40,"Walk to throne service "+npc.getName(),15000);defender.getAI().setIntentionIdle();
   }
   GiranSiegeLab.move(defender,GiranSiegeLab.camp(0,0));LOG.info("GIRAN_V8_SERVICES_PASS native shop/buffer menus,walking access,original Coliseum instances preserved");
   // Every rival pilot must fight a defender rather than keep running, including all four captors.
   int fought=0;for(int team=1;team<5;team++){Squad s=squads.get(team);s.leader=s.members.get(0).p;s.conquest=true;s.launchAt=0;s.goal=SiegeAgenda.safe(117880,145064,-2528);
    for(Pilot a:s.members){parkAll(squads);SiegeTactics.reset();s.leader=s.members.get(0).p;s.conquest=true;s.launchAt=0;
     ready(a);Location combat=SiegeAgenda.safe(116500,145095,-2560);GiranSiegeLab.move(a.p,combat);
     if(a.p!=s.leader)GiranSiegeLab.move(s.leader,SiegeAgenda.safe(117880,145064,-2528));
     Pilot victim=squads.get(0).members.get(0);ready(victim);GiranSiegeLab.move(defender,SiegeAgenda.safe(116680,145095,-2560));
     check.accept(a.p==s.leader||a.p.calculateDistance2D(s.leader)>1200,"Escort fixture beyond old leash "+a.p.getName());
     double hp=defender.getCurrentHp();a.nextThink=0;SiegeSquadBrain.act(a,defender,"asalto");
     if(a.p.getTarget()!=defender)LOG.info("GIRAN_V8_PILOT_DIAG "+a.p.getName()+" role="+a.role+" ai="+a.p.getAI().getIntention()+" target="+a.p.getTarget()+" attack="+a.p.getAI().getAttackTarget()+" cast="+a.p.getAI().getCastTarget()+" casting="+a.p.isCastingNow()+" control="+a.p.isControlBlocked()+" local="+SiegeTactics.localTarget(a)+" allowed="+SiegeSquadBrain.allowed(defender,a.p)+" LOS="+GeoEngine.getInstance().canSeeTarget(a.p,defender));
     wait.until(()->{a.p.fullRestore();SiegeSquadBrain.act(a,defender,"asalto");return defender.getCurrentHp()<hp;},"Real damage by threat-aware pilot "+a.p.getName(),18000);
     fought++;a.p.abortAttack();a.p.abortCast();a.p.getAI().setIntentionIdle();defender.abortAttack();defender.getAI().setIntentionIdle();
    }
   }
   check.accept(fought==16,"All sixteen attacking pilots fight");LOG.info("GIRAN_V8_COMBAT_PASS all16attackingPlayers including4captors;native damage;escorts beyond old1200leash");
   parkAll(squads);SiegeTactics.reset();Squad first=squads.get(1),second=squads.get(2);pressure(first,second,squads.get(0));
   check.accept(first.tactics.pressured&&SiegeTactics.truce(first.leader,second.leader)&&SiegeTactics.truce(second.leader,first.leader),"Unfavorable defense creates bilateral truce");
   check.accept(GiranRules.hostile(first.leader,second.leader)&&!GiranOrders.allied(first.leader,second.leader),"Tactical truce preserves native clans/enemy legality");
   for(Pilot a:first.members)check.accept(!SiegeTactics.engage(a,second.leader,System.currentTimeMillis()),"All first-party roles honor ceasefire "+a.role);
   for(Pilot a:second.members)check.accept(!SiegeTactics.engage(a,first.leader,System.currentTimeMillis()),"All second-party roles honor ceasefire "+a.role);
   check.accept(SiegeTactics.engage(first.members.get(1),defender,System.currentTimeMillis()),"Truce never protects castle defender");
   Creature artifact=c.getArtefacts().iterator().next();GiranSiegeLab.move(second.leader,SiegeAgenda.sealPosition(artifact));second.leader.setTarget(artifact);
   check.accept(second.leader.useMagic(second.leader.getKnownSkill(246),true,true)&&SiegeAgenda.engraving(second.leader),"Actual rival starts native capture");
   check.accept(!SiegeTactics.truce(first.leader,second.leader)&&SiegeTactics.engage(first.members.get(1),second.leader,System.currentTimeMillis()),"Conquest ends armistice and allows interruption");second.leader.abortCast();second.leader.getAI().setIntentionIdle();
   parkAll(squads);SiegeTactics.reset();first=squads.get(3);second=squads.get(4);pressure(first,second,squads.get(0));
   check.accept(SiegeTactics.truce(first.leader,second.leader),"Second native pair accepts pressure truce");
   final Squad expiryFirst=first,expirySecond=second;parkAll(squads);SiegeTactics.update(first);SiegeTactics.update(second);
   wait.until(()->{SiegeTactics.update(expiryFirst);SiegeTactics.update(expirySecond);return !SiegeTactics.truce(expiryFirst.leader,expirySecond.leader);},"Truce naturally expires when defender pressure is gone",26000);
   SiegeTactics.reset();pressure(first,second,squads.get(0));check.accept(SiegeTactics.truce(first.leader,second.leader),"Truce available again for betrayal test");
   second.members.get(1).p.getAI().setIntentionAttack(first.leader);check.accept(!SiegeTactics.truce(first.leader,second.leader),"Observable attack on truce partner breaks agreement");
   LOG.info("GIRAN_V8_TRUCES_PASS mutual pressure agreement;all8roles honor;no clan/alliance mutation;capture,betrayal and actual20s expiry break truce");
   // A commander waits for his fighting escort, and resumes the actual native capture when the area clears.
   parkAll(squads);SiegeTactics.reset();Squad s=squads.get(1);Pilot leader=s.members.get(0),escort=s.members.get(1);ready(leader);ready(escort);ready(squads.get(0).members.get(0));s.leader=leader.p;s.conquest=true;s.goal=SiegeAgenda.sealPosition(artifact);
   GiranSiegeLab.move(leader.p,SiegeAgenda.safe(117544,145064,-2640));GiranSiegeLab.move(escort.p,SiegeAgenda.safe(116650,145095,-2560));GiranSiegeLab.move(defender,SiegeAgenda.safe(116450,145095,-2560));escort.p.getAI().setIntentionAttack(defender);
   check.accept(SiegeTactics.escortBusy(s),"Nearby escort is actually fighting castle defender");leader.p.getAI().setIntentionMoveTo(s.goal);leader.nextThink=0;SiegeSquadBrain.act(leader,defender,"asalto");
   check.accept(leader.p.getAI().getIntention()!=Intention.MOVE_TO||leader.p.getTarget()==defender,"Captor waits or fights instead of abandoning escort");
   escort.p.abortAttack();escort.p.getAI().setIntentionIdle();GiranSiegeLab.move(defender,GiranSiegeLab.camp(0,0));for(int i=1;i<s.members.size();i++)GiranSiegeLab.move(s.members.get(i).p,GiranSiegeLab.camp(1,i));
   GiranSiegeLab.move(leader.p,SiegeAgenda.sealPosition(artifact));leader.nextThink=0;leader.p.fullRestore();SiegeSquadBrain.act(leader,defender,"asalto");
   check.accept(SiegeAgenda.engraving(leader.p),"Cleared sector resumes native three-minute conquest");leader.p.abortCast();
   LOG.info("GIRAN_V8_COORDINATION_PASS captain waits for combat and resumes native engraving after clearance");
  }finally {parkAll(squads);SiegeTactics.reset();}
 }
 private static void ready(Pilot a){GiranSiegeLab.reset(a);a.p.getAI().setIntentionIdle();a.p.setInvul(false);a.nextThink=0;a.nextHeadquarters=Long.MAX_VALUE;a.pendingSummon=Long.MAX_VALUE;a.summonAttempts=2;a.squad.launchAt=0;}
 private static void parkAll(List<Squad> squads){for(Squad s:squads)for(Pilot a:s.members){a.p.abortAttack();a.p.abortCast();a.p.getAI().setIntentionIdle();a.p.fullRestore();a.p.setInvul(true);a.pursuit=null;GiranSiegeLab.move(a.p,GiranSiegeLab.camp(s.id,a.slot));}}
 private static void pressure(Squad a,Squad b,Squad defense){for(Squad s:List.of(a,b)){s.leader=s.members.get(0).p;int i=0;for(Pilot p:s.members){ready(p);GiranSiegeLab.move(p.p,SiegeAgenda.safe(116500+(s==a?0:300),144950+i++*90,-2560));p.p.setCurrentHp(p.p.getMaxHp()*.35);}}
  int i=0;for(Pilot p:defense.members){ready(p);GiranSiegeLab.move(p.p,SiegeAgenda.safe(116950,144950+i++*100,-2560));}a.tactics.assessAt=0;b.tactics.assessAt=0;SiegeTactics.update(a);SiegeTactics.update(b);SiegeTactics.update(a);}
}
