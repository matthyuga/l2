package custom.GiranSiegeLab;

import java.sql.*;
import java.util.*;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.ai.CreatureAI;
import org.l2jmobius.gameserver.data.sql.ClanTable;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.mechanics.script.Script;
import custom.NormalNpcRoster.NormalNpcRoster;
import custom.SoloArenaGauntlet.SoloArenaGauntlet;
import custom.AmberContract.*;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Owned-castle native checks. Starts/aborts engraving; never completes or transfers ownership. */
public class GiranDefenseVerification extends Script {
 private static final Logger LOG=Logger.getLogger(GiranDefenseVerification.class.getName());
 private final List<Squad> squads=new ArrayList<>();private int checks,waits;private boolean claimed,started;private long date,regEnd;private boolean regOver;private int owner;private final Map<Integer,Integer> rep=new HashMap<>(),blood=new HashMap<>();private Player scout;
 public GiranDefenseVerification(){if(Boolean.getBoolean("lab.giran.v3.verify"))ThreadPool.schedule(this::ready,40000);}
 private void check(boolean ok,String why){if(!ok)throw new IllegalStateException(why);checks++;}
 private void ready(){if(!NormalNpcRoster.isReady()){if(++waits<110)ThreadPool.schedule(this::ready,3000);else LOG.severe("GIRAN_V3_VERIFY FAILED readiness");return;}ThreadPool.execute(this::verify);}
 private void waitFor(java.util.function.BooleanSupplier condition,String why)throws Exception{long end=System.currentTimeMillis()+12000;while(!condition.getAsBoolean()&&System.currentTimeMillis()<end){check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"Human must stay disconnected");Thread.sleep(100);}check(condition.getAsBoolean(),why);}
 private void verify(){synchronized(GiranSiegeLab.instance){Throwable error=null;Monster farm=null;try{
  check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"No human loaded");var c=GiranRules.castle();owner=c.getOwnerId();check(owner==ClanTable.getInstance().getClanByName("Hellsing").getId()&&!c.getSiege().isInProgress(),"Hellsing owns Giran, idle");date=c.getSiegeDate().getTimeInMillis();regOver=c.isTimeRegistrationOver();
  try(Connection con=DatabaseFactory.getConnection();Statement st=con.createStatement();var rs=st.executeQuery("SELECT regTimeEnd FROM castle WHERE id=3")){check(rs.next(),"Castle row");regEnd=rs.getLong(1);}
  for(String name:GiranRoster.CLANS){var clan=ClanTable.getInstance().getClanByName(name);rep.put(clan.getId(),clan.getReputationScore());blood.put(clan.getId(),clan.getBloodAllianceCount());}
  GiranRoster.registerAll();check(SoloArenaGauntlet.tryClaimPilot(),"Pilot lock");claimed=true;
  for(int t=0;t<5;t++){Squad s=new Squad(t);squads.add(s);for(int i=t==0?1:0;i<4;i++){Player p=GiranRoster.load(GiranRoster.NAMES[t][i]);Pilot a=new Pilot(p,s,i,GiranRoster.ROLES[t][i],true);s.members.add(a);p.setLabControlled(true);p.setOnlineStatus(true,true);p.setEnteredWorld();GiranSiegeLab.reset(a);p.setInvul(true);}
   Player leader=s.members.get(0).p;Party party=new Party(leader,PartyDistributionType.FINDERS_KEEPERS);leader.setParty(party);for(int i=1;i<s.members.size();i++)s.members.get(i).p.joinParty(party);
  }
  c.getSiege().startSiege();started=c.getSiege().isInProgress();check(started,"Native owned siege started");c.setFirstMidVictory(true);
  for(Squad s:squads)for(Pilot a:s.members){GiranSiegeLab.move(a.p,GiranSiegeLab.camp(s.id,a.slot));check(a.p.getSiegeState()==(s.id==0?2:1),"Correct native side "+a.p.getName());check(a.p.getLevel()==80&&a.p.getInventory().getInventoryItemCount(2131,-1)>=1200,"Lab80/Gemstone stock");}
  Player defender=squads.get(0).members.get(0).p;Player leader=squads.get(1).members.get(0).p;Player rival=squads.get(2).members.get(0).p;
  check(!leader.isSiegeFriend(rival),"Competing attackers are native enemies");check(GiranRules.hostile(leader,rival),"Competing clans legal target");check(!GiranRules.hostile(leader,squads.get(1).members.get(1).p),"Own squad protected");
  GiranGuardians.instance.ensure();check(GiranGuardians.instance.actors.size()==2,"Exactly two persistent guardians");
  for(var guardian:GiranGuardians.instance.actors){check(guardian.getCurrentHp()>10000,"Guardian starts with restored native HP");check(!guardian.isAutoAttackable(defender)&&guardian.isAutoAttackable(leader),"Guardian current owner allegiance");}
  // All four rival leaders have a real capture skill; start actual channel and abort before completion.
  Creature artifact=c.getArtefacts().iterator().next();Location stand=SiegeAgenda.sealPosition(artifact);check(stand.getZ()>=artifact.getZ()&&stand.getZ()-artifact.getZ()<=45,"Walkable native engraving height");
  for(int t=1;t<5;t++){Pilot a=squads.get(t).members.get(0);Player p=a.p;p.setInvul(false);GiranSiegeLab.move(p,stand);p.fullRestore();check(p.isClanLeader()&&p.getKnownSkill(246)!=null,"Rival leader has native Seal");p.setTarget(artifact);check(p.getKnownSkill(246).checkCondition(p,artifact,false),"Native capture condition "+p.getName());check(p.useMagic(p.getKnownSkill(246),true,true),"Real180s native capture channel starts "+p.getName());Thread.sleep(150);check(p.isCastingNow(),"Capture channel active");p.abortCast();p.setInvul(true);GiranSiegeLab.move(p,GiranSiegeLab.camp(t,a.slot));}
  // Guardian corpse survives until revival; native room spawn and holding phase are used.
  var guardian=GiranGuardians.instance.actors.get(0);guardian.doDie(leader);check(guardian.isDead(),"Guardian native death");guardian.revive(false);check(!guardian.isDead(),"Manual guardian revival");guardian.doDie(leader);guardian.deadAt=System.currentTimeMillis()-61000;waitFor(()->!guardian.isDead(),"Automatic guardian revival after timer");check(guardian.holdingUntil>System.currentTimeMillis()&&guardian.calculateDistance2D(guardian.home)>100,"Revived guardian waits in residence resurrection room");guardian.holdingUntil=System.currentTimeMillis()-1;
  check(c.getOwnerId()==owner,"No conquest completed or owner changed by test");
  // Real native bow damage, autonomous selection, owner target unset.
  scout=squads.get(3).members.get(0).p;scout.setInvul(false);Door gate=c.getDoors().stream().filter(d->d.getId()==23220001).findFirst().orElseThrow();Location west=SiegeAgenda.safe(gate.getX()-600,144790,-2832);GiranSiegeLab.move(scout,west);
  AmberServitor amber=AmberScoutVerificationBridge.build(scout);check(AmberScoutVerificationBridge.eligible(amber,gate),"Door enters autonomous scan");scout.setTarget(gate);check(amber.canAttack(false),"Manual bow command accepts legal siege gate");scout.setTarget(null);double hp=gate.getCurrentHp();AmberScoutVerificationBridge.enable(amber,true);check(AmberScoutVerificationBridge.enabled(amber),"Native assistance toggle enabled");waitFor(()->gate.getCurrentHp()<hp,"Autonomous Amber damages gate without owner target");
  check(scout.getTarget()==null&&AmberScoutVerificationBridge.enabled(amber),"Owner target/toggle preserved");AmberScoutVerificationBridge.enable(amber,false);amber.abortAttack();
  // Field farming while the owner moves: ordinary Attackable, no handcrafted damage.
  Location field=SiegeAgenda.safe(109500,144450,-2832);GiranSiegeLab.move(scout,field);amber.teleToLocation(field.getX()+35,field.getY()+35,field.getZ(),0,0,false);
  farm=new Monster(NpcData.getInstance().getTemplate(903200));farm.fullRestore();farm.setScriptValue(1);farm.setAI(new CreatureAI(farm));Location mob=SiegeAgenda.safe(field.getX()+400,field.getY(),field.getZ());farm.spawnMe(mob.getX(),mob.getY(),mob.getZ());farm.setInvul(false);final Monster target=farm;waitFor(()->AmberScoutVerificationBridge.eligible(amber,target),"Attackable field NPC scanned: "+AmberScoutVerificationBridge.explain(amber,target));double before=target.getCurrentHp();check(before>1000,"Field NPC has fully initialized native HP");AmberScoutVerificationBridge.enable(amber,true);scout.getAI().setIntentionMoveTo(SiegeAgenda.safe(field.getX()+250,field.getY()+100,field.getZ()));ThreadPool.schedule(()->{if(target.getCurrentHp()>=before)LOG.info("AMBER_SCOUT_DIAG "+AmberScoutVerificationBridge.explain(amber,target)+AmberScoutVerificationBridge.timing(amber));},5000);waitFor(()->target.getCurrentHp()<before,"Amber attacks field perimeter while owner walks");double firstHp=target.getCurrentHp();waitFor(()->target.getCurrentHp()<firstHp,"Native autonomous second arrow lands");check(AmberScoutVerificationBridge.enabled(amber)&&scout.getTarget()==null,"Farming remains autonomous");AmberScoutVerificationBridge.cleanup(scout);scout=null;farm.deleteMe();farm=null;

 }catch(Throwable e){error=e;}finally{
  try{if(scout!=null)AmberScoutVerificationBridge.cleanup(scout);if(farm!=null)farm.deleteMe();for(Squad s:squads)for(Pilot a:s.members){a.p.abortAttack();a.p.abortCast();if(a.p.hasSummon())a.p.getSummon().unSummon(a.p);if(a.p.isInParty())a.p.leaveParty();}
   var c=GiranRules.castle();if(started)c.getSiege().endSiege();for(Squad s:squads)for(Pilot a:s.members){a.p.setInvul(a.originalInvul);if(a.p.isDead())a.p.doRevive();GiranSiegeLab.restoreExperience(a);GiranSiegeLab.move(a.p,a.origin);a.p.setTitle(a.originalTitle);a.p.storeMe();GiranRoster.dispose(a.p);}
   if(started){c.getSiegeDate().setTimeInMillis(date);c.setTimeRegistrationOver(regOver);c.getTimeRegistrationOverDate().setTimeInMillis(regEnd);c.getSiege().saveSiegeDate();c.getSiege().startAutoTask();for(var row:rep.entrySet()){var clan=ClanTable.getInstance().getClan(row.getKey());clan.addReputationScore(row.getValue()-clan.getReputationScore());var count=clan.getClass().getDeclaredField("_bloodAllianceCount");count.setAccessible(true);count.setInt(clan,blood.get(clan.getId()));clan.updateBloodAllianceCountInDB();}GiranRoster.registerAll();check(c.getOwnerId()==owner&&!c.getSiege().isInProgress(),"Owner/idle restored");}
  }catch(Throwable e){if(error==null)error=e;else error.addSuppressed(e);}finally{if(claimed)SoloArenaGauntlet.releasePilot();}
 }
 if(error==null)LOG.info("GIRAN_V3_VERIFY PASS checks="+checks+";owned siege sides,rivals hostile,Amber native gate damage/perimeter walking,4leaders native Seal channel aborted,guardians friendly/revive/room;human not loaded,owner preserved,19pilots unloaded");else LOG.log(Level.SEVERE,"GIRAN_V3_VERIFY FAILED checks="+checks,error);
 }}
 public static void main(String[] args){new GiranDefenseVerification();}
}
