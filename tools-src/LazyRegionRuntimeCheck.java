import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.*;
import org.l2jmobius.gameserver.entity.actor.enums.creature.FenceState;
import org.l2jmobius.gameserver.managers.IdManager;
public class LazyRegionRuntimeCheck {
 static class Marker extends WorldObject {
  Marker(){super(IdManager.getInstance().getNextId());}
  public boolean isAutoAttackable(Creature c){return false;}
  public void sendInfo(Player p){}
 }
 static void check(boolean ok,String reason){if(!ok)throw new AssertionError(reason);}
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"Client connected; diagnostic cancelled");
  int doors=0,objects=World.getVisibleObjects().size(),spawned=0;
  for(WorldObject o:World.getVisibleObjects()){
   if(!o.isSpawned())continue; // The registry also holds offline roster profiles.
   check(o.getWorldRegion()!=null&&o.getWorldRegion().getVisibleObjects().contains(o),"Missing region membership "+o.getObjectId());spawned++;
   if(o instanceof Door d){doors++;for(WorldRegion r:d.getWorldRegion().getSurroundingRegions())check(r.getDoors().contains(d),"Door missing in neighbor");}
  }
  check(doors==547,"Door count changed");
  Marker a=new Marker(),b=new Marker();
  Fence fence=new Fence(83020,147880,"temporary-region-check",50,50,1,FenceState.CLOSED);
  try{
   a.spawnMe(83020,147880,-3469);b.spawnMe(83030,147880,-3469);
   fence.spawnMe(83020,147880,-3469);
   WorldRegion[] fenceRegions=fence.getWorldRegion().getSurroundingRegions();
   for(WorldRegion r:fenceRegions)check(r.getFences().contains(fence),"Fence missing in neighbor");
   fence.decayMe();for(WorldRegion r:fenceRegions)check(!r.getFences().contains(fence),"Fence removal failed");
   Set<WorldObject> seen=new HashSet<>();World.forEachVisibleObject(a,WorldObject.class,seen::add);check(seen.contains(b),"Nearby visibility missing");
   WorldRegion old=b.getWorldRegion();b.setXYZ(114800,145000,-2832);
   check(!old.getVisibleObjects().contains(b)&&b.getWorldRegion().getVisibleObjects().contains(b),"Moving between regions failed");
   seen.clear();World.forEachVisibleObject(a,WorldObject.class,seen::add);check(!seen.contains(b),"Remote object still visible");
   b.decayMe();WorldRegion siege=b.getWorldRegion();b.spawnMe(-82000,243000,-3700);
   check(!siege.getVisibleObjects().contains(b)&&b.getWorldRegion().getVisibleObjects().contains(b),"Talking Island respawn failed");
   b.decayMe();b.spawnMe(83030,147880,-3469);seen.clear();World.forEachVisibleObject(a,WorldObject.class,seen::add);check(seen.contains(b),"Visibility after return failed");
  }finally{a.decayMe();b.decayMe();fence.decayMe();IdManager.getInstance().releaseId(a.getObjectId());IdManager.getInstance().releaseId(b.getObjectId());IdManager.getInstance().releaseId(fence.getObjectId());}
  check(World.getVisibleObjects().size()==objects,"Temporary objects leaked");
  Files.writeString(Path.of(dir,"region-runtime-check.txt"),"PASS\nall_spawned_objects_have_region_membership="+spawned+"\nall_547_doors_propagated_to_neighbors=true\nfence_neighbor_add_and_remove=true\nnearby_and_remote_visibility=true\nmovement_giran_to_siege=true\nrespawn_talking_island_and_return=true\ntemporary_objects_removed=true\n");
 }
}
