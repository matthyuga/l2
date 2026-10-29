import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;

/** Remove diagnostic logging from the validated helper in an idle, client-free server. */
public class GiranChaosReloadOnly {
 static Class<?> find(Instrumentation i,String n){return Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals(n)).findFirst().orElseThrow();}
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  var w=find(i,"org.l2jmobius.gameserver.entity.World");for(Object p:(Collection<?>)w.getMethod("getPlayers").invoke(null))if(p.getClass().getMethod("getClient").invoke(p)!=null)throw new IllegalStateException("Client connected");
  var c=find(i,"custom.GiranSiegeLab.GiranChaosSiege");var f=c.getDeclaredField("instance");f.setAccessible(true);Object scene=f.get(null);
  synchronized(scene){var s=c.getDeclaredField("squads");s.setAccessible(true);if(!((List<?>)s.get(scene)).isEmpty())throw new IllegalStateException("Scene busy");var m=find(i,"custom.GiranSiegeLab.GiranChaosMachinery");i.redefineClasses(new ClassDefinition(m,Files.readAllBytes(Path.of(dir,"custom/GiranSiegeLab/GiranChaosMachinery.class"))));System.err.println("GIRAN_CHAOS_DIAGNOSTIC cleaned helper installed;core unchanged;no scene started");}
 }
}
