package custom.ElvenPvpRoom;
import java.util.*;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.actor.Player;
/** Prepares distinct offline lab actors; never duplicates a live character or a real party. */
public final class PvpRoundSets {
 private static final Logger LOG=Logger.getLogger(PvpRoundSets.class.getName());
 private static final Map<PvpRoomBots,Map<RoundState.Mode,Pending>> PENDING=new IdentityHashMap<>();
 private static final ThreadLocal<ArrayDeque<Player>> HANDOFF=new ThreadLocal<>();
 public record Batch(RoundState.Mode mode,PvpRoomBots.Profile profile,List<Player> players){}
 private static final class Pending{
  final RoundState.Mode mode;final PvpRoomBots.Profile profile;final int count;final List<Player> ready=new ArrayList<>();
  boolean canceled,loading;long retryAt;
  Pending(RoundState.Mode m,int c,PvpRoomBots.Profile p){mode=m;count=c;profile=p;}
 }
 public static void warm(PvpRoomBots owner,RoundState.Mode mode,int count,PvpRoomBots.Profile profile){
  Pending pending;
  synchronized(PENDING){pending=PENDING.computeIfAbsent(owner,k->new EnumMap<>(RoundState.Mode.class)).computeIfAbsent(mode,k->new Pending(mode,count,profile));if(pending.loading||pending.ready.size()==count||System.currentTimeMillis()<pending.retryAt)return;pending.loading=true;}
  Pending task=pending;ThreadPool.execute(()->prepare(task));
 }
 private static void prepare(Pending task){
  List<Player> loaded=new ArrayList<>();boolean complete=false;
  try{
   for(int i=0;i<task.count;i++){
    synchronized(PENDING){if(task.canceled)return;}
    loaded.add(PvpSiegeRoster.acquire());
    if(i+1<task.count)Thread.sleep(250);
   }
   Collections.shuffle(loaded);
   synchronized(PENDING){if(!task.canceled){task.ready.addAll(loaded);loaded.clear();complete=true;}}
  }catch(Exception e){LOG.warning("PvpRoundSets: next "+task.mode+" batch unavailable: "+e.getMessage());}
  finally{
   for(Player p:loaded)try{PvpSiegeRoster.release(p);}catch(Exception e){LOG.warning("PvpRoundSets: cleanup failed "+p.getObjectId()+": "+e);}
   synchronized(PENDING){task.loading=false;if(!complete)task.retryAt=System.currentTimeMillis()+60000;}
  }
 }
 public static void cancel(PvpRoomBots owner,RoundState.Mode mode){
  Pending task;List<Player> release;
  synchronized(PENDING){var modes=PENDING.get(owner);task=modes==null?null:modes.remove(mode);if(modes!=null&&modes.isEmpty())PENDING.remove(owner);if(task==null)return;task.canceled=true;release=new ArrayList<>(task.ready);task.ready.clear();}
  for(Player p:release)try{PvpSiegeRoster.release(p);}catch(Exception e){LOG.warning("PvpRoundSets: cancel cleanup failed "+p.getObjectId()+": "+e);}
 }
 public static Batch beforeRound(PvpRoomBots owner,RoundState.Mode mode){
  Batch batch;
  synchronized(PENDING){var modes=PENDING.get(owner);Pending task=modes==null?null:modes.get(mode);if(task==null||task.loading||task.ready.size()!=task.count)return null;
   modes.remove(mode);if(modes.isEmpty())PENDING.remove(owner);task.canceled=true;batch=new Batch(mode,task.profile,List.copyOf(task.ready));task.ready.clear();}
  owner.stop(mode);return batch;
 }
 public static Player prepared(){var queue=HANDOFF.get();return queue==null?null:queue.poll();}
 public static void afterRound(PvpRoundRooms host,PvpRoomBots owner,Batch batch){
  if(batch==null)return;
  ArrayDeque<Player> queue=new ArrayDeque<>(batch.players());HANDOFF.set(queue);
  try{owner.start(batch.mode(),batch.players().size(),batch.profile());LOG.info("PvpRoundSets: activated new "+batch.mode()+" batch of "+batch.players().size());}
  catch(Exception e){LOG.warning("PvpRoundSets: activation failed "+batch.mode()+": "+e);}
  finally{HANDOFF.remove();for(Player p:queue)try{host.botState(batch.mode()).leave(p.getObjectId());PvpSiegeRoster.release(p);}catch(Exception e){LOG.warning("PvpRoundSets: unused profile cleanup failed: "+e);}}
 }
 public static String status(PvpRoomBots owner){synchronized(PENDING){var modes=PENDING.get(owner);if(modes==null)return "";StringJoiner out=new StringJoiner(", ");for(var e:modes.entrySet())out.add(e.getKey()+"="+e.getValue().ready.size()+"/"+e.getValue().count+(e.getValue().loading?" preparando":""));return " | Proxima tanda: "+out;}}
}
