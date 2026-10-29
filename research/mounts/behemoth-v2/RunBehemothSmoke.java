import java.lang.instrument.Instrumentation;
import java.lang.invoke.MethodHandles;
import java.nio.file.*;
public final class RunBehemothSmoke {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  Class<?> service=null;
  for(Class<?> c:inst.getAllLoadedClasses())if(c.getName().equals("custom.BehemothTransport.BehemothTransport")){service=c;break;}
  if(service==null)throw new IllegalStateException("Behemoth service not loaded");
  var field=service.getDeclaredField("instance");field.setAccessible(true);Object instance=field.get(null);
  Class<?> test=MethodHandles.privateLookupIn(service,MethodHandles.lookup()).defineClass(Files.readAllBytes(Path.of(directory,"BehemothSmokeV2.class")));
  var run=test.getDeclaredMethod("run",service);run.setAccessible(true);run.invoke(null,instance);
 }
}
