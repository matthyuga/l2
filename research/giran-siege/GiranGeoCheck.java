import java.nio.*;
import java.nio.file.*;
import java.util.Arrays;
import org.l2jmobius.gameserver.geoengine.geodata.regions.Region;
/** Standalone native parser check: no DB, no server, no loading human characters. */
public class GiranGeoCheck {
 public static void main(String[] args)throws Exception{
  ByteBuffer b=ByteBuffer.wrap(Files.readAllBytes(Path.of(args[0]))).order(ByteOrder.LITTLE_ENDIAN);Region region=new Region(b);
  if(b.hasRemaining()){byte[] footer=new byte[b.remaining()];b.get(footer);if(!Arrays.equals(footer,new byte[]{75,117,111,106,97}))throw new IllegalStateException("Unknown trailing bytes");System.out.println("Known author footer Kuoja (native loader ignores footer)");}
  for(int t=0;t<5;t++)for(int s=0;s<4;s++)verify(region,"camp "+t+":"+s,110700+s*65,144450+t*260,-2800,true);
  verify(region,"Ares",114174,145058,-2751,true);verify(region,"Nyx",117700,145150,-2544,true);System.out.println("Native23_22parse/22anchor PASS; bytes="+b.position());
 }
 static void verify(Region r,String label,int x,int y,int hint,boolean walkable){
  if((x+655360)/32768!=23||(y+589824)/32768!=22)throw new IllegalStateException("Wrong region "+label);
  int gx=(x+655360)/16,gy=(y+589824)/16,z=r.getNearestZ(gx,gy,hint);boolean open=r.checkNearestNswe(gx,gy,z,15);
  if(z<-4000||z>-1500||walkable&&!open)throw new IllegalStateException("Bad anchor "+label+" z="+z+" nswe="+open);
  System.out.println(label+" x="+x+" y="+y+" floor="+z+" walkable="+open);
 }
}
