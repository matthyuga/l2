package custom.ElvenPvpRoom;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
/** Conditional suggestions; the executor validates learned skill, costs, native conditions and every area recipient. */
public final class RoomClassSkills {
 public record Choice(int id,boolean self){}
 private RoomClassSkills(){}
 public static List<Choice> choices(Player p,Player enemy,List<Player> members,RoomTacticalPolicy.Role role){
  List<Choice> result=new ArrayList<>();double distance=p.calculateDistance2D(enemy),hp=p.getCurrentHp()/Math.max(1,p.getMaxHp());int close=0;
  for(Player q:members)if(q!=p&&!q.isDead()&&q.getInstanceId()==p.getInstanceId()&&RoomCombatRules.decision(p,q)==1&&p.calculateDistance2D(q)<300)close++;
  String name=p.getPlayerClass().name();
  if(role==RoomTacticalPolicy.Role.ARCHER){
   if(distance>350&&close==0&&!enemy.isMoving()&&!RoomNavigator.travelling(p)){result.add(new Choice(313,true));result.add(new Choice(414,true));}
   if(distance<500&&close==0)result.add(new Choice(413,true));
   if(enemy.isCastingNow()||enemy.isMoving())result.add(new Choice(101,false));
   if(hp<.6)result.add(new Choice(111,true));
  }
  if(role==RoomTacticalPolicy.Role.DAGGER){
   if(enemy.getTarget()==p&&distance<220){result.add(new Choice(11,false));result.add(new Choice(12,false));result.add(new Choice(358,false));}
   if(hp<.7&&enemy.getTarget()==p){result.add(new Choice(445,true));result.add(new Choice(111,true));}
   if(distance>180||hp<.45)result.add(new Choice(4,true));
  }
  if(role==RoomTacticalPolicy.Role.TANK&&enemy.isCastingNow())result.add(new Choice(92,false));
  if(role==RoomTacticalPolicy.Role.WARRIOR){if(hp<.3){result.add(new Choice(176,true));result.add(new Choice(139,true));}if(distance>250)result.add(new Choice(451,true));}
  if(name.equals("DOMINATOR")||name.equals("OVERLORD")){
   if(close>=2){for(int id:new int[]{1246,1208,1366,1096,1104,1108,1209,1248})result.add(new Choice(id,true));}
   if(hp<.6)result.add(new Choice(1245,false));
  }
  if(name.equals("MYSTIC_MUSE")||name.equals("SPELLSINGER"))for(int id:new int[]{1340,1342,1264})result.add(new Choice(id,false));
  if(name.equals("ARCHMAGE")||name.equals("SORCERER"))result.add(new Choice(1339,false));
  if(name.equals("STORM_SCREAMER")||name.equals("SPELLHOWLER"))for(int id:new int[]{1341,1266})result.add(new Choice(id,false));
  if(name.equals("SOULTAKER")||name.equals("NECROMANCER"))result.add(new Choice(1343,false));
  return result;
 }
 public static boolean areaAllowed(Player p,Player target,Skill skill){
  if(!Set.of(1096,1099,1104,1108,1208,1209,1210,1246,1247,1248,1366,1367).contains(skill.getId()))return false;
  int opponents=0;
  for(var object:skill.getTargetList(p,false,target)){
   if(!(object instanceof org.l2jmobius.gameserver.entity.actor.Creature creature))return false;Player owner=creature.asPlayer();
   if(owner==null||owner==p||!PvpSiegeRoster.owned(owner)||owner.getInstanceId()!=p.getInstanceId()||RoomCombatRules.decision(p,owner)!=1)return false;opponents++;
  }
  return opponents>=2;
 }
}
