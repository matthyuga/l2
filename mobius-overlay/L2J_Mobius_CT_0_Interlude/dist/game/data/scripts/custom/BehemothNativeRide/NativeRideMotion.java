package custom.BehemothNativeRide;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.network.serverpackets.StopMove;
/** Send the normal stop packet once on arrival, including the local rider. */
public final class NativeRideMotion {
 private record State(boolean moving,int x,int y,int z) {}
 private static final ConcurrentMap<Integer,State> STATES=new ConcurrentHashMap<>();
 private static final AtomicInteger ARRIVALS=new AtomicInteger();
 private NativeRideMotion(){}
 public static void begin(Player p){STATES.put(p.getObjectId(),new State(false,p.getX(),p.getY(),p.getZ()));p.broadcastPacket(new StopMove(p));}
 public static void tick(Player p){
  State now=new State(p.isMoving(),p.getX(),p.getY(),p.getZ()),before=STATES.put(p.getObjectId(),now);
  if(before!=null&&!now.moving()&&(before.moving()||before.x()!=now.x()||before.y()!=now.y()||before.z()!=now.z())){p.broadcastPacket(new StopMove(p));ARRIVALS.incrementAndGet();}
 }
 public static void remove(Player p){STATES.remove(p.getObjectId());}
 public static int arrivals(){return ARRIVALS.get();}
}
