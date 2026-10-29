package custom.ElvenPvpRoom;
import java.util.*;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureAttack;
import org.l2jmobius.gameserver.mechanics.skill.Skill;

/** Input reaction and skill weaving. Native attack, cast and item reuse clocks are never changed. */
public final class RoomCombatRhythm {
 private static final class State {long weaveAt,targetAt,lastAttack,lastInterval;int attacks,skills,selected;ConsumerEventListener listener;}
 private static final Map<Player,State> STATES=new IdentityHashMap<>();
 private RoomCombatRhythm(){}
 private static State state(Player p){
  State s=STATES.get(p);if(s!=null)return s;s=new State();STATES.put(p,s);State captured=s;
  s.weaveAt=System.nanoTime()+1_500_000_000L;
  s.listener=new ConsumerEventListener(p,EventType.ON_CREATURE_ATTACK,(OnCreatureAttack event)->{if(event.getAttacker()==p){long now=System.nanoTime();synchronized(captured){if(captured.lastAttack!=0)captured.lastInterval=now-captured.lastAttack;captured.lastAttack=now;captured.attacks++;}}},RoomCombatRhythm.class);p.addListener(s.listener);return s;
 }
 public static void forget(Player p){State s=STATES.remove(p);if(s!=null&&s.listener!=null)s.listener.unregisterMe();}
 public static String report(Player p){State s=STATES.get(p);return s==null?"rhythm={}":"rhythm={native_attacks="+s.attacks+", skills="+s.skills+", last_attack_interval_ms="+(s.lastInterval/1000000)+"}";}
 public static Player target(Player p,List<Player> members){
  State s=state(p);long now=System.nanoTime();
  if(now<s.targetAt)for(Player q:members)if(q.getObjectId()==s.selected&&!q.isDead()&&!q.isTeleporting()&&q.getInstanceId()==p.getInstanceId()&&RoomCombatRules.decision(p,q)==1)return q;
  Player q=RoomNavigator.target(p,members);s.selected=q==null?0:q.getObjectId();s.targetAt=now+400_000_000L;return q;
 }
 public static void pressure(Player p,Player enemy){
  state(p);
  if(p.isAffectedBySkill(313)&&(enemy==null||p.calculateDistance2D(enemy)>p.getPhysicalAttackRange()+50||p.calculateDistance2D(enemy)<250))p.stopSkillEffects(org.l2jmobius.gameserver.mechanics.skill.enums.SkillFinishType.REMOVED,313);
  if(enemy==null)return;
  if(p.isCastingNow()||p.isAttackingNow()||p.isAttackDisabled()||p.isMovementDisabled()&&p.getPhysicalAttackRange()<200)return;
  if(p.calculateDistance2D(enemy)>p.getPhysicalAttackRange()+160||Math.abs(p.getZ()-enemy.getZ())>80||!GeoEngine.getInstance().canSeeTarget(p,enemy)||!RoomRoutePlanner.walk(new org.l2jmobius.gameserver.entity.Location(p),new org.l2jmobius.gameserver.entity.Location(enemy),p.getInstanceId()))return;
  if(p.getAI().getIntention()!=Intention.ATTACK||p.getAI().getAttackTarget()!=enemy){p.setTarget(enemy);p.getAI().setIntentionAttack(enemy);}
 }
 public static boolean weave(Player p){return System.nanoTime()>=state(p).weaveAt;}
 public static void skillUsed(Player p,Skill skill){
  State s=state(p);s.skills++;
  long interval=p.getActiveWeaponItem()!=null&&p.getActiveWeaponItem().getItemType().toString().contains("BOW")?3_000_000_000L:1_900_000_000L;
  s.weaveAt=System.nanoTime()+interval+(Math.floorMod(p.getObjectId(),4)*100_000_000L);
 }
}
