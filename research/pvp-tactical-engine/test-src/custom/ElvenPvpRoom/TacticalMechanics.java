package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.listeners.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureSkillUse;
public final class TacticalMechanics extends PvpRoundRooms{
 public TacticalMechanics(PvpRoomConfig config){super(config,System::nanoTime,0,false);}
 private static void check(boolean ok,String why){if(!ok)throw new IllegalStateException(why);}
 private static int profile(int... classes)throws Exception{
  String list=Arrays.toString(classes).replace('[','(').replace(']',')');
  try(var c=DatabaseFactory.getConnection();var q=c.createStatement();var rs=q.executeQuery("SELECT c.charId FROM characters c WHERE c.online=0 AND c.classid IN "+list+" AND c.account_name LIKE 'telemetry%' AND EXISTS(SELECT 1 FROM lab_normal_npc_profiles p WHERE p.char_id=c.charId AND p.recipe_version='normal-pvp-s4-hybrid-v2') ORDER BY FIELD(c.classid,"+list.substring(1,list.length()-1)+"),c.charId")){
   while(rs.next())if(World.getPlayer(rs.getInt(1))==null)return rs.getInt(1);
  }throw new IllegalStateException("Role unavailable "+list);
 }
 private static void pump(Player p,long millis)throws Exception{long end=System.currentTimeMillis()+millis;while(System.currentTimeMillis()<end){PvpTacticalEngine.act(p,null);Thread.sleep(250);}}
 public static void run(Path dir)throws Exception{
  Object production=VoicedCommandHandler.getInstance().getHandler("salas"),registry=ScriptManager.getInstance().getScript("PvpRoundRooms");
  PvpRoomConfig config=new PvpRoomConfig(Path.of("config/Custom/PvpRooms.properties"));Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);Object prior=loading.get(null);check(prior==null,"Script loader busy");TacticalMechanics host;
  try{loading.set(null,dir.resolve("test-src/custom/ElvenPvpRoom/TacticalMechanics.java"));host=new TacticalMechanics(config);}finally{loading.set(null,prior);}
  List<Player> actors=new ArrayList<>();List<AbstractEventListener> listeners=new ArrayList<>();Map<Player,Set<Integer>> used=new IdentityHashMap<>();StringBuilder log=new StringBuilder();AtomicInteger heals=new AtomicInteger(),silences=new AtomicInteger();
  try{
   for(int[] classes:new int[][]{{105,112,97},{95,110,94,103},{92,102,109},{90,99,106},{96,104,111},{107,100},{116,98,115}}){
    int id=profile(classes);PvpTacticalSelection.request(id);Player p;try{p=PvpSiegeRoster.acquire();}finally{PvpTacticalSelection.clear();}actors.add(p);check(host.botJoin(p,RoundState.Mode.TWO_TEAMS),"Entry rejected");used.put(p,ConcurrentHashMap.newKeySet());
    int slot=actors.size()-1;var event=new ConsumerEventListener(p,EventType.ON_CREATURE_SKILL_USE,(OnCreatureSkillUse e)->{if(e.getCaster()!=p)return;int skill=e.getSkill().getId();used.get(p).add(skill);if(slot==0&&Set.of(1401,1218,1217).contains(skill))heals.incrementAndGet();if(slot==1&&skill==1064)silences.incrementAndGet();},host);p.addListener(event);listeners.add(event);
   }
   // Select Primeval by a real vote on the isolated room model, then begin its next generation.
   var state=host.botState(RoundState.Mode.TWO_TEAMS);long now=System.nanoTime(),voteAt=now+config.roundNanos-config.voteLeadNanos+1_000_000_000L;
   check(state.vote(actors.get(0).getObjectId(),state.generation(),"primeval",voteAt),"Fixture map vote failed");state.advance(now+config.roundNanos+2_000_000_000L);state.restart(now+config.roundNanos+2_000_000_000L);
   for(int i=0;i<actors.size();i++){
    Player p=actors.get(i);int team=state.join(p.getObjectId(),p.getName());int x=6400+(team==1?-40:40),y=-20016+i/2*32,z=GeoEngine.getInstance().getHeight(x,y,-3584);p.teleToLocation(new Location(x,y,z),p.getInstanceId(),0);p.onTeleported();p.setTeleportProtection(false);p.setInvul(false);p.setSpawnProtection(false);RoomCombatRules.join(p,team,false);check(p.isSpawned()&&p.getInstanceId()>0&&config.maps.get("primeval").inside(new Location(p)),"Native fixture spawn failed");
   }
   for(int team=1;team<=2;team++){List<Player> members=new ArrayList<>();for(Player p:actors)if(state.team(p.getObjectId())==team)members.add(p);Player leader=members.get(0);Party party=new Party(leader,PartyDistributionType.FINDERS_KEEPERS);leader.setParty(party);for(int i=1;i<members.size();i++)members.get(i).joinParty(party);}
   PvpTacticalEngine.bind(host,RoundState.Mode.TWO_TEAMS);
   Player healer=actors.get(0),mage=actors.get(1),archer=actors.get(2),tank=actors.get(3),summoner=actors.get(4),support=actors.get(5),buffer=actors.get(6);
   archer.setCurrentHp(archer.getMaxHp()*.35);double before=archer.getCurrentHp();pump(healer,4500);
   check(heals.get()>0&&archer.getCurrentHp()-before>1000,"Native ally heal did not execute/recover HP");log.append("PASS ally healing: native casts=").append(heals).append(" hp_gain=").append(archer.getCurrentHp()-before).append('\n');
   // Isolate one caster target; the healer may have kited away after finishing the healing scenario.
   for(Player p:actors)if(p!=healer)RoomCombatRules.join(p,2,false);
   mage.teleToLocation(new Location(healer.getX()+150,healer.getY(),healer.getZ()),mage.getInstanceId(),0);mage.onTeleported();mage.setTeleportProtection(false);mage.setSpawnProtection(false);
   log.append("Mage ").append(mage.getName()).append(" silence_known=").append(mage.getKnownSkill(1064)!=null).append('\n');pump(mage,4500);check(silences.get()>0,"No native Silence cast executed: "+PvpTacticalEngine.report(mage)+" used="+used.get(mage));log.append("PASS native Silence executed; effect_seen=").append(healer.isMuted()||healer.isAffectedBySkill(1064)).append('\n');
   for(Player p:actors)RoomCombatRules.join(p,state.team(p.getObjectId()),false);
   mage.abortAttack();mage.abortCast();mage.getAI().setIntentionActive();
   tank.setCurrentHp(tank.getMaxHp()*.30);pump(tank,3000);check(tank.isAffectedBySkill(110),"Native Ultimate Defense missing");log.append("PASS native Ultimate Defense active\n");
   double x=archer.getX(),y=archer.getY();pump(archer,5500);check(Math.hypot(archer.getX()-x,archer.getY()-y)>30&&PvpTacticalEngine.report(archer).contains("kite="),"No actual native kite movement");check(config.maps.get("primeval").inside(new Location(archer)),"Kite left perimeter");log.append("PASS native kite moved ").append(Math.hypot(archer.getX()-x,archer.getY()-y)).append(" within Primeval perimeter\n");
   archer.abortAttack();archer.abortCast();archer.getAI().setIntentionActive();pump(summoner,8500);check(summoner.hasSummon()&&summoner.getSummon().getInstanceId()==summoner.getInstanceId(),"Native summon missing/cross-instance");log.append("PASS native summon present; transfer_pain=").append(summoner.isAffectedBySkill(1262)).append('\n');
   pump(support,5500);boolean dance=false;for(int id:new int[]{264,267,268,269,271,273,274,275,276})dance|=tank.isAffectedBySkill(id);check(dance,"No native song/dance reached ally");log.append("PASS native party song/dance reached tank\n");
   archer.stopAllEffects();pump(buffer,7000);boolean buff=false;for(int id:new int[]{1007,1251,1068,1086,1240,1003,1282})buff|=archer.isAffectedBySkill(id);check(buff,"No native buffer skill reached ally");log.append("PASS native buffer restored missing ally buff\n");
   for(Player p:actors){p.abortAttack();p.abortCast();p.getAI().setIntentionActive();RoomCombatRules.join(p,0,false);}healer.stopAllEffects();PvpSiegeRoster.prepare(healer);archer.stopAllEffects();archer.setCurrentHp(archer.getMaxHp()*.35);int count=heals.get();pump(healer,1500);check(heals.get()==count,"Healer treated FFA party opponent as ally");log.append("PASS FFA party opponent not healed\n");
   host.botForget(archer);var oldWorld=InstanceManager.getInstance().getWorld(archer.getInstanceId());if(oldWorld!=null)oldWorld.removeAllowed(archer);
   archer.teleToLocation(new Location(6400,-20016,-3584),0,0);archer.onTeleported();archer.setTeleportProtection(false);
   org.l2jmobius.gameserver.taskmanagers.AttackStanceTaskManager.getInstance().removeAttackStanceTask(archer);
   check(host.botJoin(archer,RoundState.Mode.FREE),"Separate instance entry failed");check(archer.getInstanceId()!=healer.getInstanceId(),"Rooms did not isolate actors");count=heals.get();pump(healer,1500);check(heals.get()==count,"Cross-instance ally heal");log.append("PASS separate room instance not selected\n");
   check(VoicedCommandHandler.getInstance().getHandler("salas")==production&&ScriptManager.getInstance().getScript("PvpRoundRooms")==registry,"Production lobby registry changed");
   for(Player p:actors)log.append(p.getName()).append(' ').append(PvpTacticalEngine.report(p)).append(" executed=").append(used.get(p)).append('\n');
   Files.writeString(dir.resolve("mechanics-status.txt"),"PASS native mechanics checks in isolated Primeval room\n");
  }finally{for(var listener:listeners)listener.unregisterMe();for(Player p:actors){host.botForget(p);PvpTacticalEngine.forget(p);PvpSiegeRoster.release(p);}host.closeForVerification();ScriptManager.getInstance().getScripts().remove("TacticalMechanics",host);Files.writeString(dir.resolve("mechanics.txt"),log);}
 }
}
