package custom.GiranSiegeLab;

import java.sql.*;
import java.util.*;
import java.util.concurrent.ScheduledFuture;
import java.util.logging.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.Door;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.entity.spawns.Spawn;
import org.l2jmobius.gameserver.geoengine.pathfinding.PathFinding;
import org.l2jmobius.gameserver.managers.CastleManager;
import org.l2jmobius.gameserver.mechanics.script.Script;
import custom.NormalNpcRoster.NormalNpcRoster;
import custom.SoloArenaGauntlet.SoloArenaGauntlet;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Opt-in native smoke test. Only reserved pilots; never loads the operator or casts conquest. */
public class GiranAgendaVerification extends Script {
 private static final Logger LOG=Logger.getLogger(GiranAgendaVerification.class.getName());
 private final List<Squad> squads=new ArrayList<>();private final List<Spawn> bosses=new ArrayList<>();
 private final SiegeAgenda agenda=new SiegeAgenda();private final Map<Creature,Double> health=new IdentityHashMap<>();
 private ScheduledFuture<?> timer;private int checks,waits,ticks,moved,hits;private boolean claimed,started,opened;private long start,date,regEnd;private boolean regOver;private Player proxy;
 public GiranAgendaVerification(){if(Boolean.getBoolean("lab.giran.v2.verify"))ThreadPool.schedule(this::ready,40000);}
 private void check(boolean ok,String why){if(!ok)throw new IllegalStateException(why);checks++;}
 private boolean humanOnline(){return World.getPlayers().stream().anyMatch(p->p.getClient()!=null);}
 private void ready(){
  if(!NormalNpcRoster.isReady()){if(++waits<110)ThreadPool.schedule(this::ready,3000);else LOG.severe("GIRAN_V2_VERIFY FAILED readiness");return;}
  synchronized(GiranSiegeLab.instance){try{
   check(!humanOnline(),"No human clients during test");var c=CastleManager.getInstance().getCastleById(3);check(c.getOwnerId()==0&&!c.getSiege().isInProgress(),"NPC castle idle");
   date=c.getSiegeDate().getTimeInMillis();regOver=c.isTimeRegistrationOver();
   try(Connection con=DatabaseFactory.getConnection();Statement st=con.createStatement();var rs=st.executeQuery("SELECT regTimeEnd FROM castle WHERE id=3")){check(rs.next(),"Castle row");regEnd=rs.getLong(1);}
   GiranRoster.registerAll();check(SoloArenaGauntlet.tryClaimPilot(),"Exclusive pilot lock");claimed=true;
   for(int t=0;t<5;t++){
    Squad s=new Squad(t);squads.add(s);
    for(int i=t==0?1:0;i<4;i++){Player p=GiranRoster.load(GiranRoster.NAMES[t][i]);Pilot a=new Pilot(p,s,i,GiranRoster.ROLES[t][i],true);s.members.add(a);p.setLabControlled(true);p.setOnlineStatus(true,true);p.setEnteredWorld();if(p.isDead())p.doRevive();GiranSiegeLab.reset(a);p.setInvul(true);
     check(p.getClan().getClanMember(p.getObjectId()).getPlayer()==p,"Native online clan link "+p.getName());}
    Player lead=s.members.get(0).p;Party party=new Party(lead,PartyDistributionType.FINDERS_KEEPERS);lead.setParty(party);for(int i=1;i<s.members.size();i++)s.members.get(i).p.joinParty(party);
   }
   proxy=squads.get(0).members.get(0).p;c.getSiege().startSiege();started=c.getSiege().isInProgress();check(started,"Native siege started");
   for(Squad s:squads)for(Pilot a:s.members){GiranSiegeLab.move(a.p,GiranSiegeLab.camp(s.id,a.slot));a.p.setInvul(true);check(a.p.getSiegeState()==1,"Native attacker flag "+a.p.getName());check(a.p.getParty()!=null,"Native squad party");}
   for(int[] d:new int[][]{{903200,114174,145058,-2752},{903201,117700,145150,-2640}}){Spawn sp=new Spawn(d[0]);Location loc=SiegeAgenda.safe(d[1],d[2],d[3]);sp.setXYZ(loc.getX(),loc.getY(),loc.getZ());sp.setHeading(32768);sp.setRespawnDelay(0);sp.stopRespawn();bosses.add(sp);sp.doSpawn(false).setRunning();}
   // Check every pair in the actual active zone: Amber uses this native friendship rule.
   for(Squad s:squads)for(Pilot a:s.members)for(Squad z:squads)for(Pilot b:z.members)if(a!=b)check(a.p.isSiegeFriend(b.p),"Attacker friendship "+a.p.getName()+" / "+b.p.getName());
   agenda.refresh();
   for(var plan:SiegeAgenda.PLANS)for(var task:plan)if(task.id()>0){Creature target=agenda.find(task);check(target!=null,"Native objective spawned "+task.name());check(SiegeSquadBrain.allowed(target,proxy),"Native objective attackable "+task.name());}
   check(!SiegeSquadBrain.allowed(c.getArtefacts().iterator().next(),proxy),"Artifact excluded from AI");check(!SiegeSquadBrain.allowed(proxy,proxy),"Players excluded from AI");
   var seal=SkillData.getInstance().getSkill(246,1);check(seal.getHitTime()==180000&&seal.getMpConsume()+seal.getMpInitialConsume()==50&&seal.getItemConsumeId()==0,"Native seal:180s50MPnoitem");
   start=System.currentTimeMillis();for(Squad s:squads)s.launchAt=start+s.id*1600L;
   for(WorldObject o:World.getVisibleObjects())if(o instanceof Npc n&&SiegeSquadBrain.GUARDS.contains(n.getId())&&c.checkIfInZone(n.getX(),n.getY(),n.getZ()))health.put(n,n.getCurrentHp());
   for(Door d:c.getDoors())health.put(d,d.getCurrentHp());
   LOG.info("GIRAN_V2_VERIFY SMOKE START 19Players,5parties; test-only invulnerability; outer gates open at35s; no conquest, human not loaded");
   timer=ThreadPool.scheduleAtFixedRate(this::tick,500,500);
  }catch(Throwable e){finish(e);}}
 }
 private void tick(){synchronized(GiranSiegeLab.instance){try{
  check(!humanOnline(),"Human client appeared; stopping isolated test");ticks++;
  if(!opened&&System.currentTimeMillis()-start>35000){opened=true;for(Door d:CastleManager.getInstance().getCastleById(3).getDoors())if(d.getId()==23220001||d.getId()==23220002)d.openMe();LOG.info("GIRAN_V2_VERIFY outer gates opened for route smoke; breach balance not measured");}
  for(Squad s:squads){agenda.update(s,proxy,"asalto");for(Pilot a:s.members){if(a.p.isDead())throw new IllegalStateException("Invulnerable test actor died");SiegeSquadBrain.act(a,proxy,"asalto");}}
  if(System.currentTimeMillis()-start>85000){
   for(Squad s:squads){check(s.leader==s.members.get(0).p,"Local captain "+s.id);for(Pilot a:s.members)if(a.p.calculateDistance2D(GiranSiegeLab.camp(s.id,a.slot))>250)moved++;}
   for(var entry:health.entrySet())if(entry.getKey().isDead()||entry.getKey().getCurrentHp()<entry.getValue()-10)hits++;
   check(moved>=12,"At least12 pilots moved natively, got "+moved);check(hits>0,"Native defenders/doors actually lost HP");
   check(squads.get(1).step>0&&squads.get(2).step>0&&squads.get(3).step>0&&squads.get(4).step>0,"Four agendas advanced after native outer opening");
   for(Squad s:squads)LOG.info("GIRAN_V2_VERIFY position "+GiranRoster.CLANS[s.id]+" "+s.leader.getX()+","+s.leader.getY()+","+s.leader.getZ()+" step="+s.step+" objective="+s.objective);
   var field=PathFinding.class.getDeclaredField("_created");field.setAccessible(true);int buffers=0;for(var n:(java.util.concurrent.atomic.AtomicInteger[])field.get(PathFinding.getInstance()))buffers+=n.get();check(buffers<=32,"Global native buffer bound");LOG.info("GIRAN_V2_VERIFY buffers="+buffers);
   finish(null);
  }
 }catch(Throwable e){finish(e);}}}
 private void finish(Throwable error){
  if(timer!=null)timer.cancel(false);
  try{
   for(Squad s:squads)for(Pilot a:s.members){a.p.abortAttack();a.p.abortCast();if(a.p.hasSummon())a.p.getSummon().unSummon(a.p);if(a.p.isInParty())a.p.leaveParty();}
   var c=CastleManager.getInstance().getCastleById(3);if(started)c.getSiege().endSiege();
   for(Spawn sp:bosses){sp.stopRespawn();if(sp.getLastSpawn()!=null)sp.getLastSpawn().deleteMe();}
   for(Squad s:squads)for(Pilot a:s.members){a.p.setInvul(a.originalInvul);a.p.stopAllEffects();if(a.p.isDead())a.p.doRevive();GiranSiegeLab.restoreExperience(a);GiranSiegeLab.move(a.p,a.origin);a.p.setTitle(a.originalTitle);a.p.storeMe();GiranRoster.dispose(a.p);}
   if(started){c.getSiegeDate().setTimeInMillis(date);c.setTimeRegistrationOver(regOver);c.getTimeRegistrationOverDate().setTimeInMillis(regEnd);c.getSiege().saveSiegeDate();c.getSiege().startAutoTask();GiranRoster.registerAll();check(!c.getSiege().isInProgress()&&c.getOwnerId()==0,"Native siege ended with NPC owner");check(c.getSiegeDate().getTimeInMillis()==date,"Original siege date restored");}
   check(squads.stream().flatMap(s->s.members.stream()).noneMatch(a->World.getPlayer(a.p.getObjectId())!=null),"All19 unloaded");
  }catch(Throwable cleanup){if(error==null)error=cleanup;else error.addSuppressed(cleanup);}
  finally{if(claimed)SoloArenaGauntlet.releasePilot();agenda.clear();}
  if(error==null)LOG.info("GIRAN_V2_VERIFY PASS checks="+checks+" ticks="+ticks+" moved="+moved+" damagedDefenders="+hits+";native flags/friendship,independent agendas,native movement/damage;castle date/registrations restored; no human loaded or conquest. Full siege balance remains user trial.");
  else LOG.log(Level.SEVERE,"GIRAN_V2_VERIFY FAILED checks="+checks,error);
 }
 public static void main(String[] args){new GiranAgendaVerification();}
}
