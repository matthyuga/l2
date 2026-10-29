package custom.ElvenPvpRoom;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.groups.*;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
/** Room-scoped adaptation of SiegeSquadBrain's movement/casting; no siege objectives or castle edits. */
public final class PvpLegacyBrain {
 private static final class State{long moved,progressAt,castAt;int x,y;Location destination;}
 private static final Map<Player,State> STATES=new IdentityHashMap<>();
 private static final Map<Object,Long> GROUP_ROUNDS=new IdentityHashMap<>();
 public static void regroup(PvpRoundRooms host,RoundState.Mode mode,Object group){long generation=host.botState(mode).generation();if(!Objects.equals(GROUP_ROUNDS.get(group),generation)){parties(host,mode);GROUP_ROUNDS.put(group,generation);}}
 public static void clearGroup(Object group){GROUP_ROUNDS.remove(group);}
 public static void forget(Player p){STATES.remove(p);PvpSiegeCombat.forget(p);}
 public static void parties(PvpRoundRooms host,RoundState.Mode mode){
  Map<Integer,List<Player>> teams=new HashMap<>();
  for(Player p:host.botParticipants(mode)){if(!PvpSiegeRoster.owned(p))continue;if(p.isInParty())p.leaveParty();teams.computeIfAbsent(host.botState(mode).team(p.getObjectId()),k->new ArrayList<>()).add(p);}
  for(List<Player> team:teams.values()){
   Collections.shuffle(team);int offset=0;
   while(offset<team.size()){
    int remaining=team.size()-offset,size=Math.min(remaining,ThreadLocalRandom.current().nextInt(2,5));if(remaining-size==1&&size<4)size++;if(size==remaining&&remaining>3)size=2;
    if(size>=2){Player leader=team.get(offset);Party party=new Party(leader,PartyDistributionType.FINDERS_KEEPERS);leader.setParty(party);for(int i=1;i<size;i++)team.get(offset+i).joinParty(party);}
    offset+=size;
   }
  }
 }
 public static Player target(Player p,List<Player> candidates){
  Player best=null;double distance=Double.MAX_VALUE;
  for(Player q:candidates){double d=p.calculateDistance2D(q);boolean party=p.isInPartyWith(q);double score=d+(party?100000:0);if(score<distance){distance=score;best=q;}}
  return best;
 }
 public static void act(Player p,Player enemy){
  if(!PvpSiegeRoster.owned(p)||enemy==null||p.isDead()||p.isOutOfControl()||p.isControlBlocked()||p.isCastingNow())return;
  PvpSiegeCombat.maintain(p);if(!p.isMageClass())PvpSiegeCombat.shot(p,false);p.setRunning();State s=STATES.computeIfAbsent(p,k->{State a=new State();a.x=p.getX();a.y=p.getY();a.progressAt=System.nanoTime();return a;});
  long now=System.nanoTime();
  if(PvpSiegeCombat.summon(p))return;
  PvpSiegeCombat.orderSummon(p,enemy);
  Player patient=p;
  if(p.isInParty())for(Player ally:p.getParty().getMembers())if(PvpSiegeRoster.owned(ally)&&!ally.isDead()&&ally.getInstanceId()==p.getInstanceId()&&ally.getCurrentHp()/ally.getMaxHp()<patient.getCurrentHp()/patient.getMaxHp())patient=ally;
  if(patient.getCurrentHp()<patient.getMaxHp()*.65)for(int id:new int[]{1401,1218,1217})if(cast(p,p.getKnownSkill(id),patient,s,now))return;
  int[] offensive=p.isMageClass()?new int[]{1239,1230,1235,1234,1245,1148}:new int[]{343,101,263,11,12,347,48,261};
  for(int id:offensive)if(cast(p,p.getKnownSkill(id),enemy,s,now))return;
  for(Skill skill:p.getAllSkills())if(skill.isDamage()&&!skill.isAOE()&&!skill.isSuicideAttack()&&!skill.isToggle()&&!skill.isPassive()&&(p.isMageClass()?skill.isMagic():!skill.isMagic())&&cast(p,skill,enemy,s,now))return;
  boolean bow=p.getKnownSkill(343)!=null&&p.getActiveWeaponItem()!=null&&p.getActiveWeaponItem().getItemType().toString().contains("BOW");
  double reach=p.isMageClass()?550:bow?500:60;
  if(p.calculateDistance2D(enemy)>reach||!GeoEngine.getInstance().canSeeTarget(p,enemy)){go(p,enemy,s,now);return;}
  if(p.isMageClass()){p.abortAttack();if(p.getAI().getIntention()==Intention.ATTACK)p.getAI().setIntentionActive();return;}
  PvpSiegeCombat.shot(p,false);
  if(p.getAI().getIntention()!=Intention.ATTACK||p.getAI().getAttackTarget()!=enemy){p.setTarget(enemy);p.getAI().setIntentionAttack(enemy);}
 }
 private static boolean cast(Player p,Skill skill,Player target,State state,long now){
  if(skill==null||skill.isPassive()||now<state.castAt||p.isSkillDisabled(skill)||p.getCurrentMp()<skill.getMpConsume()+skill.getMpInitialConsume()||p.getCurrentHp()<=skill.getHpConsume())return false;
  if(target!=p&&(p.calculateDistance2D(target)>Math.max(40,skill.getCastRange()<0?skill.getAffectRange():skill.getCastRange())+20||!GeoEngine.getInstance().canSeeTarget(p,target)))return false;
  if(skill.getItemConsumeId()>0&&p.getInventory().getInventoryItemCount(skill.getItemConsumeId(),-1)<skill.getItemConsumeCount())return false;
  p.setTarget(target);if(!skill.checkCondition(p,target,false))return false;
  PvpSiegeCombat.shot(p,skill.isMagic());
  boolean success=p.useMagic(skill,true,true);if(success){state.castAt=now+1_200_000_000L;PvpSiegeCombat.castAccepted(p,skill);}return success;
 }
 private static void go(Player p,Player target,State s,long now){
  if(Math.hypot(p.getX()-s.x,p.getY()-s.y)>24){s.x=p.getX();s.y=p.getY();s.progressAt=now;}
  double dx=target.getX()-(double)p.getX(),dy=target.getY()-(double)p.getY(),distance=Math.max(1,Math.hypot(dx,dy));
  double step=Math.min(450,distance);int x=p.getX()+(int)(dx/distance*step),y=p.getY()+(int)(dy/distance*step);
  if(now-s.progressAt>5_000_000_000L){int side=(p.getObjectId()%2==0?1:-1);x=p.getX()+(int)(-dy/distance*160*side);y=p.getY()+(int)(dx/distance*160*side);s.progressAt=now;}
  int z=GeoEngine.getInstance().getHeight(x,y,p.getZ());Location goal=new Location(x,y,z);
  if(now-s.moved<1_000_000_000L)return;
  if(p.isMoving()&&s.destination!=null&&Math.hypot(s.destination.getX()-x,s.destination.getY()-y)<100)return;
  p.abortAttack();p.getAI().setIntentionMoveTo(goal);s.destination=goal;s.moved=now;
 }
}
