import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;

/** Load only the opt-in experiment into the existing script loader; no core redefinition. */
public class CapacityBenchAttachProtected {
 public static void agentmain(String directory,Instrumentation i)throws Exception{
  var anchor=Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals("custom.GiranSiegeLab.GiranSiegeLab")).findFirst().orElseThrow();
  Path root=Path.of(directory),file=root.resolve("classes/custom/GiranSiegeLab/GiranCapacityBenchProtected.class");
  var lookup=MethodHandles.privateLookupIn(anchor,MethodHandles.lookup());Class<?> test=lookup.defineClass(Files.readAllBytes(file));test.getMethod("start",String.class).invoke(null,root.toString());
 }
}
