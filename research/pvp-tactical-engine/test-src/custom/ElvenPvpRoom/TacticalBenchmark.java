package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.util.*;
import java.lang.reflect.*;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.*;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.listeners.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.*;
import custom.GiranSiegeLab.RoomSiegeReference;

public final class TacticalBenchmark extends PvpRoundRooms {
 private static final class Stats{
  double damage,healed;int skills,deaths,controls,moved;double x,y;final Set<Integer> ids=new TreeSet<>();
 }
 public TacticalBenchmark(PvpRoomConfig config){super(config,System::nanoTime,0,false);}
 private static void check(boolean ok,String why){if(!ok)throw new IllegalStateException(why);}
 private static List<Integer> candidates()throws Exception{
  List<Integer> ids=new ArrayList<>();
  // Actors have verified lab builds; fixed role mix on each side. Exact profiles recorded in output.
  for(int[] classes:new int[][]{{97,105,112},{94,95,103,110},{92,102,109},{90,91,99,106},{93,101,108},{88,89,113,114}}){
   String list=Arrays.toString(classes).replace('[','(').replace(']',')');
   try(var c=DatabaseFactory.getConnection();var q=c.createStatement();var rs=q.executeQuery("SELECT c.charId FROM characters c WHERE c.online=0 AND c.classid IN "+list+" AND c.account_name LIKE 'telemetry%' AND (EXISTS(SELECT 1 FROM lab_normal_npc_profiles p WHERE p.char_id=c.charId AND p.recipe_version='normal-pvp-s4-hybrid-v2') OR EXISTS(SELECT 1 FROM lab_real_human_pilots p WHERE p.char_id=c.charId AND p.recipe_version IN ('human-pilots-v3-hybrid-third','human-pilots-v2-active-slot'))) ORDER BY c.charId")){
    boolean found=false;while(rs.next())if(!ids.contains(rs.getInt(1))&&World.getPlayer(rs.getInt(1))==null){ids.add(rs.getInt(1));found=true;break;}check(found,"No free actor for role classes "+list);
   }
  }return ids;
 }
 private static Player target(Player p,List<Player> actors){Player best=null;for(Player q:actors)if(q!=p&&!q.isDead()&&RoomCombatRules.decision(p,q)==1&&(best==null||p.calculateDistance2D(q)<p.calculateDistance2D(best)))best=q;return best;}
 private static void guardian(Player p,Player enemy){
  if(p.isDead()||p.isCastingNow()||p.isOutOfControl()||p.isControlBlocked()||enemy==null)return;
  PvpSiegeCombat.maintain(p);int[] ids=p.isMageClass()?new int[]{1064,1074,1341,1291,1239}:new int[]{261,1,6};
  for(int id:ids){var skill=p.getKnownSkill(id);if(skill==null||skill.isPassive()||p.isSkillDisabled(skill)||p.getCurrentMp()<skill.getMpConsume()+skill.getMpInitialConsume()||p.calculateDistance2D(enemy)>Math.max(40,skill.getCastRange())+30)continue;if((id==1064||id==1074||id==1341)&&enemy.isAffectedBySkill(id))continue;p.setTarget(enemy);if(skill.checkCondition(p,enemy,false)){PvpSiegeCombat.shot(p,skill.isMagic());if(p.useMagic(skill,true,true))return;}}
  if(p.isMageClass()){if(p.calculateDistance2D(enemy)>550)p.getAI().moveToPawn(enemy,550);}
  else{PvpSiegeCombat.shot(p,false);if(p.getAI().getAttackTarget()!=enemy||p.getAI().getIntention()!=Intention.ATTACK){p.setTarget(enemy);p.getAI().setIntentionAttack(enemy);}}
 }
 private static void resetActors(TacticalBenchmark host,List<Player> actors,int variant)throws Exception{
  for(Player p:actors){p.abortAttack();p.abortCast();p.stopMove(null);p.getAI().setIntentionActive();if(p.hasSummon())p.getSummon().unSummon(p);if(p.isInParty())p.leaveParty();}
  Thread.sleep(1500);
  for(int i=0;i<actors.size();i++){
   Player p=actors.get(i);if(p.isDead())p.doRevive();p.stopAllEffects();p.getDisabledSkills().clear();p.getSkillReuseTimeStamps().clear();p.getItemReuseTimeStamps().clear();p.clearCharges();PvpTacticalEngine.forget(p);PvpLegacyBrain.forget(p);PvpSiegeRoster.prepare(p);
   int team=i%2+1;RoomCombatRules.join(p,team,false);int x=43673+(team==1?-90:90),y=49683+(i/2-1)*80;
   int z=org.l2jmobius.gameserver.geoengine.GeoEngine.getInstance().getHeight(x,y,-2900),instance=p.getInstanceId();p.teleToLocation(new Location(x,y,z),instance,0);p.onTeleported();p.setTeleportProtection(false);p.setInvul(false);p.setSpawnProtection(false);p.setTarget(null);
   check(p.getInstanceId()==instance&&instance>0&&x==p.getX()&&y==p.getY()&&p.isSpawned(),"Fixture reset changed instance/position or failed native spawn");
  }
  for(int team=1;team<=2;team++){List<Player> members=new ArrayList<>();for(int i=0;i<actors.size();i++)if(i%2+1==team)members.add(actors.get(i));Player lead=members.get(0);Party party=new Party(lead,PartyDistributionType.FINDERS_KEEPERS);lead.setParty(party);for(int i=1;i<members.size();i++)members.get(i).joinParty(party);}
  RoomSiegeReference.reset();PvpTacticalEngine.bind(host,RoundState.Mode.TWO_TEAMS);Thread.sleep(1000);
 }
 public static void run(Path dir)throws Exception{
  Object real=VoicedCommandHandler.getInstance().getHandler("salas");Object registered=ScriptManager.getInstance().getScript("PvpRoundRooms");Player human=World.getPlayer("Hellkevin");Object humanParty=human==null?null:human.getParty();int humanInstance=human==null?-1:human.getInstanceId();
  PvpRoomConfig config=new PvpRoomConfig(Path.of("config/Custom/PvpRooms.properties"));Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);Object prior=loading.get(null);check(prior==null,"Script loader busy");TacticalBenchmark host;
  try{loading.set(null,dir.resolve("test-src/custom/ElvenPvpRoom/TacticalBenchmark.java"));host=new TacticalBenchmark(config);}finally{loading.set(null,prior);}
  List<Player> actors=new ArrayList<>();List<AbstractEventListener> listeners=new ArrayList<>();Map<Player,Stats> stats=Collections.synchronizedMap(new IdentityHashMap<>());List<String> rows=new ArrayList<>();rows.add("baseline,leg,brain,players,damage,skills,distinct_skills,controls,deaths,healed_hp_samples,moving_samples,tick_ms_mean");
  Path csv=dir.resolve("trials.csv");StringBuilder roster=new StringBuilder();
  try{
   for(int id:candidates()){
    PvpTacticalSelection.request(id);Player p;try{p=PvpSiegeRoster.acquire();}finally{PvpTacticalSelection.clear();}
    actors.add(p);check(host.botJoin(p,RoundState.Mode.TWO_TEAMS),"Fixture entry rejected");stats.put(p,new Stats());
    var damage=new ConsumerEventListener(p,EventType.ON_CREATURE_DAMAGE_RECEIVED,(OnCreatureDamageReceived e)->{
     Player attacker=e.getAttacker()==null?null:e.getAttacker().asPlayer();if(attacker!=null&&stats.containsKey(attacker)&&actors.contains(e.getTarget())){Stats st=stats.get(attacker);synchronized(st){st.damage+=Math.max(0,e.getDamage());}}},host);p.addListener(damage);listeners.add(damage);
    var use=new ConsumerEventListener(p,EventType.ON_CREATURE_SKILL_USE,(OnCreatureSkillUse e)->{if(e.getCaster()!=p)return;Stats st=stats.get(p);synchronized(st){st.skills++;st.ids.add(e.getSkill().getId());if(e.getSkill().isDebuff()&&!e.getSkill().isDamage())st.controls++;}},host);p.addListener(use);listeners.add(use);
    var death=new ConsumerEventListener(p,EventType.ON_CREATURE_DEATH,(OnCreatureDeath e)->{if(e.getTarget()==p){Stats st=stats.get(p);synchronized(st){st.deaths++;}}},host);p.addListener(death);listeners.add(death);
    roster.append(p.getObjectId()).append(' ').append(p.getName()).append(" class=").append(p.getPlayerClass()).append(" role=").append(PvpTacticalEngine.role(p)).append(" weapon=").append(p.getActiveWeaponItem()).append('\n');
   }
   Files.writeString(dir.resolve("roster.txt"),roster);
   for(String baseline:List.of("LEGACY","SIEGE_CAST","GUARDIAN_PATTERN"))for(int leg=0;leg<2;leg++){
    resetActors(host,actors,leg);for(Player p:actors){Stats st=new Stats();st.x=p.getX();st.y=p.getY();stats.put(p,st);}
    Map<Player,Double> previousHp=new IdentityHashMap<>();for(Player p:actors)previousHp.put(p,p.getCurrentHp());
    long started=System.nanoTime(),duration=30_000_000_000L;double elapsedMs=0;int steps=0;
    Files.writeString(dir.resolve("progress.txt"),"RUNNING "+baseline+" leg="+leg+"; actors="+actors.size()+"; production untouched\n");
    while(System.nanoTime()-started<duration){
     long step=System.nanoTime();
     for(int i=0;i<actors.size();i++){
      Player p=actors.get((i+steps)%actors.size());if(p.isDead())continue;int index=actors.indexOf(p);boolean tactical=index%2==leg;Player enemy=target(p,actors);
      if(tactical)PvpTacticalEngine.act(p,enemy);
      else if(baseline.equals("LEGACY")){if(enemy!=null)PvpLegacyBrain.act(p,enemy);}
      else if(baseline.equals("SIEGE_CAST")){List<Player> allies=new ArrayList<>();for(int j=0;j<actors.size();j++)if(j%2==index%2)allies.add(actors.get(j));RoomSiegeReference.act(p,enemy,allies);}
      else guardian(p,enemy);
     }
     for(Player p:actors){Stats st=stats.get(p);if(Math.hypot(p.getX()-st.x,p.getY()-st.y)>10)st.moved++;st.x=p.getX();st.y=p.getY();double old=previousHp.get(p),hp=p.getCurrentHp();if(hp>old&&!p.isDead())st.healed+=hp-old;previousHp.put(p,hp);}
     elapsedMs+=(System.nanoTime()-step)/1_000_000.0;steps++;Thread.sleep(500);
    }
    for(boolean tactical:List.of(true,false)){
     double damage=0,healed=0;int skills=0,deaths=0,controls=0,moved=0;Set<Integer> distinct=new HashSet<>();
     for(int i=0;i<actors.size();i++)if((i%2==leg)==tactical){Stats st=stats.get(actors.get(i));damage+=st.damage;healed+=st.healed;skills+=st.skills;deaths+=st.deaths;controls+=st.controls;moved+=st.moved;distinct.addAll(st.ids);}
     rows.add(String.format(Locale.ROOT,"%s,%d,%s,3,%.1f,%d,%d,%d,%d,%.1f,%d,%.3f",baseline,leg,tactical?"TACTICAL":baseline,damage,skills,distinct.size(),controls,deaths,healed,moved,elapsedMs/Math.max(1,steps)));
    }
    Files.write(csv,rows);StringBuilder detail=new StringBuilder();for(Player p:actors)detail.append(p.getName()).append(' ').append(PvpTacticalEngine.report(p)).append(" executed=").append(stats.get(p).ids).append(" xyz=").append(p.getX()).append(',').append(p.getY()).append(',').append(p.getZ()).append(" spawned=").append(p.isSpawned()).append(" moveDisabled=").append(p.isMovementDisabled()).append(" dead=").append(p.isDead()).append('\n');Files.writeString(dir.resolve(baseline+"-leg"+leg+".txt"),detail);
    double damageTotal=0;for(Stats st:stats.values())damageTotal+=st.damage;check(damageTotal>1000,"Insufficient actual combat; trial is invalid, total damage="+damageTotal);
   }
   check(VoicedCommandHandler.getInstance().getHandler("salas")==real&&ScriptManager.getInstance().getScript("PvpRoundRooms")==registered,"Production lobby changed");
   check(human==null||human.getParty()==humanParty&&human.getInstanceId()==humanInstance,"Human party/instance changed");
   Files.writeString(dir.resolve("benchmark-status.txt"),"PASS six crossover trials executed using native combat; no claim of statistical significance. Registry and human party/instance unchanged.\n");
  }finally{
   Files.write(csv,rows);for(var listener:listeners)listener.unregisterMe();for(Player p:actors){host.botForget(p);PvpTacticalEngine.forget(p);PvpLegacyBrain.forget(p);PvpSiegeRoster.release(p);}host.closeForVerification();ScriptManager.getInstance().getScripts().remove("TacticalBenchmark",host);RoomSiegeReference.reset();Files.writeString(dir.resolve("cleanup.txt"),"Fixture actors retired; production room not closed.\n");
  }
 }
}
