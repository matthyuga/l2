package custom.GiranSiegeLab;

import java.sql.*;
import java.util.*;
import java.util.logging.*;
import java.util.function.BooleanSupplier;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.ai.*;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import custom.NormalNpcRoster.NormalNpcRoster;
import custom.SoloArenaGauntlet.SoloArenaGauntlet;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Opt-in native two-side smoke. No user is loaded; engraving is never completed. */
final class GiranChaosVerification {
 final GiranChaosSiege scene;int checks;long deadline=System.currentTimeMillis()+600000;
 GiranChaosVerification(GiranChaosSiege scene){this.scene=scene;}
 void whenReady(){if(!NormalNpcRoster.isReady()){if(System.currentTimeMillis()<deadline)ThreadPool.schedule(this::whenReady,3000);else GiranChaosSiege.LOG.severe("GIRAN_CHAOS_VERIFY FAILED readiness");return;}ThreadPool.execute(this::run);}
 void check(boolean ok,String msg){checks++;if(!ok)throw new IllegalStateException(msg);}
 void waitFor(BooleanSupplier condition,String label,long timeout)throws Exception{long end=System.currentTimeMillis()+timeout;while(!condition.getAsBoolean()&&System.currentTimeMillis()<end){check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"Client stays disconnected");Thread.sleep(150);}check(condition.getAsBoolean(),label);}
 void run(){synchronized(scene){Throwable failure=null;var castle=GiranRules.castle();int owner=castle.getOwnerId();long date=castle.getSiegeDate().getTimeInMillis();boolean reg=castle.isTimeRegistrationOver();long end=castle.getTimeRegistrationOverDate().getTimeInMillis();
  Map<Integer,Integer> reputation=new HashMap<>(),blood=new HashMap<>();Map<Npc,CreatureAI> ai=new HashMap<>();Map<Npc,Boolean> invul=new HashMap<>();List<Servitor> machines=new ArrayList<>();
  try{
   check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"No user loaded");
   GiranChaosSiege.setupSides();
   for(String n:GiranRoster.CLANS){var clan=ClanTable.getInstance().getClanByName(n);reputation.put(clan.getId(),clan.getReputationScore());blood.put(clan.getId(),clan.getBloodAllianceCount());}
   var raid=ClanTable.getInstance().getClanByName(GiranChaosSiege.CLAN);reputation.put(raid.getId(),raid.getReputationScore());blood.put(raid.getId(),raid.getBloodAllianceCount());
   check(raid.getCrestId()==0&&raid.getAllyCrestId()==0&&raid.getAllyId()==0&&raid.getMembersCount()==20,"20 crestless attackers");
   scene.prepareTeams(null);check(scene.squads.size()==14,"5 defender and9attacker groups");
   check(scene.squads.stream().flatMap(s->s.members.stream()).count()==39,"Exactly39 bots;human not loaded");
   for(int i=0;i<9;i++){var s=scene.squads.get(i+5);check(s.members.size()==GiranChaosSiege.ATTACK[i].length,"Mixed sizes");for(var a:s.members){check(a.p.isInParty()==(s.members.size()>1),"True solo/party status "+a.p.getName());check(!a.role.contains("SUPPORT")&&!a.role.equals("HEALER")||s.members.size()>1,"Support has companions");}}
   // Preserve native stats/AI; fixtures pause guards only to isolate side and weapon behavior.
   scene.start();GiranGuardians.instance.verificationPaused=true;
   for(WorldObject o:World.getVisibleObjects())if(o instanceof Npc n&&SiegeSquadBrain.GUARDS.contains(n.getId())&&castle.checkIfInZone(n.getX(),n.getY(),n.getZ())){invul.put(n,n.isInvul());n.abortAttack();n.abortCast();n.setInvul(true);if(n instanceof Attackable a)a.clearAggroList();if(!(n instanceof GiranGuardians.Guardian)){ai.put(n,n.getAI());n.getAI().stopAITask();n.setAI(new CreatureAI(n));}}
   List<Pilot> attackers=new ArrayList<>(),defenders=new ArrayList<>();
   for(Squad s:scene.squads)for(Pilot a:s.members){a.p.setInvul(true);a.summonAttempts=2;s.launchAt=0;a.nextThink=0;(s.id>=5?attackers:defenders).add(a);check(a.p.getSiegeState()==(s.id>=5?1:2)&&a.p.getSiegeSide()==3,"Native side marker "+a.p.getName());check(a.p.getLevel()==80&&a.p.getClassIndex()==0&&a.p.getSubClasses().size()==3,"Recipe preserved");}
   check(attackers.size()==20&&defenders.size()==19,"Requested sides");
   for(Pilot a:attackers)for(Pilot b:attackers)check(!SiegeSquadBrain.allowed(a.p,b.p),"Attacker allies protected");
   for(Pilot a:defenders)for(Pilot b:defenders)check(!SiegeSquadBrain.allowed(a.p,b.p),"Defender allies protected");
   var ap=attackers.get(0);var dp=defenders.get(0);GiranSiegeLab.move(ap.p,SiegeAgenda.safe(116650,145095,-2560));GiranSiegeLab.move(dp.p,SiegeAgenda.safe(116760,145095,-2560));ap.p.setInvul(false);dp.p.setInvul(false);
   check(SiegeSquadBrain.allowed(dp.p,ap.p)&&SiegeSquadBrain.allowed(ap.p,dp.p),"Native opposing Players attackable");
   dp.squad.leader=dp.p;scene.agenda.update(dp.squad,scene.routes.get(dp.squad),null,"defensa",System.currentTimeMillis());check(dp.squad.focus==ap.p,"Defender intercepts approaching attacker");
   for(Pilot d:defenders)check(GiranRules.defender(d.p),"All old clan members defenders");
   for(var g:GiranGuardians.instance.actors){check(!GiranGuardianBrain.enemy(g,dp.p)&&GiranGuardianBrain.enemy(g,ap.p),"Guardian allegiance unchanged");}
   double hp=dp.p.getCurrentHp()+dp.p.getCurrentCp();ap.squad.leader=ap.p;ap.squad.focus=dp.p;ap.nextThink=0;SiegeSquadBrain.act(ap,dp.p,"asalto");waitFor(()->{SiegeSquadBrain.act(ap,dp.p,"asalto");return dp.p.getCurrentHp()+dp.p.getCurrentCp()<hp;},"Real Player PvP HP/CP damage",12000);ap.p.abortAttack();ap.p.abortCast();ap.p.getAI().setIntentionIdle();ap.p.setInvul(true);dp.p.setInvul(true);
   // Actual native curative skill: HP is the fixture stimulus, recovery must come from the cast.
   Pilot healer=attackers.stream().filter(a->a.p.getName().equals("ArenaNerys")).findFirst().orElseThrow();Pilot patient=healer.squad.members.get(0);GiranSiegeLab.move(healer.p,SiegeAgenda.safe(116500,145095,-2560));GiranSiegeLab.move(patient.p,SiegeAgenda.safe(116550,145095,-2560));patient.p.setInvul(false);patient.p.setCurrentHp(patient.p.getMaxHp()*.35);double hurt=patient.p.getCurrentHp();patient.p.getStatus().stopHpMpRegeneration();healer.nextThink=0;healer.squad.leader=patient.p;healer.squad.focus=null;SiegeSquadBrain.act(healer,dp.p,"asalto");check(healer.reuse.containsKey(1401)||healer.reuse.containsKey(1218)||healer.reuse.containsKey(1217),"Native healing skill requested");waitFor(()->patient.p.getCurrentHp()>hurt+500,"Native support healing",12000);healer.p.abortCast();patient.p.fullRestore();patient.p.setInvul(true);GiranChaosSiege.LOG.info("GIRAN_CHAOS_VERIFY STAGE PASS: native PvP HP/CP damage and healing");
   // Route randomness is observable on independent leaders, bounded to the actual hall.
   Set<String> destinations=new HashSet<>();for(Squad s:scene.squads)if(s.id>=5&&!s.leader.isClanLeader()){GiranSiegeLab.move(s.leader,SiegeAgenda.safe(116650,145095,-2560));var r=scene.routes.get(s);for(int k=0;k<8;k++){r.nextChoice=0;r.destination=null;scene.agenda.update(s,r,null,"defensa",System.currentTimeMillis()+2000);check(r.destination!=null&&r.destination.getX()>115450,"Interior random stage");destinations.add(r.destination.getX()+":"+r.destination.getY());}}
   check(destinations.size()>12,"Diverse independent destinations");GiranChaosSiege.LOG.info("GIRAN_CHAOS_VERIFY STAGE PASS: independent random destinations="+destinations.size());
   for(Squad s:scene.squads)for(Pilot a:s.members){a.p.abortAttack();a.p.abortCast();a.p.getAI().setIntentionIdle();GiranSiegeLab.move(a.p,scene.spawnPoint(a.p,s.id,a.slot));}
   scene.machines.deploy(scene.squads);
   Pilot dwarf=attackers.stream().filter(a->a.p.getName().equals("ArenaDagna")).findFirst().orElseThrow(),cannonOwner=attackers.stream().filter(a->a.p.getName().equals("ArenaBorin")).findFirst().orElseThrow();
   check(dwarf.p.hasSummon()&&dwarf.p.getSummon().getId()==14737,"One native Siege Golem");check(cannonOwner.p.hasSummon()&&cannonOwner.p.getSummon().getId()==14768,"One native Wild Hog Cannon");
   check(dwarf.p.getKnownSkill(13)==null&&cannonOwner.p.getKnownSkill(299)==null,"No new learned skills/build edits");machines.add(dwarf.p.getSummon().asServitor());machines.add(cannonOwner.p.getSummon().asServitor());
   Door gate=GiranChaosAgenda.door(23220001);check(gate!=null&&!gate.isDead(),"Native gate present");
   GiranSiegeLab.move(cannonOwner.p,SiegeAgenda.safe(112200,144790,-2832));cannonOwner.p.getSummon().teleToLocation(112200,144790,-2832,0,0,false);cannonOwner.p.getSummon().setInvul(true);double gateHp=gate.getCurrentHp();scene.machines.act(scene.squads);waitFor(()->gate.getCurrentHp()<gateHp,"Actual cannon damages native gate",18000);check(scene.machines.casts>0,"Native cannon skill used");cannonOwner.p.getSummon().abortCast();GiranChaosSiege.LOG.info("GIRAN_CHAOS_VERIFY STAGE PASS: cannon gate damage");
   Door south=GiranChaosAgenda.door(23220002);GiranSiegeLab.move(dwarf.p,SiegeAgenda.safe(112750,144950,-2832));dwarf.p.getSummon().teleToLocation(112750,144950,-2832,0,0,false);dwarf.p.getSummon().setInvul(true);double southHp=south.getCurrentHp();scene.machines.act(scene.squads);waitFor(()->south.getCurrentHp()<southHp,"Actual golem attacks gate",18000);dwarf.p.getSummon().abortAttack();GiranChaosSiege.LOG.info("GIRAN_CHAOS_VERIFY STAGE PASS: golem gate damage");
   // Native movement, no teleport after each fixture's start position.
   Pilot solo=attackers.stream().filter(a->a.p.getName().equals("ArenaRhogar")).findFirst().orElseThrow();GiranSiegeLab.move(solo.p,SiegeAgenda.safe(116200,145095,-2560));Location before=new Location(solo.p);solo.squad.focus=null;solo.squad.leader=solo.p;solo.squad.goal=SiegeAgenda.safe(116650,145095,-2560);solo.nextThink=0;SiegeSquadBrain.act(solo,dp.p,"asalto");waitFor(()->solo.p.calculateDistance2D(before)>100,"Solo moves through native AI",12000);solo.p.getAI().setIntentionIdle();
   check(castle.getOwnerId()==owner,"Conquest not completed");check(GiranGuardians.instance.actors.size()==2,"Exactly Ares and Nyx retained");
  }catch(Throwable e){failure=e;}finally{
   try{scene.finish(true);GiranGuardians.instance.verificationPaused=false;
    for(var entry:invul.entrySet())if(entry.getKey().isSpawned())entry.getKey().setInvul(entry.getValue());for(var entry:ai.entrySet())if(entry.getKey().isSpawned()){entry.getKey().setAI(entry.getValue());entry.getKey().getAI().setIntentionActive();}
    castle.getSiegeDate().setTimeInMillis(date);castle.setTimeRegistrationOver(reg);castle.getTimeRegistrationOverDate().setTimeInMillis(end);castle.getSiege().saveSiegeDate();castle.getSiege().startAutoTask();
    for(int id:reputation.keySet()){var c=ClanTable.getInstance().getClan(id);c.addReputationScore(reputation.get(id)-c.getReputationScore());var f=c.getClass().getDeclaredField("_bloodAllianceCount");f.setAccessible(true);f.setInt(c,blood.get(id));c.updateBloodAllianceCountInDB();}
    GiranChaosSiege.setupSides();check(castle.getOwnerId()==owner&&!castle.getSiege().isInProgress(),"Owner and idle state preserved");check(machines.stream().noneMatch(Creature::isSpawned),"Both machines removed");check(World.getPlayers().stream().noneMatch(p->GiranChaosSiege.attackers().contains(p.getName().replace("Arena",""))),"Attacker Players unloaded");check(SoloArenaGauntlet.tryClaimPilot(),"Lock released");SoloArenaGauntlet.releasePilot();
   }catch(Throwable e){if(failure==null)failure=e;else failure.addSuppressed(e);}
  }
  if(failure==null)GiranChaosSiege.LOG.info("GIRAN_CHAOS_VERIFY PASS checks="+checks+";39 real pilots,20vs19,6 parties+3 solos,native side flags,crestless clan,guardian allegiance,PvP damage,healing,random destinations,native golem/cannon gate damage,movement,cleanup;no human loaded or conquest completed");else GiranChaosSiege.LOG.log(Level.SEVERE,"GIRAN_CHAOS_VERIFY FAILED checks="+checks,failure);
 }}
}
