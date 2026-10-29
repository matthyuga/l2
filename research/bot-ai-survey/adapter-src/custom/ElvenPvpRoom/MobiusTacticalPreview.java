package custom.ElvenPvpRoom;

import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import custom.ElvenPvpRoom.RoomTacticalPolicy.*;

/** Compilable Mobius adapter candidate. Preview only: never casts, moves, targets, grants skills or consumes items. */
public final class MobiusTacticalPreview {
 private static final Map<Role,int[]> ATTACKS=Map.of(
  Role.MAGE,new int[]{1339,1340,1341,1343,1239,1230,1235,1148,1234},
  Role.ARCHER,new int[]{343,369},Role.DAGGER,new int[]{30,344,263,321},
  Role.TANK,new int[]{400,401},Role.WARRIOR,new int[]{261,5,6,1,284,281,280,54,346,362,260,100},
  Role.SUMMONER,new int[]{1239,1230,1235,1148},Role.BUFFER,new int[]{1245},Role.SUPPORT,new int[]{400,401},Role.HEALER,new int[]{});
 private static final int[] HEALS={1401,1218,1217};
 private MobiusTacticalPreview(){}
 public static Role role(Player p){return RoomTacticalPolicy.role(p.getPlayerClass().name(),p.getActiveWeaponItem()==null?"":p.getActiveWeaponItem().getItemType().toString(),p.isMageClass());}
 public static Decision preview(Player p,List<Player> room,long now,Map<Integer,Long> retryUntil){
  Role role=role(p);Self self=new Self(p.getObjectId(),p.getInstanceId(),role,p.isDead(),p.isCastingNow()||p.isControlBlocked()||p.isOutOfControl()||p.isTeleporting(),ratio(p.getCurrentHp(),p.getMaxHp()),ratio(p.getCurrentMp(),p.getMaxMp()));
  if(!PvpSiegeRoster.owned(p)||!room.contains(p)||p.getInstanceId()<=0)return Decision.idle("not an active owned room actor");
  List<Option> options=new ArrayList<>();Player enemy=null;double best=Double.MAX_VALUE;
  for(Player q:room){
   if(q==p||!PvpSiegeRoster.owned(q)||q.getInstanceId()!=p.getInstanceId())continue;
   int relation=RoomCombatRules.decision(p,q);
   if(relation==1&&!q.isDead()){
    double score=p.calculateDistance2D(q)+ratio(q.getCurrentHp(),q.getMaxHp())*100;
    if(score<best){best=score;enemy=q;}
   }
   if(relation==0&&role==Role.HEALER){
    if(q.isDead()&&!q.isReviveRequested())add(options,p,q,1016,Kind.RESURRECT,25,1,now,retryUntil);
    else if(ratio(q.getCurrentHp(),q.getMaxHp())<.75)for(int skill:HEALS)add(options,p,q,skill,Kind.HEAL,10,1-ratio(q.getCurrentHp(),q.getMaxHp()),now,retryUntil);
   }
  }
  if(self.hp()<.55){
   if(role==Role.TANK||role==Role.SUPPORT)add(options,p,p,110,Kind.DEFENSE,0,1-self.hp(),now,retryUntil);
   if(role==Role.ARCHER||role==Role.DAGGER)add(options,p,p,111,Kind.DEFENSE,0,1-self.hp(),now,retryUntil);
   for(int skill:HEALS)add(options,p,p,skill,Kind.HEAL,5,1-self.hp(),now,retryUntil);
   if(role==Role.TANK)add(options,p,p,341,Kind.HEAL,5,1-self.hp(),now,retryUntil);
  }
  if(role==Role.ARCHER&&!p.isAffectedBySkill(99))add(options,p,p,99,Kind.BUFF,28,.3,now,retryUntil);
  if(role==Role.BUFFER){
   for(Player q:room)if(q==p||q.getInstanceId()==p.getInstanceId()&&PvpSiegeRoster.owned(q)&&RoomCombatRules.decision(p,q)==0){
    if(q.isDead())continue;
    for(int id:q.isMageClass()?new int[]{1085,1059,1078}:new int[]{1068,1086,1240})if(!q.isAffectedBySkill(id))add(options,p,q,id,Kind.BUFF,30,.2,now,retryUntil);
   }
  }
  if(enemy!=null){
   if(role==Role.TANK){if(!enemy.isStunned())add(options,p,enemy,92,Kind.CONTROL,35,.8,now,retryUntil);if(!enemy.isRooted()&&p.calculateDistance2D(enemy)>200)for(int id:new int[]{402,403})add(options,p,enemy,id,Kind.CONTROL,35,.6,now,retryUntil);}
   if(role==Role.ARCHER&&!enemy.isStunned())add(options,p,enemy,101,Kind.CONTROL,35,.8,now,retryUntil);
   if(role==Role.MAGE){if(enemy.isMageClass()&&!enemy.isMuted()&&!enemy.isAffectedBySkill(1064))add(options,p,enemy,1064,Kind.CONTROL,35,.8,now,retryUntil);if(!enemy.isAffectedBySkill(1263))add(options,p,enemy,1263,Kind.CONTROL,36,.6,now,retryUntil);}
   if(role==Role.DAGGER&&!enemy.isStunned())add(options,p,enemy,358,Kind.CONTROL,35,.7,now,retryUntil);
   int[] offensive=ATTACKS.get(role);
   for(int i=0;i<offensive.length;i++){
    if(offensive[i]==30&&!behind(p,enemy))continue;
    add(options,p,enemy,offensive[i],Kind.OFFENSE,50+i,.5,now,retryUntil);
   }
   options.add(new Option(Kind.ATTACK,0,enemy.getObjectId(),enemy.getInstanceId(),100,0,true,true,true,true,true,p.calculateDistance2D(enemy)<=(role==Role.ARCHER?500:60),GeoEngine.getInstance().canSeeTarget(p,enemy),false,false));
  }
  return RoomTacticalPolicy.choose(self,options);
 }
 private static double ratio(double value,double max){return value/Math.max(1,max);}
 private static boolean behind(Player p,Player target){double heading=target.getHeading()*Math.PI/32768;return (p.getX()-target.getX())*Math.cos(heading)+(p.getY()-target.getY())*Math.sin(heading)<0;}
 private static void add(List<Option> options,Player p,Player target,int id,Kind kind,int priority,double urgency,long now,Map<Integer,Long> retryUntil){
  Skill skill=p.getKnownSkill(id);if(skill==null||skill.isPassive()||skill.isAOE()||skill.isToggle()||skill.isSuicideAttack())return;
  boolean resources=p.getCurrentMp()>=skill.getMpConsume()+skill.getMpInitialConsume()&&p.getCurrentHp()>skill.getHpConsume()&&(skill.getItemConsumeId()<=0||p.getInventory().getInventoryItemCount(skill.getItemConsumeId(),-1)>=skill.getItemConsumeCount());
  boolean friend=target==p||RoomCombatRules.decision(p,target)==0;
  boolean legal=target==p||PvpSiegeRoster.owned(target)&&p.getInstanceId()==target.getInstanceId()&&(kind==Kind.HEAL||kind==Kind.BUFF||kind==Kind.RESURRECT?friend:RoomCombatRules.decision(p,target)==1);
  int range=Math.max(40,skill.getCastRange()<0?skill.getAffectRange():skill.getCastRange())+20;
  // Native checkCondition/useMagic must run again at execution, with the exact target; preview does not mutate target.
  options.add(new Option(kind,id,target.getObjectId(),target.getInstanceId(),priority,urgency,true,!p.isSkillDisabled(skill)&&now>=retryUntil.getOrDefault(id,0L),resources,true,legal,target==p||p.calculateDistance2D(target)<=range,target==p||GeoEngine.getInstance().canSeeTarget(p,target),target.isDead(),target.isReviveRequested()));
 }
}
