package custom.ExplorationWalking;
import java.util.*;
public class FogGridTest {
    static int checks;static void check(boolean v){checks++;if(!v)throw new AssertionError("Check "+checks);}
    public static void main(String[] args) throws Exception{
        BitSet a=new BitSet(),b=new BitSet();check(FogGrid.reveal(a,83400,147800));check(a.cardinality()==9);
        check(!FogGrid.reveal(a,83401,147801));check(FogGrid.reveal(a,147725,-56517));check(a.cardinality()==18);
        check(b.isEmpty());BitSet global=(BitSet)a.clone();global.or(b);check(global.cardinality()==18&&b.isEmpty());
        check(FogGrid.decode(FogGrid.encode(a)).equals(a));
        check(!FogGrid.reveal(a,-131073,147800));check(!FogGrid.reveal(a,500000,147800));
        check(a.cardinality()==18);check(FogGrid.reveal(b,FogGrid.MIN_X,FogGrid.MIN_Y));check(b.cardinality()==4);
        BitSet full=new BitSet();full.set(0,15000);check(FogGrid.packet(123,1,full,full).length()<5500);
        check(FogGrid.decode(FogGrid.encode(full)).cardinality()==15000);
        for(String p:FogGrid.packets(268473899,123,full,full))check(p.length()<128);
        if(args.length==1)java.nio.file.Files.write(java.nio.file.Path.of(args[0]),Arrays.asList(FogGrid.packets(268473899,123,global,a)));
        try{FogGrid.decode(Base64.getEncoder().encodeToString(new byte[1876]));throw new AssertionError();}catch(IllegalArgumentException expected){checks++;}
        System.out.println("PASS "+checks+" grid checks: walking, destination-only teleport, player isolation, persistence encoding and bounded snapshots.");
        System.out.println(FogGrid.packet(123,1,global,a));
    }
}
