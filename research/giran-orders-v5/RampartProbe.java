import java.nio.*;import java.nio.file.*;
import org.l2jmobius.gameserver.geoengine.geodata.regions.Region;
public class RampartProbe{
 public static void main(String[] args)throws Exception{Region r=new Region(ByteBuffer.wrap(Files.readAllBytes(Path.of(args[0]))).order(ByteOrder.LITTLE_ENDIAN));
  for(int y:new int[]{144640,144720,144800,144880,144960,145040}){System.out.println("Y="+y);for(int x=112720;x<=113136;x+=32){int gx=(x+655360)/16,gy=(y+589824)/16;StringBuilder row=new StringBuilder(x+":");for(int hint:new int[]{-2832,-2500,-2300,-2000}){int z=r.getNearestZ(gx,gy,hint),mask=0;for(int n:new int[]{1,2,4,8})if(r.checkNearestNswe(gx,gy,z,n))mask|=n;row.append(" ").append(z).append("/").append(mask);}System.out.println(row);}}
 }
}
