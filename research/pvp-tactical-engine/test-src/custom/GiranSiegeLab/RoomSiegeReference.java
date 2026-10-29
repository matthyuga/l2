package custom.GiranSiegeLab;
import java.util.*;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.actor.Player;
import custom.ElvenPvpRoom.PvpSiegeCombat;
import custom.ElvenPvpRoom.RoomTacticalPolicy;
import custom.ElvenPvpRoom.RoomTacticalPolicy.Role;
/** Benchmark adapter: real siege cast implementation, room-supplied legal targets; no castle objectives. */
public final class RoomSiegeReference {
 private static final Map<Player,GiranSiegeLab.Pilot> PILOTS=new IdentityHashMap<>();
 public static void reset(){PILOTS.clear();}
 private static Role role(Player p){return RoomTacticalPolicy.role(p.getPlayerClass().name(),p.getActiveWeaponItem()==null?"":p.getActiveWeaponItem().getItemType().toString(),p.isMageClass());}
 public static void act(Player p,Player enemy,List<Player> allies){
  if(p.isDead()||p.isCastingNow()||p.isOutOfControl()||p.isControlBlocked())return;
  var a=PILOTS.computeIfAbsent(p,k->{var squad=new GiranSiegeLab.Squad(0);squad.launchAt=0;squad.leader=p;return new GiranSiegeLab.Pilot(p,squad,0,role(p).name(),true);});
  PvpSiegeCombat.maintain(p);
  Player patient=p;for(Player q:allies)if(!q.isDead()&&q.getCurrentHp()/q.getMaxHp()<patient.getCurrentHp()/patient.getMaxHp())patient=q;
  if(patient.getCurrentHp()<patient.getMaxHp()*.65)for(int id:new int[]{1401,1218,1217})if(SiegeSquadBrain.cast(a,id,patient,true))return;
  if(p.getCurrentHp()<p.getMaxHp()*.25&&SiegeSquadBrain.cast(a,110,p,false))return;
  if(PvpSiegeCombat.summon(p))return;if(enemy==null)return;PvpSiegeCombat.orderSummon(p,enemy);
  if(p.isMageClass()&&enemy.isCastingNow()&&!enemy.isAffectedBySkill(1064)&&SiegeSquadBrain.cast(a,1064,enemy,false))return;
  int[] ids=p.isMageClass()?new int[]{1239,1230,1235,1148,1234,1245}:role(p)==Role.DAGGER?new int[]{263,11,12}:role(p)==Role.TANK?new int[]{347,48,261}:new int[]{343,101};
  for(int id:ids)if(SiegeSquadBrain.cast(a,id,enemy,true))return;
  PvpSiegeCombat.shot(p,false);if(p.getAI().getAttackTarget()!=enemy||p.getAI().getIntention()!=Intention.ATTACK){p.setTarget(enemy);p.getAI().setIntentionAttack(enemy);}
 }
}
