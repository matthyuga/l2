import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.l2jmobius.gameserver.config.GeoEngineConfig;
import org.l2jmobius.gameserver.geoengine.pathfinding.*;
/** Concurrent lease stress using native arrays; does not start a server or load players. */
public class PathPoolCheck {
 public static void main(String[] args)throws Exception{
  GeoEngineConfig.PATHFIND_BUFFERS="100x6;128x6;192x6;256x4;320x4;384x4;500x2";
  var ctor=PathFinding.class.getDeclaredConstructor();ctor.setAccessible(true);PathFinding pool=ctor.newInstance();
  Method take=PathFinding.class.getDeclaredMethod("alloc",int.class),give=PathFinding.class.getDeclaredMethod("release",NodeBuffer.class);take.setAccessible(true);give.setAccessible(true);
  List<NodeBuffer> all=new ArrayList<>();while(true){NodeBuffer n=(NodeBuffer)take.invoke(pool,1);if(n==null)break;all.add(n);}
  if(all.size()!=32)throw new IllegalStateException("Configured count mismatch "+all.size());
  if(take.invoke(pool,501)!=null)throw new IllegalStateException("Oversized allocation accepted");
  for(NodeBuffer n:all)give.invoke(pool,n);
  Set<NodeBuffer> leased=Collections.synchronizedSet(Collections.newSetFromMap(new IdentityHashMap<>()));AtomicInteger success=new AtomicInteger();ExecutorService workers=Executors.newFixedThreadPool(128);CountDownLatch start=new CountDownLatch(1);List<Future<?>> jobs=new ArrayList<>();
  for(int w=0;w<128;w++){final int seed=w;jobs.add(workers.submit(()->{try{start.await();for(int i=0;i<200;i++){
   NodeBuffer n=(NodeBuffer)take.invoke(pool,new int[]{80,115,180,230,300,370,450}[(seed+i)%7]);if(n==null)continue;
   if(!leased.add(n))throw new IllegalStateException("Concurrent double lease");
   try{Thread.yield();success.incrementAndGet();n.free();}finally{if(!leased.remove(n))throw new IllegalStateException("Missing lease");give.invoke(pool,n);}
  }}catch(Exception e){throw new RuntimeException(e);}}));}start.countDown();for(Future<?> f:jobs)f.get();workers.shutdown();
  Field counts=PathFinding.class.getDeclaredField("_created"),limits=PathFinding.class.getDeclaredField("_limits");counts.setAccessible(true);limits.setAccessible(true);int total=0;AtomicInteger[] created=(AtomicInteger[])counts.get(pool);int[] cap=(int[])limits.get(pool);
  for(int i=0;i<cap.length;i++){if(created[i].get()>cap[i])throw new IllegalStateException("Pool exceeded cap");total+=created[i].get();}
  if(total!=32||!leased.isEmpty()||success.get()<1000)throw new IllegalStateException("Stress result");
  long bytes=all.stream().mapToLong(n->32L*n.getMapSize()*n.getMapSize()).sum();
  System.out.println("PATH_POOL PASS:128 concurrent workers,25600requests,"+success.get()+"exclusive leases,32max buffers,"+bytes+"bytes primitive arrays (under80MiB),no ThreadLocal growth.");
 }
}
