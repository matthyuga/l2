import java.lang.instrument.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import com.sun.tools.attach.VirtualMachine;

/** Local diagnostic reload of the machinery helper only. Never changes core classes. */
public class GiranChaosReload {
 static Class<?> find(Instrumentation i,String name){return Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals(name)).findFirst().orElseThrow();}
 public static void agentmain(String dir,Instrumentation inst)throws Exception {
  var world=find(inst,"org.l2jmobius.gameserver.entity.World");
  var players=(Collection<?>)world.getMethod("getPlayers").invoke(null);
  for(Object p:players)if(p.getClass().getMethod("getClient").invoke(p)!=null)throw new IllegalStateException("Client connected; diagnostic cancelled");
  var sc=find(inst,"custom.GiranSiegeLab.GiranChaosSiege");var f=sc.getDeclaredField("instance");f.setAccessible(true);Object scene=f.get(null);
  synchronized(scene){var sf=sc.getDeclaredField("squads");sf.setAccessible(true);if(!((List<?>)sf.get(scene)).isEmpty())throw new IllegalStateException("Scene busy");
   var mc=find(inst,"custom.GiranSiegeLab.GiranChaosMachinery");inst.redefineClasses(new ClassDefinition(mc,Files.readAllBytes(Path.of(dir,"custom/GiranSiegeLab/GiranChaosMachinery.class"))));
   System.err.println("GIRAN_CHAOS_DIAGNOSTIC machinery helper reloaded from compiled source;core unchanged");
   var vc=find(inst,"custom.GiranSiegeLab.GiranChaosVerification");var ctor=vc.getDeclaredConstructor(sc);ctor.setAccessible(true);Object verification=ctor.newInstance(scene);var method=vc.getDeclaredMethod("whenReady");method.setAccessible(true);method.invoke(verification);
  }
 }
 public static void main(String[] args)throws Exception {
  VirtualMachine vm=VirtualMachine.attach(args[0]);try{vm.loadAgent(Path.of(args[1]).toAbsolutePath().toString(),Path.of(args[2]).toAbsolutePath().toString());}finally{vm.detach();}
 }
}
