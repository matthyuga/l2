import java.lang.instrument.Instrumentation;
import java.net.URLClassLoader;
import java.nio.file.*;
import java.util.*;
public final class InstallNativeRide {
 private static URLClassLoader loader;
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  for(Class<?> c:inst.getAllLoadedClasses())if(c.getName().equals("custom.BehemothTransport.BehemothTransport")){var f=c.getDeclaredField("instance");f.setAccessible(true);Object service=f.get(null);if(service==null)continue;f=c.getDeclaredField("owned");f.setAccessible(true);synchronized(service){for(Object trip:List.copyOf(((Map<?,?>)f.get(service)).values())){var close=c.getDeclaredMethod("close",trip.getClass(),String.class);close.setAccessible(true);close.invoke(service,trip,"Cambio al montaje nativo del Behemoth.");}}}
  ClassLoader parent=Class.forName("org.l2jmobius.gameserver.GameServer").getClassLoader();
  loader=new URLClassLoader(new java.net.URL[]{Path.of(directory,"native-ride-runtime.jar").toUri().toURL()},parent);
  var type=Class.forName("custom.BehemothNativeRide.BehemothNativeRide",true,loader);Object service=type.getConstructor().newInstance();
  Class.forName("custom.BehemothNativeRide.NativeRideSmoke",true,loader).getMethod("run",type).invoke(null,service);
  Files.writeString(Path.of(directory,"native-ride-install.txt"),"Native driver module active. Legacy remote-control mounts closed. Smoke complete; native client visual verification pending.\n");
 }
}
