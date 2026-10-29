import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import org.l2jmobius.commons.database.DatabaseFactory;
public class OfflinePosition {
 public static void agentmain(String dir,Instrumentation i)throws Exception {
  try(var c=DatabaseFactory.getConnection();var s=c.prepareStatement("SELECT x,y,z,heading FROM characters WHERE char_name=?")){
   s.setString(1,"Hellkevin");try(var r=s.executeQuery()){
    if(r.next())Files.writeString(Path.of(dir,"example-position.txt"),r.getInt(1)+","+r.getInt(2)+","+r.getInt(3)+","+r.getInt(4));
   }
  }
 }
}
