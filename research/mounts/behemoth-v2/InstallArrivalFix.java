import java.lang.instrument.*;
import java.lang.invoke.MethodHandles;
import java.nio.file.*;
import java.util.*;
public final class InstallArrivalFix {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  Class<?> type=null;Object service=null;
  for(Class<?> c:inst.getAllLoadedClasses())if(c.getName().equals("custom.BehemothNativeRide.BehemothNativeRide")){var f=c.getDeclaredField("instance");f.setAccessible(true);if(f.get(null)!=null){type=c;service=f.get(null);break;}}
  if(type==null)throw new IllegalStateException("Native module not loaded");
  var lookup=MethodHandles.privateLookupIn(type,MethodHandles.lookup());
  var motion=lookup.defineClass(Files.readAllBytes(Path.of(directory,"NativeRideMotion.class")));
  lookup.defineClass(Files.readAllBytes(Path.of(directory,"NativeRideMotion$State.class")));
  synchronized(service){
   inst.redefineClasses(new ClassDefinition(type,Files.readAllBytes(Path.of(directory,"NativeRideArrivalFixed.class"))));
   var f=type.getDeclaredField("riders");f.setAccessible(true);
   for(Object player:((Map<?,?>)f.get(service)).values()){var p=(org.l2jmobius.gameserver.entity.actor.Player)player;motion.getMethod(p.isMoving()?"tick":"begin",org.l2jmobius.gameserver.entity.actor.Player.class).invoke(null,p);}
  }
  var test=lookup.defineClass(Files.readAllBytes(Path.of(directory,"NativeRideSmokeV2.class")));test.getMethod("run",type).invoke(null,service);
  Files.writeString(Path.of(directory,"arrival-fix-install.txt"),"Explicit StopMove on arrival active; only custom native ride class redefined. Native motion tests complete.\n");
 }
}
