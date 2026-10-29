package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.managers.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.listeners.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.*;
public final class PressureTrial extends PvpRoundRooms {
 public PressureTrial(PvpRoomConfig config){super(config,System::nanoTime,0,false);}
 private static void check(boolean condition,String reason){if(!condition)throw new IllegalStateException(reason);}
 public static void run(Path directory)throws Exception{
  Object production=VoicedCommandHandler.getInstance().getHandler("salas"),registry=ScriptManager.getInstance().getScript("PvpRoundRooms");Player human=World.getPlayer("Hellkevin");Object humanParty=human==null?null:human.getParty();int humanInstance=human==null?0:human.getInstanceId();
  var config=new PvpRoomConfig(Path.of("config/Custom/PvpRooms.properties"));Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);Object old=loading.get(null);check(old==null,"Other script loader busy");PressureTrial host;
  try{loading.set(null,directory.resolve("src/custom/ElvenPvpRoom/PressureTrial.java"));host=new PressureTrial(config);}finally{loading.set(null,old);}
  List<Player> borrowed=new ArrayList<>();List<AbstractEventListener> listeners=new ArrayList<>();StringBuilder log=new StringBuilder();
  try{
   Player archer=null,mage=null;
   for(int i=0;i<14&&(archer==null||mage==null||borrowed.size()<4);i++){
    Player p=PvpSiegeRoster.acquire();borrowed.add(p);if(archer==null&&PvpTacticalEngine.role(p)==RoomTacticalPolicy.Role.ARCHER)archer=p;
    if(mage==null&&PvpTacticalEngine.role(p)==RoomTacticalPolicy.Role.MAGE)mage=p;
   }
   check(archer!=null&&mage!=null,"No free archer/mage for paired native trial");
   List<Player> actors=new ArrayList<>(List.of(archer,mage));for(Player p:borrowed)if(p!=archer&&p!=mage&&actors.size()<4)actors.add(p);
   for(Player p:new ArrayList<>(borrowed))if(!actors.contains(p)){PvpSiegeRoster.release(p);borrowed.remove(p);}
   for(Player p:actors)check(host.botJoin(p,RoundState.Mode.TWO_TEAMS),"Fixture join rejected");
   var state=host.botState(RoundState.Mode.TWO_TEAMS);long now=System.nanoTime(),end=now+config.roundNanos+1_000_000_000L;
   check(state.vote(archer.getObjectId(),state.generation(),"primeval",now+config.roundNanos-config.voteLeadNanos+1_000_000_000L),"Fixture map vote failed");state.advance(end);state.restart(end);
   Map<Player,List<Long>> attacks=new IdentityHashMap<>();Map<Player,Map<Integer,Integer>> skills=new IdentityHashMap<>();
   for(Player p:actors){attacks.put(p,new CopyOnWriteArrayList<>());skills.put(p,new ConcurrentHashMap<>());
    var attack=new ConsumerEventListener(p,EventType.ON_CREATURE_ATTACK,(OnCreatureAttack e)->{if(e.getAttacker()==p)attacks.get(p).add(System.nanoTime());},host);p.addListener(attack);listeners.add(attack);
    var cast=new ConsumerEventListener(p,EventType.ON_CREATURE_SKILL_USE,(OnCreatureSkillUse e)->{if(e.getCaster()==p)skills.get(p).merge(e.getSkill().getId(),1,Integer::sum);},host);p.addListener(cast);listeners.add(cast);
   }
   Player dummy=actors.get(2);int physicalAttacks=0,magicCasts=0;
   for(Player attacker:List.of(archer,mage))for(boolean candidate:new boolean[]{false,true}){
    for(Player p:actors){p.abortAttack();p.abortCast();p.stopMove(null);p.getAI().setIntentionActive();if(p.isDead())p.doRevive();p.stopAllEffects();p.getDisabledSkills().clear();p.getSkillReuseTimeStamps().clear();p.getItemReuseTimeStamps().clear();if(p.hasSummon())p.getSummon().unSummon(p);RoomCombatRhythm.forget(p);PressureBaseline.forget(p);PressureCandidate.forget(p);PvpSiegeRoster.prepare(p);
     for(var skill:p.getAllSkills())if(skill.getName().startsWith("Summon "))p.disableSkill(skill,120000);
     RoomCombatRules.join(p,p==dummy?2:1,false);int x=p==attacker?6400:p==dummy?7000:5120;int y=p==attacker||p==dummy?-20016:-21040;
     int z=org.l2jmobius.gameserver.geoengine.GeoEngine.getInstance().getHeight(x,y,-3500);p.teleToLocation(new Location(x,y,z),p.getInstanceId(),0);p.onTeleported();p.setTeleportProtection(false);p.setSpawnProtection(false);p.setInvul(p!=attacker);attacks.get(p).clear();skills.get(p).clear();
    }
    PressureBaseline.bind(host,RoundState.Mode.TWO_TEAMS);PressureCandidate.bind(host,RoundState.Mode.TWO_TEAMS);attacker.setCurrentCp(attacker.getMaxCp()*.3);attacker.setCurrentMp(attacker.getMaxMp()*.4);
    long start=System.nanoTime();while(System.nanoTime()-start<12_000_000_000L){if(candidate)PressureCandidate.act(attacker,dummy);else PressureBaseline.act(attacker,dummy);Thread.sleep(candidate?100:500);}
    attacker.abortAttack();attacker.abortCast();attacker.stopMove(null);attacker.getAI().setIntentionActive();
    log.append(attacker.getName()).append(" role=").append(PvpTacticalEngine.role(attacker)).append(" brain=").append(candidate?"candidate":"baseline").append(" native_attacks=").append(attacks.get(attacker).size()).append(" executed_skills=").append(skills.get(attacker)).append('\n');
    if(candidate&&attacker==archer)physicalAttacks=attacks.get(attacker).size();if(candidate&&attacker==mage)magicCasts=skills.get(attacker).entrySet().stream().filter(e->e.getKey()<2000).mapToInt(Map.Entry::getValue).sum();
    Files.writeString(directory.resolve("pressure-trial.txt"),log);
   }
   check(physicalAttacks>=2,"Candidate did not sustain native normal attacks");check(magicCasts>=3,"Candidate did not execute native magic cadence");
   // Native area target list: two enemies and one ally, all reserved and in the same room.
   Player caster=null;int seal=0;for(Player p:actors)for(int id:new int[]{1208,1246,1096})if(p.getKnownSkill(id)!=null&&caster==null){caster=p;seal=id;}
   if(caster!=null){
    Player ally=null;for(Player p:actors)if(p!=caster){ally=p;break;}
    for(Player p:actors){p.abortAttack();p.abortCast();p.getAI().setIntentionActive();p.getDisabledSkills().clear();p.setInvul(false);p.fullRestore();p.stopAllEffects();RoomCombatRules.join(p,p==caster||p==ally?1:2,false);p.teleToLocation(new Location(6400+actors.indexOf(p)*32,-20016,-3584),p.getInstanceId(),0);p.onTeleported();p.setTeleportProtection(false);}
    var skill=caster.getKnownSkill(seal);check(RoomClassSkills.areaAllowed(caster,caster,skill),"Guard rejected two native enemies");
    for(var recipient:skill.getTargetList(caster,false,caster))check(recipient!=ally&&recipient!=caster,"Native AOE target list contains ally");
    caster.setTarget(caster);check(skill.checkCondition(caster,caster,false)&&caster.useMagic(skill,true,true),"Native seal cast rejected");long begin=System.nanoTime();do{Thread.sleep(100);}while(caster.isCastingNow()&&System.nanoTime()-begin<8_000_000_000L);
    check(!ally.isAffectedBySkill(seal),"Native seal affected same-team ally");check(skills.get(caster).getOrDefault(seal,0)>0,"Seal accepted but not executed");
    log.append("PASS native seal ").append(seal).append(" executed; ally excluded; enemy effects retain native resistance.\n");
    for(Player p:actors)if(p!=caster&&p!=ally){RoomCombatRules.join(p,1,false);break;}
    check(!RoomClassSkills.areaAllowed(caster,caster,skill),"AOE guard allowed only one opponent");
   }else log.append("SKIP no borrowed actor learned a reviewed seal; area execution not certified.\n");
   check(VoicedCommandHandler.getInstance().getHandler("salas")==production&&ScriptManager.getInstance().getScript("PvpRoundRooms")==registry,"Production lobby changed");
   check(human==null||human.getInstanceId()==humanInstance&&human.getParty()==humanParty,"Human instance/party changed during trial");
   Files.writeString(directory.resolve("pressure-trial.txt"),log);Files.writeString(directory.resolve("pressure-status.txt"),"PASS native attack/cast continuity and lobby guards; see trial for area coverage.\n");
  }finally{
   for(var listener:listeners)listener.unregisterMe();for(Player p:borrowed){RoomCombatRhythm.forget(p);PressureBaseline.forget(p);PressureCandidate.forget(p);host.botForget(p);PvpSiegeRoster.release(p);}host.closeForVerification();ScriptManager.getInstance().getScripts().remove("PressureTrial");Files.writeString(directory.resolve("cleanup.txt"),"Trial actors retired, isolated rooms closed, fixture registry removed.\n");
  }
 }
}
