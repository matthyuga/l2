package custom.ElvenPvpRoom;

import java.util.*;

/** Pure decision layer. Original implementation; references and licenses are recorded in ADAPTACION.md. */
public final class RoomTacticalPolicy {
 public enum Role { HEALER, BUFFER, ARCHER, DAGGER, TANK, MAGE, SUMMONER, WARRIOR, SUPPORT }
 public enum Kind { DEFENSE, HEAL, RESURRECT, BUFF, CONTROL, OFFENSE, MOVE, ATTACK }
 public record Self(int id,int instance,Role role,boolean dead,boolean busy,double hp,double mp){}
 public record Option(Kind kind,int skill,int target,int instance,int priority,double urgency,
  boolean known,boolean ready,boolean resources,boolean nativeAllowed,boolean legal,
  boolean inRange,boolean visible,boolean targetDead,boolean targetPendingRevive){}
 public record Decision(Kind kind,int skill,int target,String reason){
  public static Decision idle(String why){return new Decision(null,0,0,why);}
 }
 private RoomTacticalPolicy(){}
 public static Role role(String className,String weapon,boolean mage){
  String name=className.toUpperCase(Locale.ROOT),item=weapon.toUpperCase(Locale.ROOT);
  if(Set.of("CARDINAL","BISHOP","EVA_SAINT","EVAS_SAINT","ELDER","ELVEN_ELDER","SHILLIEN_SAINT","SHILLIEN_ELDER").contains(name))return Role.HEALER;
  if(Set.of("HIEROPHANT","PROPHET","DOMINATOR","OVERLORD","DOOMCRYER","WARCRYER").contains(name))return Role.BUFFER;
  if(Set.of("ARCANA_LORD","WARLOCK","ELEMENTAL_MASTER","ELEMENTAL_SUMMONER","SPECTRAL_MASTER","PHANTOM_SUMMONER").contains(name))return Role.SUMMONER;
  if(item.contains("BOW"))return Role.ARCHER;
  if(item.contains("DAGGER"))return Role.DAGGER;
  if(Set.of("PHOENIX_KNIGHT","PALADIN","HELL_KNIGHT","DARK_AVENGER","EVA_TEMPLAR","EVAS_TEMPLAR","TEMPLE_KNIGHT","SHILLIEN_TEMPLAR","SHILLIEN_KNIGHT").contains(name))return Role.TANK;
  if(Set.of("SWORD_MUSE","SWORDSINGER","SPECTRAL_DANCER","BLADEDANCER").contains(name))return Role.SUPPORT;
  return mage?Role.MAGE:Role.WARRIOR;
 }
 public static Decision choose(Self self,List<Option> options){
  if(self.dead())return Decision.idle("dead: room respawn controller retains ownership");
  if(self.busy())return Decision.idle("casting or controlled");
  Option best=null;
  for(Option option:options){
   if(option.instance()!=self.instance()||!option.legal()||!option.ready()||!option.resources()||!option.nativeAllowed()||!option.inRange()||!option.visible())continue;
   if(option.kind()==Kind.RESURRECT){if(!option.targetDead()||option.targetPendingRevive())continue;}
   else if(option.targetDead())continue;
   if(option.skill()!=0&&!option.known())continue;
   if(option.kind()==Kind.ATTACK&&(self.role()==Role.MAGE||self.role()==Role.HEALER||self.role()==Role.BUFFER||self.role()==Role.SUMMONER))continue;
   if(best==null||option.priority()<best.priority()||option.priority()==best.priority()&&option.urgency()>best.urgency())best=option;
  }
  return best==null?Decision.idle("no legal affordable action"):new Decision(best.kind(),best.skill(),best.target(),"priority="+best.priority()+" urgency="+best.urgency());
 }
 /** Returns a room-bounded retreat candidate; native geodata validation belongs to the adapter. */
 public static int[] retreat(int x,int y,int enemyX,int enemyY,int minX,int maxX,int minY,int maxY,int step){
  double dx=x-(double)enemyX,dy=y-(double)enemyY,length=Math.hypot(dx,dy);if(length<1){dx=1;dy=0;length=1;}
  int nx=x+(int)Math.round(dx/length*step),ny=y+(int)Math.round(dy/length*step);
  if(nx<=minX+64||nx>=maxX-64||ny<=minY+64||ny>=maxY-64)return null;
  return new int[]{nx,ny};
 }
}
