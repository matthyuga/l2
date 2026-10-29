import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import java.util.jar.JarFile;
import java.util.concurrent.atomic.AtomicLong;
import java.lang.reflect.*;
import custom.ElvenPvpRoom.*;
import custom.ElvenPvpRoom.RoundState.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.managers.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDeath;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
public class VerifyRoundRoomsV3 {
 static void check(boolean ok,String m){if(!ok)throw new AssertionError(m);}
 static Object field(Object o,String n)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(o);}
 static void set(Object o,String n,long value)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);f.setLong(o,value);}
 static Player player(String name)throws Exception{
  var template=PlayerTemplateData.getInstance().getTemplate(0);var ctor=Player.class.getDeclaredConstructor(template.getClass(),String.class,org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance.class);ctor.setAccessible(true);
  Player p=ctor.newInstance(template,"round-transient-probe",new org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance((byte)0,(byte)0,(byte)0,false));
  p.setName(name);p.setLabControlled(true);p.setOnlineStatus(true,false);p.setEnteredWorld();p.setDead(false);p.setInvul(false);p.setSpawnProtection(false);p.spawnMe(83425,148585,-3406);
  p.setCurrentHp(p.getMaxHp()*0.6);p.setCurrentMp(p.getMaxMp()*0.5);p.setCurrentCp(p.getMaxCp()*0.4);
  SkillData.getInstance().getSkill(1204,1).applyEffects(p,p);p.addTimeStamp(SkillData.getInstance().getSkill(1204,1),120000);return p;
 }
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path s=Path.of(directory);StringBuilder out=new StringBuilder();List<Player> probes=new ArrayList<>();PvpRoundRooms controller=null;
  Player user=World.getPlayer(268473899);int userInstance=user==null?-1:user.getInstanceId();int ux=user==null?0:user.getX(),uy=user==null?0:user.getY();
  try{
   // Support is appended by the deployment agent before this verification agent is loaded.
   AtomicLong clock=new AtomicLong(1_000_000_000L);long start=clock.get();
   PvpRoomConfig config=new PvpRoomConfig(s.resolve("PvpRooms.properties"));
   Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);
   Object previous=loading.get(null);check(previous==null,"Another script is loading");
   try{loading.set(null,s.resolve("src/custom/ElvenPvpRoom/PvpRoundRooms.java"));controller=new PvpRoundRooms(config,clock::get,0,false);}finally{loading.set(null,previous);}

   Player a=player("RoundProbeA"),b=player("RoundProbeB"),c=player("RoundProbeC");probes.add(a);probes.add(b);probes.add(c);
   double hp=a.getCurrentHp(),mp=a.getCurrentMp(),cp=a.getCurrentCp();
   controller.onCommand("salas",a,"equipos");controller.onCommand("salas",b,"equipos");controller.onCommand("salas",c,"equipos");
   check(a.getInstanceId()==b.getInstanceId()&&a.getInstanceId()==c.getInstanceId()&&a.getInstanceId()!=userInstance,"Isolation failed");
   check(RoomCombatRules.decision(a,b)==1&&RoomCombatRules.decision(a,c)==0,"Team relation failed");
   check(b.isAutoAttackable(a)&&!c.isAutoAttackable(a),"Autoattack relation failed");
   check(a.getPvpFlag()==1&&!a.isTeleportProtected()&&a.getCurrentHp()==hp&&a.getCurrentMp()==mp&&a.getCurrentCp()==cp&&a.isAffectedBySkill(1204),"Entry changed state or protection");
   double before=c.getCurrentHp();c.getStatus().reduceHp(3,a,true,false,false,true);check(c.getCurrentHp()==before,"Friendly physical damage");
   before=b.getCurrentHp();b.getStatus().reduceHp(3,a,true,false,false,true);check(b.getCurrentHp()<before,"Enemy damage blocked");
   var debuff=SkillData.getInstance().getSkill(1164,19);check(!a.checkPvpSkill(c,debuff)&&a.checkPvpSkill(b,debuff),"Debuff target rules");
   debuff.applyEffects(a,c);check(!c.isAffectedBySkill(1164),"Friendly debuff applied");
   out.append("PASS isolated team room, balanced teams, hostile targeting, actual friendly/enemy damage, debuffs, state preservation and no immunity.\n");
   Map<?,?> rooms=(Map<?,?>)field(controller,"rooms");Object teamRoom=rooms.get(Mode.TWO_TEAMS);RoundState state=(RoundState)field(teamRoom,"state");
   Method death=PvpRoundRooms.class.getDeclaredMethod("death",OnCreatureDeath.class,long.class);death.setAccessible(true);death.invoke(controller,new OnCreatureDeath(a,b),state.generation());
   check(state.teamScore(1)==1,"Kill not counted");death.invoke(controller,new OnCreatureDeath(a,b),state.generation());check(state.teamScore(1)==1,"Duplicate kill counted");
   clock.set(start+1500_000_000_000L);controller.tick();check(state.phase()==Phase.VOTING,"Vote timing");
   controller.onCommand("salas",a,"votar 1 primeval");controller.onCommand("salas",a,"votar 1 saints");check(state.tally().get("primeval")==1&&state.tally().get("saints")==0,"Double vote accepted");
   controller.onCommand("salas",b,"votar 1 primeval");clock.set(start+1560_000_000_000L);controller.tick();check(state.phase()==Phase.RESULT&&state.next().equals("primeval"),"Voting winner");
   clock.set(start+1800_000_000_000L);controller.tick();check(state.current().equals("primeval")&&state.generation()==2,"Map did not switch");
   check(config.maps.get("primeval").inside(new Location(a))&&a.getPvpFlag()==1&&a.getCurrentHp()==hp,"Map switch changed resources or outside perimeter");
   check(a.getSkillRemainingReuseTime(SkillData.getInstance().getSkill(1204,1).getReuseHashCode())>110000,"Map change reset cooldown");
   check(state.teamScore(1)==0,"Score not reset");death.invoke(controller,new OnCreatureDeath(a,b),1L);check(state.teamScore(1)==0,"Previous round death counted");
   out.append("PASS death scoring/deduplication, 5m vote/60s close, duplicate vote rejection, winner, map switch, score reset, stale death rejection and preserved cooldown.\n");
   clock.set(start+3300_000_000_000L);controller.tick();controller.onCommand("salas",a,"votar 2 saints");clock.set(start+3360_000_000_000L);controller.tick();
   clock.set(start+3600_000_000_000L);controller.tick();check(state.current().equals("saints")&&config.maps.get("saints").inside(new Location(a)),"Saints transition failed");
   Object visit=((Map<?,?>)field(controller,"visits")).get(a.getObjectId());Location last=new Location(a);
   var m=config.maps.get("saints");a.setXYZ(m.maxX()+32,a.getY(),a.getZ());controller.tick();check((long)field(visit,"exitStarted")>0,"Exit did not begin");
   a.setXYZ(last.getX(),last.getY(),last.getZ());controller.tick();check((long)field(visit,"exitStarted")==0&&a.getPvpFlag()==1,"Exit cancel");
   controller.onCommand("salas",a,"salir");clock.addAndGet(3_800_000_000L);controller.tick();check(a.getInstanceId()>0,"Early exit");clock.addAndGet(300_000_000L);controller.tick();check(a.getInstanceId()==0&&RoomCombatRules.decision(a,c)==-1,"Exit membership cleanup");
   check(Objects.equals(a.getAppearance().getVisibleTitle(),a.getTitle()),"Team title not restored");
   out.append("PASS Saints terrain/transition, boundary cancellation, 4s exit and native combat restored outside.\n");
   Player free=player("RoundProbeFree");probes.add(free);controller.onCommand("salas",free,"libre");check(free.getInstanceId()!=b.getInstanceId(),"Modes share instance");
   Player free2=player("RoundProbeFree2");probes.add(free2);controller.onCommand("salas",free2,"libre");check(RoomCombatRules.decision(free,free2)==1,"FFA attack relation");
   free.setOnlineStatus(false,false);controller.tick();check(!PvpFlagTaskManager.getInstance().isForced(free),"Offline flag owner leaked");
   if(user!=null)check(user.getInstanceId()==userInstance&&user.getX()==ux&&user.getY()==uy,"User moved during test");
   out.append("PASS independent mode instances, FFA opponent rule, offline cleanup; Hellkevin location unchanged.\n");
  }catch(Throwable t){out.append("FAIL ").append(t).append('\n');throw t;}
  finally{
   if(controller!=null)controller.closeForVerification();
   for(Player p:probes){p.abortAttack();p.abortCast();p.stopAllEffects();p.deleteMe();p.setOnlineStatus(false,false);RoomCombatRules.leave(p);}
   PvpFlagTaskManager.getInstance().run();Files.writeString(s.resolve("server-verification-v3.txt"),out);
  }
 }
}
