package custom.ExplorationWalking;
import java.util.Base64;
import java.util.BitSet;

/** Fixed, versioned continental grid shared by server and client. */
public final class FogGrid {
    public static final int COLS=100,ROWS=150,CELL=4096,MIN_X=-131072,MIN_Y=-262144,BYTES=1875;
    public static BitSet decode(String encoded) {
        if(encoded==null||encoded.isEmpty())return new BitSet(COLS*ROWS);
        byte[] data=Base64.getDecoder().decode(encoded);
        if(data.length>BYTES)throw new IllegalArgumentException("Fog grid exceeds bounds");
        return BitSet.valueOf(data);
    }
    public static String encode(BitSet bits){return Base64.getEncoder().encodeToString(bits.toByteArray());}
    public static int column(int x){return Math.floorDiv(x-MIN_X,CELL);}
    public static int row(int y){return Math.floorDiv(y-MIN_Y,CELL);}
    public static boolean reveal(BitSet bits,int x,int y) {
        int col=column(x),row=row(y);if(col<0||col>=COLS||row<0||row>=ROWS)return false;
        int before=bits.cardinality();
        // Reveal around the position, never a line from the previous position: teleports do not survey the route.
        for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){
            int cx=col+dx,cy=row+dy;if(cx>=0&&cx<COLS&&cy>=0&&cy<ROWS)bits.set(cy*COLS+cx);
        }
        return before!=bits.cardinality();
    }
    public static String packet(int playerId,long sequence,BitSet global,BitSet personal) {
        String text="#NXFOG4|"+playerId+"|"+sequence+"|"+encode(global)+"|"+encode(personal);
        if(text.length()>5500)throw new IllegalStateException("Fog snapshot too large");return text;
    }
    public static String[] packets(int playerId,long sequence,BitSet global,BitSet personal) {
        String snapshot=packet(playerId,sequence,global,personal);
        int count=(snapshot.length()+63)/64;
        String[] parts=new String[count];
        for(int i=0;i<count;i++)parts[i]="#NXFC4|"+playerId+"|"+sequence+"|"+i+"|"+count+"|"+snapshot.substring(i*64,Math.min(snapshot.length(),(i+1)*64));
        return parts;
    }
}
