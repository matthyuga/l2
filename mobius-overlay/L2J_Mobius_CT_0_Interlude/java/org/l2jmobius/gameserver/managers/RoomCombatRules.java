package org.l2jmobius.gameserver.managers;

import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;

/** Explicit membership; never changes combat rules outside these instances. */
public final class RoomCombatRules {
 private record Member(int instance,int team,boolean friendlyFire) {}
 private static final Map<Integer,Member> MEMBERS=new ConcurrentHashMap<>();
 private RoomCombatRules(){}
 public static void join(Player p,int team,boolean friendlyFire){
  if(p.getInstanceId()<=0 || team<0 || team>3)throw new IllegalArgumentException("Invalid room membership");
  MEMBERS.put(p.getObjectId(),new Member(p.getInstanceId(),team,friendlyFire));
 }
 public static void leave(Player p){MEMBERS.remove(p.getObjectId());}
 /** -1: native rules, 0: friendly target, 1: valid opponent (party/clan irrelevant). */
 public static int decision(Creature attacker,Creature target){
  if(attacker==null || target==null || !attacker.isPlayable() || !target.isPlayable())return -1;
  Player a=attacker.asPlayer(),b=target.asPlayer();
  if(a==null || b==null || a==b)return -1;
  Member am=MEMBERS.get(a.getObjectId()),bm=MEMBERS.get(b.getObjectId());
  if(am==null || bm==null || !a.isOnline() || !b.isOnline() || a.getInstanceId()!=am.instance || b.getInstanceId()!=bm.instance || am.instance!=bm.instance)return -1;
  return am.team==0 || am.team!=bm.team || am.friendlyFire?1:0;
 }
}
