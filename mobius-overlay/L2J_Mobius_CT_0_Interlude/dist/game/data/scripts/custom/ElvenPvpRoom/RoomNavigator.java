package custom.ElvenPvpRoom;
import java.util.*;
import java.util.concurrent.*;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.RoomCombatRules;

/** Persistent waypoint following, bounded asynchronous planning, and temporary failed-target memory. */
public final class RoomNavigator {
 private static final class State {
  int target,instance,index;String map="";Location goal;List<Location> path=List.of();CompletableFuture<List<Location>> future;
  long retryAt,issuedAt,progressAt,committedAt,lastFollow;double bestDistance=Double.MAX_VALUE;
  final Map<Integer,Long> blocked=new HashMap<>();final Map<String,Integer> counts=new TreeMap<>();
 }
 private static final Map<Player,State> STATES=new IdentityHashMap<>();
 private static final Semaphore JOBS=new Semaphore(2);
 private RoomNavigator(){}
 private static State state(Player p){return STATES.computeIfAbsent(p,k->new State());}
 private static void count(State s,String key){s.counts.merge(key,1,Integer::sum);}
 public static void forget(Player p){State s=STATES.remove(p);if(s!=null&&s.future!=null)s.future.cancel(false);}
 public static String report(Player p){State s=STATES.get(p);return s==null?"nav={}":"nav="+s.counts+" waypoint="+s.index+"/"+s.path.size()+" target="+s.target;}
 public static boolean travelling(Player p){State s=STATES.get(p);return s!=null&&(s.future!=null||s.index<s.path.size());}
 public static Player target(Player p,List<Player> members){
  State s=state(p);long now=System.nanoTime();Player best=null;double bestScore=-Double.MAX_VALUE;
  for(Player q:members)if(q!=p&&PvpSiegeRoster.owned(q)&&q.isOnline()&&!q.isDead()&&!q.isTeleporting()&&q.getInstanceId()==p.getInstanceId()&&RoomCombatRules.decision(p,q)==1){
   if(s.blocked.getOrDefault(q.getObjectId(),0L)>now)continue;
   double distance=p.calculateDistance2D(q),score=200*(1-q.getCurrentHp()/Math.max(1,q.getMaxHp()))-distance*.25;
   boolean visible=GeoEngine.getInstance().canSeeTarget(p,q),walk=RoomRoutePlanner.walk(new Location(p),new Location(q),p.getInstanceId());
   if(walk)score+=350;if(visible)score+=80;
   if(q.getObjectId()==s.target){score+=160;if(travelling(p)&&now-s.committedAt<20_000_000_000L)score+=1000;}
   if(q.hasAI()&&q.getAI().getAttackTarget()==p)score+=150;
   if(score>bestScore){best=q;bestScore=score;}
  }
  if(best!=null&&s.target!=best.getObjectId()){
   if(s.future!=null)s.future.cancel(false);s.future=null;s.path=List.of();s.index=0;s.retryAt=0;s.target=best.getObjectId();s.committedAt=now;
  }
  return best;
 }
 public static boolean approach(Player p,Player target,PvpRoomConfig.ArenaMap map){return follow(p,new Location(target),target.getObjectId(),map);}
 public static boolean follow(Player p,Location goal,int target,PvpRoomConfig.ArenaMap map){
  if(!PvpSiegeRoster.owned(p)||p.isDead()||p.isTeleporting()||p.isMovementDisabled()||p.isCastingNow())return false;
  State s=state(p);long now=System.nanoTime();if(now-s.lastFollow>2_000_000_000L)s.progressAt=now;s.lastFollow=now;
  if(s.instance!=p.getInstanceId()||!s.map.equals(map.id())||s.target!=target){
   if(s.future!=null)s.future.cancel(false);s.future=null;s.path=List.of();s.index=0;s.retryAt=0;s.target=target;s.instance=p.getInstanceId();s.map=map.id();s.committedAt=now;s.progressAt=now;
  }
  if(s.future!=null&&s.future.isDone()){
   try{s.path=s.future.join();}catch(CancellationException|CompletionException error){s.path=List.of();count(s,"planner_exception");java.util.logging.Logger.getLogger(RoomNavigator.class.getName()).log(java.util.logging.Level.WARNING,"Room route job failed",error);}
   s.future=null;s.index=0;s.bestDistance=Double.MAX_VALUE;s.progressAt=now;
   if(s.path.isEmpty()){fail(s,target,now,"no_route");return false;}count(s,"route_ready");
  }
  if(s.index>=s.path.size()){
   if(Math.hypot(p.getX()-goal.getX(),p.getY()-goal.getY())<50&&Math.abs(p.getZ()-goal.getZ())<64)return true;
   if(now<s.retryAt||s.future!=null)return true;
   if(!JOBS.tryAcquire()){count(s,"planner_busy");s.retryAt=now+500_000_000L;return true;}
   Location start=new Location(p),destination=new Location(goal.getX(),goal.getY(),goal.getZ());int instance=p.getInstanceId();s.goal=destination;s.future=new CompletableFuture<>();var future=s.future;count(s,"route_requested");
   ThreadPool.execute(()->{try{future.complete(RoomRouteNetwork.plan(start,destination,map,instance));}catch(Throwable error){future.completeExceptionally(error);}finally{JOBS.release();}});return true;
  }
  while(s.index<s.path.size()){
   Location point=s.path.get(s.index);double distance=Math.hypot(p.getX()-point.getX(),p.getY()-point.getY());
   if(distance<14&&Math.abs(p.getZ()-point.getZ())<48){s.index++;s.bestDistance=Double.MAX_VALUE;s.progressAt=now;count(s,"waypoint_reached");continue;}
   if(distance<s.bestDistance-12){s.bestDistance=distance;s.progressAt=now;}
   if(now-s.progressAt>7_000_000_000L){fail(s,target,now,"stuck_target_skipped");p.stopMove(null);return false;}
   if(now-s.issuedAt<900_000_000L)return true;
   if(!RoomRoutePlanner.walk(new Location(p),point,p.getInstanceId())){fail(s,target,now,"route_obstructed");return false;}
   p.abortAttack();p.setRunning();p.getAI().setIntentionMoveTo(point);s.issuedAt=now;count(s,"waypoint_order");return true;
  }
  s.path=List.of();s.retryAt=0;count(s,"route_completed");return true;
 }
 private static void fail(State s,int target,long now,String reason){s.path=List.of();s.index=0;s.retryAt=now+3_000_000_000L;if(target!=0)s.blocked.put(target,now+12_000_000_000L);count(s,reason);}
 public static void roam(Player p,PvpRoomConfig.ArenaMap map){
  State s=STATES.get(p);if(s!=null&&s.target==0&&s.goal!=null&&travelling(p)){follow(p,s.goal,0,map);return;}
  Location choice=null;double best=Double.MAX_VALUE;
  for(Location anchor:map.spawns()){double distance=Math.hypot(p.getX()-anchor.getX(),p.getY()-anchor.getY());if(distance>400&&distance<best){choice=anchor;best=distance;}}
  if(choice!=null)follow(p,choice,0,map);
 }
}

