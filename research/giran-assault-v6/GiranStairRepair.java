import java.nio.*;import java.nio.file.*;import java.util.*;
import org.l2jmobius.gameserver.config.GeoEngineConfig;
import org.l2jmobius.gameserver.geoengine.geodata.regions.Region;
/** Restore east/west links of the existing north staircase; heights and other collision bits stay intact. */
public class GiranStairRepair{
 public static void main(String[] args)throws Exception{
  byte[] original=Files.readAllBytes(Path.of(args[0]));Region region=new Region(ByteBuffer.wrap(original).order(ByteOrder.LITTLE_ENDIAN));
  int y=(145064+589824)/16,start=(117528+655360)/16,end=(117950+655360)/16,changed=0;
  for(int x=start;x<end;x++){int z=region.getNearestZ(x,y,-2544),nz=region.getNearestZ(x+1,y,-2544);if(Math.abs(z-nz)>40)throw new IllegalStateException("Not a stair step: "+x+" "+z+" -> "+nz);
   if(!region.checkNearestNswe(x,y,z,1)){region.setNearestNswe(x,y,z,(byte)1);changed++;}
   if(!region.checkNearestNswe(x+1,y,nz,2)){region.setNearestNswe(x+1,y,nz,(byte)2);changed++;}
  }
  Path dest=Path.of(args[1]).toAbsolutePath();Files.createDirectories(dest.getParent());GeoEngineConfig.GEOEDIT_PATH=dest.getParent();if(!region.saveToFile(dest.getFileName().toString()))throw new IllegalStateException("Save failed");
  byte[] out=Files.readAllBytes(dest);if(original.length==out.length+5&&Arrays.equals(Arrays.copyOfRange(original,original.length-5,original.length),new byte[]{75,117,111,106,97})){out=Arrays.copyOf(out,original.length);System.arraycopy(original,original.length-5,out,out.length-5,5);Files.write(dest,out);}
  if(out.length!=original.length)throw new IllegalStateException("Layout changed");int bytes=0;for(int i=0;i<out.length;i++)if(out[i]!=original[i]){if(((out[i]^original[i])&0xfc)!=0)throw new IllegalStateException("Changed non E/W bits or height at "+i);bytes++;}
  if(bytes>54||bytes==0)throw new IllegalStateException("Unexpected repair extent "+bytes);System.out.println("STAIR_REPAIR links="+changed+" changedBytes="+bytes+"; existing heights/layout, N/S bits and all other cells preserved; y145064,x117528..117960 only.");
 }
}
