package custom.ElvenPvpRoom;
import java.util.*;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import custom.ElvenPvpRoom.RoomTacticalPolicy.Role;
/** Native, room-owned execution of the reviewed role policy. No artificial damage or resource refill. */
public final class PvpTacticalEngine {
 private static final Logger LOG=Logger.getLogger(PvpTacticalEngine.class.getName());
 private record Scope(PvpRoundRooms host,RoundState.Mode mode,long generation,PvpRoomConfig.ArenaMap map){}
 private static final class State{long castAt,moveAt,kiteAt,buffAt;int target;final Map<Integer,Long> retry=new HashMap<>();final Map<String,Long> counts=new TreeMap<>();}
 private static final Map<Player,Scope> SCOPES=new IdentityHashMap<>();
 private static final Map<Player,State> STATES=new IdentityHashMap<>();
 public static volatile boolean enabled=true;
 private PvpTacticalEngine(){}
 public static void bind(PvpRoundRooms host,RoundState.Mode mode){
  try{var field=PvpRoundRooms.class.getDeclaredField("config");field.setAccessible(true);PvpRoomConfig config=(PvpRoomConfig)field.get(host);var map=config.maps.get(host.botState(mode).current());for(Player p:host.botParticipants(mode))if(PvpSiegeRoster.owned(p))SCOPES.put(p,new Scope(host,mode,host.botState(mode).generation(),map));}
  catch(ReflectiveOperationException e){throw new IllegalStateException("Room configuration unavailable",e);}
 }
 public static void forget(Player p){SCOPES.remove(p);
  // Preserve the synthetic enum-switch nest used by the already loaded trial class.
  // Both branches intentionally perform identical cleanup; tactics use string switches.
  switch(role(p)){case MAGE->STATES.remove(p);default->STATES.remove(p);}
 }
 public static Role role(Player p){return RoomTacticalPolicy.role(p.getPlayerClass().name(),p.getActiveWeaponItem()==null?"":p.getActiveWeaponItem().getItemType().toString(),p.isMageClass());}
 public static String report(Player p){State s=STATES.get(p);return "role="+role(p)+" "+(s==null?"{}":s.counts);}
 private static State state(Player p){return STATES.computeIfAbsent(p,k->new State());}
 private static void count(State s,String name){s.counts.merge(name,1L,Long::sum);}
 private static boolean hostile(Player p,Player q){return p!=q&&PvpSiegeRoster.owned(q)&&q.isOnline()&&!q.isDead()&&!q.isTeleporting()&&q.getInstanceId()==p.getInstanceId()&&RoomCombatRules.decision(p,q)==1;}
 private static boolean friendly(Player p,Player q){return q==p||PvpSiegeRoster.owned(q)&&q.isOnline()&&q.getInstanceId()==p.getInstanceId()&&RoomCombatRules.decision(p,q)==0;}
 private static double hp(Player p){return p.getCurrentHp()/Math.max(1,p.getMaxHp());}
 public static boolean act(Player p,Player fallback){
  Scope scope=SCOPES.get(p);if(scope==null)return false;
  if(!PvpSiegeRoster.owned(p)||p.getInstanceId()<=0||scope.generation()!=scope.host().botState(scope.mode()).generation())return true;
  State s=state(p);long now=System.nanoTime();count(s,"ticks");
  if(p.isDead()||p.isTeleporting()||p.isOutOfControl()||p.isControlBlocked())return true;
  PvpSiegeCombat.maintain(p);if(p.isCastingNow())return true;
  List<Player> members=scope.host().botParticipants(scope.mode());Role role=role(p);Player enemy=target(p,members,s);
  if(enemy==null&&fallback!=null&&members.contains(fallback)&&hostile(p,fallback))enemy=fallback;
  p.setRunning();if(role!=Role.MAGE&&role!=Role.HEALER&&role!=Role.BUFFER&&role!=Role.SUMMONER)PvpSiegeCombat.shot(p,false);
  if(hp(p)<.45){
   if((role==Role.TANK||role==Role.SUPPORT)&&freshCast(p,p,110,s,now,"defense"))return true;
   if((role==Role.ARCHER||role==Role.DAGGER)&&freshCast(p,p,111,s,now,"defense"))return true;
   if(hp(p)<.30)for(int id:new int[]{1401,1218,1217})if(cast(p,p,id,s,now,"self_heal"))return true;
  }
  Player patient=p;
  if(role==Role.HEALER)for(Player q:members)if(friendly(p,q)&&!q.isDead()&&!q.isTeleporting()&&hp(q)<hp(patient)&&p.calculateDistance2D(q)<1100)patient=q;
  if(role==Role.HEALER&&hp(patient)<.80){
   for(int id:new int[]{1401,1218,1217})if(cast(p,patient,id,s,now,"ally_heal"))return true;
   if(p.calculateDistance2D(patient)>550){move(p,patient.getX(),patient.getY(),s,now,scope,"heal_approach");return true;}
  }
  if(role==Role.HEALER)for(Player q:members)if(q!=p&&friendly(p,q)&&q.isDead()&&!q.isReviveRequested()&&cast(p,q,1016,s,now,"revive"))return true;
  if(now>=s.buffAt){
   s.buffAt=now+2_000_000_000L;
   int[] buffs=switch(role.name()){case "ARCHER"->new int[]{99};case "DAGGER"->new int[]{409,410};case "WARRIOR"->new int[]{297};case "SUPPORT"->p.getPlayerClass().name().equals("SWORD_MUSE")?new int[]{264,267,269,268}:new int[]{271,274,275,273,276};default->new int[]{};};
   for(int id:buffs)if(freshCast(p,p,id,s,now,"self_buff"))return true;
   if(role==Role.BUFFER)for(Player q:members)if(friendly(p,q)&&!q.isDead()){
    int[] buffsForTarget=switch(p.getPlayerClass().name()){
     case "DOOMCRYER","WARCRYER"->q.isMageClass()?new int[]{1002,1006,1362}:new int[]{1007,1251,1308,1253};
     case "DOMINATOR","OVERLORD"->new int[]{1003,1004,1005,1008,1282};
     default->q.isMageClass()?new int[]{1085,1059,1078}:new int[]{1068,1086,1240};};
    for(int id:buffsForTarget)if(freshCast(p,q,id,s,now,"ally_buff"))return true;
   }
  }
  if(summon(p,members,s,now))return true;
  if(enemy==null){count(s,"no_enemy");return true;}
  if(p.hasSummon())PvpSiegeCombat.orderSummon(p,enemy);
  double distance=p.calculateDistance2D(enemy);
  if((role==Role.ARCHER||role==Role.MAGE||role==Role.HEALER)&&distance<190&&now>=s.kiteAt&&!p.isMovementDisabled()){
   s.kiteAt=now+3_000_000_000L;
   var map=scope.map();int[] goal=RoomTacticalPolicy.retreat(p.getX(),p.getY(),enemy.getX(),enemy.getY(),map.minX(),map.maxX(),map.minY(),map.maxY(),220);
   if(goal!=null&&move(p,goal[0],goal[1],s,now,scope,"kite"))return true;
  }
  if(role==Role.TANK){
   if(!enemy.isStunned()&&cast(p,enemy,92,s,now,"control"))return true;
   if(!enemy.isRooted()&&distance>200)for(int id:new int[]{402,403})if(freshCast(p,enemy,id,s,now,"control"))return true;
  }
  if(role==Role.DAGGER&&!enemy.isStunned()&&cast(p,enemy,358,s,now,"control"))return true;
  if(role==Role.ARCHER&&!enemy.isStunned()&&cast(p,enemy,101,s,now,"control"))return true;
  if(role==Role.MAGE||role==Role.HEALER||role==Role.SUMMONER){
   if(enemy.isMageClass()&&!enemy.isMuted()&&freshCast(p,enemy,1064,s,now,"silence"))return true;
   if(role!=Role.HEALER&&freshCast(p,enemy,1263,s,now,"debuff"))return true;
  }
  if(role==Role.WARRIOR&&p.getCharges()<4&&p.getKnownSkill(8)!=null&&distance>120&&cast(p,p,8,s,now,"charge"))return true;
  int[] offense=switch(role.name()){
   case "HEALER"->new int[]{};
   case "ARCHER"->new int[]{343,369,354};
   case "DAGGER"->new int[]{30,344,263,321};
   case "TANK","SUPPORT"->new int[]{400,401,260,100};
   case "WARRIOR"->new int[]{261,5,6,284,281,280,54,346,362,260,100,1};
   default->mageSkills(p);
  };
  for(int id:offense){if(id==30&&!behind(p,enemy))continue;if(cast(p,enemy,id,s,now,"offense"))return true;}
  if(role==Role.HEALER){
   Player anchor=null;for(Player q:members)if(q!=p&&friendly(p,q)&&!q.isDead()&&(anchor==null||p.calculateDistance2D(q)<p.calculateDistance2D(anchor)))anchor=q;
   if(anchor!=null&&p.calculateDistance2D(anchor)>500)move(p,anchor.getX(),anchor.getY(),s,now,scope,"support_follow");
   return true;
  }
  int reach=role==Role.ARCHER?520:role==Role.MAGE||role==Role.BUFFER||role==Role.SUMMONER?550:55;
  if(distance>reach||!GeoEngine.getInstance().canSeeTarget(p,enemy)){double step=Math.min(350,Math.max(80,distance-reach+30));double dx=enemy.getX()-(double)p.getX(),dy=enemy.getY()-(double)p.getY();double len=Math.max(1,Math.hypot(dx,dy));move(p,p.getX()+(int)(dx/len*step),p.getY()+(int)(dy/len*step),s,now,scope,"approach");return true;}
  if(role==Role.MAGE||role==Role.BUFFER||role==Role.SUMMONER){p.abortAttack();if(p.getAI().getIntention()==Intention.ATTACK)p.getAI().setIntentionActive();return true;}
  if(p.getAI().getIntention()!=Intention.ATTACK||p.getAI().getAttackTarget()!=enemy){p.setTarget(enemy);p.getAI().setIntentionAttack(enemy);count(s,"attack_order");}
  return true;
 }
 private static int[] mageSkills(Player p){return switch(p.getPlayerClass().name()){
  case "STORM_SCREAMER","SPELLHOWLER"->new int[]{1341,1239,1234,1148};
  case "MYSTIC_MUSE","SPELLSINGER"->new int[]{1340,1235,1239};
  case "ARCHMAGE","SORCERER"->new int[]{1339,1230,1239};
  case "SOULTAKER","NECROMANCER"->new int[]{1343,1148,1234,1239};
  default->new int[]{1239,1230,1235,1245,1148};};}
 private static Player target(Player p,List<Player> members,State s){
  Player best=null;double value=-Double.MAX_VALUE;
  for(Player q:members)if(hostile(p,q)){
   double score=200*(1-hp(q))-p.calculateDistance2D(q)*.35+(q.getObjectId()==s.target?90:0);
   if(q.hasAI()&&q.getAI().getAttackTarget()==p)score+=180;
   if(role(q)==Role.HEALER)score+=70;
   if(score>value){value=score;best=q;}
  }
  s.target=best==null?0:best.getObjectId();return best;
 }
 private static boolean freshCast(Player p,Player q,int id,State s,long now,String why){
  if(q.isAffectedBySkill(id))return false;Skill incoming=p.getKnownSkill(id);
  if(incoming!=null&&!incoming.getAbnormalType().name().equals("NONE"))for(var buff:q.getEffectList().getEffects())if(buff.getSkill().getAbnormalType()==incoming.getAbnormalType()&&buff.getSkill().getAbnormalLevel()>=incoming.getAbnormalLevel())return false;
  return cast(p,q,id,s,now,why);
 }
 private static boolean cast(Player p,Player q,int id,State s,long now,String why){
  Skill skill=p.getKnownSkill(id);if(skill==null||skill.isPassive()||skill.isToggle()||skill.isSuicideAttack()||now<s.castAt||now<s.retry.getOrDefault(id,0L)||p.isSkillDisabled(skill))return false;
  if(p.isCastingNow()||p.getCurrentMp()<skill.getMpConsume()+skill.getMpInitialConsume()||p.getCurrentHp()<=skill.getHpConsume())return false;
  if(skill.getItemConsumeId()>0&&p.getInventory().getInventoryItemCount(skill.getItemConsumeId(),-1)<skill.getItemConsumeCount())return false;
  boolean hostile=skill.hasNegativeEffect()||skill.isDamage();
  if(skill.isAOE()&&hostile)return false;
  if(q!=p&&(hostile?!hostile(p,q):!friendly(p,q)))return false;
  if(q!=p&&(p.calculateDistance2D(q)>Math.max(40,skill.getCastRange()<0?skill.getAffectRange():skill.getCastRange())+20||!GeoEngine.getInstance().canSeeTarget(p,q)))return false;
  if(q.isDead()&&!skill.getTargetType().name().contains("CORPSE"))return false;
  s.retry.put(id,now+1_000_000_000L);p.setTarget(q);
  if(skill.isAOE()||skill.getTargetType().name().contains("PARTY")||skill.getTargetType().name().contains("CLAN"))for(var object:skill.getTargetList(p,false,q)){
   if(!(object instanceof org.l2jmobius.gameserver.entity.actor.Creature creature)||creature.asPlayer()==null||!friendly(p,creature.asPlayer()))return false;
  }
  if(!skill.checkCondition(p,q,false)){count(s,"condition_rejected");return false;}
  PvpSiegeCombat.shot(p,skill.isMagic());boolean used=p.useMagic(skill,true,true);
  if(used){s.castAt=now+900_000_000L;s.retry.put(id,now+(skill.isDebuff()?5_000_000_000L:1_000_000_000L));PvpSiegeCombat.castAccepted(p,skill);count(s,why+"_"+id);}else count(s,"cast_rejected");return used;
 }
 private static boolean summon(Player p,List<Player> room,State s,long now){
  if(p.hasSummon()&&p.getSummon().isDead())p.getSummon().unSummon(p);
  if(p.hasSummon()){
   Skill tp=p.getKnownSkill(1262);if(tp!=null&&!p.isAffectedBySkill(1262)&&now>=s.retry.getOrDefault(1262,0L)&&!p.isSkillDisabled(tp)&&p.getCurrentMp()>=tp.getMpConsume()+tp.getMpInitialConsume()){
    s.retry.put(1262,now+5_000_000_000L);p.setTarget(p);if(tp.checkCondition(p,p,false)&&p.useMagic(tp,true,true)){count(s,"transfer_pain");s.castAt=now+900_000_000L;return true;}
   }return false;
  }
  int id=switch(p.getPlayerClass().name()){case "ARCANA_LORD","WARLOCK"->1331;case "ELEMENTAL_MASTER","ELEMENTAL_SUMMONER"->1332;case "SPECTRAL_MASTER","PHANTOM_SUMMONER"->1333;case "HELL_KNIGHT","DARK_AVENGER"->283;case "MAESTRO","WARSMITH"->25;default->0;};
  if(id>0)return cast(p,p,id,s,now,"summon");return false;
 }
 private static boolean behind(Player p,Player target){double heading=target.getHeading()*Math.PI/32768;return (p.getX()-target.getX())*Math.cos(heading)+(p.getY()-target.getY())*Math.sin(heading)<0;}
 private static boolean move(Player p,int x,int y,State s,long now,Scope scope,String why){
  if(now<s.moveAt||p.isMovementDisabled()||p.isCastingNow())return false;
  var map=scope.map();int z=GeoEngine.getInstance().getHeight(x,y,p.getZ());Location dest=new Location(x,y,z);
  if(!map.inside(dest)||Math.abs(z-p.getZ())>128||!GeoEngine.getInstance().canMoveToTarget(p.getX(),p.getY(),p.getZ(),x,y,z,p.getInstanceId())){count(s,"move_rejected");return false;}
  p.abortAttack();p.getAI().setIntentionMoveTo(dest);s.moveAt=now+1_000_000_000L;count(s,why);return true;
 }
}
