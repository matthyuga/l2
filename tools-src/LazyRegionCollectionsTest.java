import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;

/** Regression coverage for cold regions, concurrent publication and visibility migration. */
public class LazyRegionCollectionsTest {
 static class ObjectStub extends WorldObject {
  ObjectStub(int id){super(id);}
  public boolean isAutoAttackable(Creature c){return false;}
  public void sendInfo(Player p){}
 }
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 static Object field(WorldRegion r,String name)throws Exception{Field f=WorldRegion.class.getDeclaredField(name);f.setAccessible(true);return f.get(r);}
 public static void main(String[] args)throws Exception{
  WorldRegion cold=new WorldRegion(0,0,0);
  for(String name:List.of("_visibleObjects","_doors","_fences"))check(field(cold,name)==null,"eager allocation "+name);
  check(cold.getVisibleObjects().isEmpty()&&cold.getDoors().isEmpty()&&cold.getFences().isEmpty(),"cold reads");
  cold.removeVisibleObject(new ObjectStub(1));
  for(String name:List.of("_visibleObjects","_doors","_fences"))check(field(cold,name)==null,"read/remove allocated "+name);
  ObjectStub object=new ObjectStub(2);cold.addVisibleObject(object);
  Collection<WorldObject> published=cold.getVisibleObjects();
  cold.removeVisibleObject(object);cold.addVisibleObject(object);
  check(published==cold.getVisibleObjects()&&published.contains(object),"published view replaced");
  WorldRegion next=new WorldRegion(1,1,1);cold.removeVisibleObject(object);next.addVisibleObject(object);
  check(cold.getVisibleObjects().isEmpty()&&next.getVisibleObjects().contains(object),"migration");
  for(int x=-2;x<=2;x++)for(int y=-2;y<=2;y++)for(int z=-2;z<=2;z++)
   check(cold.isSurroundingRegion(new WorldRegion(x,y,z))==(Math.abs(x)<=1&&Math.abs(y)<=1&&Math.abs(z)<=1),"adjacency");
  check(!cold.isSurroundingRegion(null),"null adjacency");
  // Exercise the same allocation path for all three fields under a simultaneous first write.
  Method create=WorldRegion.class.getDeclaredMethod("getOrCreateSet",java.lang.invoke.VarHandle.class);create.setAccessible(true);
  ExecutorService pool=Executors.newFixedThreadPool(16);
  try{
   for(String handleName:List.of("VISIBLE_OBJECTS","DOORS","FENCES")){
    Field hf=WorldRegion.class.getDeclaredField(handleName);hf.setAccessible(true);Object handle=hf.get(null);
    for(int round=0;round<20;round++){
     WorldRegion r=new WorldRegion(0,0,0);CountDownLatch start=new CountDownLatch(1);List<Future<Set<?>>> tasks=new ArrayList<>();
     for(int worker=0;worker<16;worker++){final int n=worker;tasks.add(pool.submit(()->{
      start.await();@SuppressWarnings("unchecked") Set<Object> set=(Set<Object>)create.invoke(r,handle);
      for(int k=0;k<100;k++)set.add(n*100+k);return set;
     }));}
     start.countDown();Set<?> first=tasks.get(0).get();for(Future<Set<?>> task:tasks)check(task.get()==first,"publication race");
     check(first.size()==1600,"lost concurrent writes");
    }
   }
  }finally{pool.shutdownNow();}
  System.out.println("PASS: cold reads/removes, retained views, visibility migration, 125 adjacency cases, 60 concurrent first-write rounds / 96000 insertions");
 }
}
