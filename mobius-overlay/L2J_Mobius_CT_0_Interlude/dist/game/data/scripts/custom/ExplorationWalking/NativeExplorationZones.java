package custom.ExplorationWalking;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;

/** Read-only reconstruction of the client's native P8 zone-mask lookup. */
public final class NativeExplorationZones {
    public static final class Zone {
        public final String id,name;public final int record,color;
        final double bottom,top;
        Zone(Element e){id=e.getAttribute("id");name=e.getAttribute("name");record=num(e,"record");color=num(e,"color");bottom=Double.parseDouble(e.getAttribute("bottom"));top=Double.parseDouble(e.getAttribute("top"));}
        boolean height(int z){return z>bottom&&z<top;}
    }
    private static int num(Element e,String key){return Integer.parseInt(e.getAttribute(key));}
    private static long tile(int x,int y){return ((long)x<<32)|(y&0xffffffffL);}
    private static long key(int color,int x,int y){return color<200?color:((long)y<<16)|((long)x<<8)|color;}
    private final Map<Long,byte[]> masks=new HashMap<>();
    private final Map<Long,List<Zone>> zones=new HashMap<>();
    private int records;
    public NativeExplorationZones(Path directory)throws Exception {
        var factory=DocumentBuilderFactory.newInstance();factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl",true);
        var elements=factory.newDocumentBuilder().parse(directory.resolve("native-zones.xml").toFile()).getElementsByTagName("zone");
        Set<Integer> ids=new HashSet<>();
        for(int i=0;i<elements.getLength();i++){
            Element e=(Element)elements.item(i);Zone z=new Zone(e);
            if(z.name.isBlank()||z.color<0||z.color>255||z.bottom>=z.top||!ids.add(z.record))throw new IllegalArgumentException("Invalid native zone");
            zones.computeIfAbsent(key(z.color,num(e,"tileX"),num(e,"tileY")),k->new ArrayList<>()).add(z);records++;
        }
        ByteBuffer b=ByteBuffer.wrap(Files.readAllBytes(directory.resolve("zone-masks.bin"))).order(ByteOrder.LITTLE_ENDIAN);
        byte[] magic=new byte[8];b.get(magic);if(!Arrays.equals(magic,new byte[]{'N','X','Z','O','N','E','5',0}))throw new IllegalArgumentException("Invalid mask header");
        int count=b.getInt();if(count<1||count>1000||b.remaining()!=count*(8+16384))throw new IllegalArgumentException("Invalid mask length");
        for(int i=0;i<count;i++){int x=b.getInt(),y=b.getInt();byte[] pixels=new byte[16384];b.get(pixels);if(masks.put(tile(x,y),pixels)!=null)throw new IllegalArgumentException("Duplicate tile");}
    }
    public int size(){return records;}
    public int maskCount(){return masks.size();}
    public Zone find(int x,int y,int z){
        int tx=Math.floorDiv(x,32768)+20,ty=Math.floorDiv(y,32768)+18;
        byte[] pixels=masks.get(tile(tx,ty));if(pixels==null)return null;
        int px=Math.floorMod(x,32768)/256,py=Math.floorMod(y,32768)/256;
        int color=pixels[py*128+px]&255;
        List<Zone> candidates=zones.get(key(color,tx,ty));
        if(candidates!=null)for(Zone candidate:candidates)if(candidate.height(z))return candidate;
        return null;
    }
}
