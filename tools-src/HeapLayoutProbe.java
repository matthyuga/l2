import java.lang.instrument.*;
import java.nio.file.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.l2jmobius.gameserver.entity.WorldRegion;
public class HeapLayoutProbe {
 public static void agentmain(String dir,Instrumentation i)throws Exception{
  Object[] values={new ConcurrentHashMap<>(),ConcurrentHashMap.newKeySet(),new AtomicInteger(),new Object[0],new Object[27],new byte[0],new short[0],new int[0],new long[0],new WorldRegion[0],new WorldRegion[27]};
  StringBuilder s=new StringBuilder("class,bytes\n");for(Object o:values)s.append(o.getClass().getTypeName()+","+i.getObjectSize(o)+"\n");
  Files.writeString(Path.of(dir,"native-layout.csv"),s.toString());
 }
}
