import java.lang.instrument.*;
import java.lang.invoke.*;
import java.nio.file.*;
import java.util.*;
public class MultiRoomCapacityAttach20261022 {
 public static void agentmain(String directory,Instrumentation i)throws Exception{
  Class<?> anchor=Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals("custom.ElvenPvpRoom.PvpRoundRooms")).findFirst().orElseThrow();
  var lookup=MethodHandles.privateLookupIn(anchor,MethodHandles.lookup());
  byte[] bytes=Files.readAllBytes(Path.of(directory,"classes/custom/ElvenPvpRoom/MultiRoomCapacity20261022.class"));
  Class<?> test=Arrays.stream(i.getAllLoadedClasses()).filter(c->c.getName().equals("custom.ElvenPvpRoom.MultiRoomCapacity20261022")).findFirst().orElse(null);
  if(test==null)test=lookup.defineClass(bytes);else i.redefineClasses(new ClassDefinition(test,bytes));
  test.getMethod("start",String.class).invoke(null,directory);
 }
}
