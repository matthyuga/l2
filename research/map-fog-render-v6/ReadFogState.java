import java.nio.file.*;import java.util.*;import java.sql.*;
public class ReadFogState {
 public static void main(String[] args)throws Exception{
  Properties p=new Properties();try(var r=Files.newBufferedReader(Path.of("E:/l2-local/server/game/config/Database.ini"))){p.load(r);}
  Class.forName(p.getProperty("Driver"));
  try(var c=DriverManager.getConnection(p.getProperty("URL"),p.getProperty("Login"),p.getProperty("Password"))){
   c.setReadOnly(true);
   try(var s=c.prepareStatement("SELECT var,val FROM character_variables WHERE charId=? AND var IN ('FOG4_PERSONAL','FOG4_PAUSED')")){
    s.setInt(1,268473899);try(var r=s.executeQuery()){while(r.next()){
     String key=r.getString(1),v=r.getString(2);
     if(key.equals("FOG4_PERSONAL")){
      var bits=BitSet.valueOf(Base64.getDecoder().decode(v));System.out.println("Persisted personal cells="+bits.cardinality());
      for(int[] xy:new int[][]{{83400,147800},{147725,-56517},{137500,-90200}}){int col=Math.floorDiv(xy[0]+131072,4096),row=Math.floorDiv(xy[1]+262144,4096);System.out.println("Visited "+xy[0]+","+xy[1]+"="+bits.get(row*100+col));}
     }else System.out.println("Paused="+v);
    }}
   }
  }
 }
}
