package custom.ExplorationWalking;
import java.nio.file.*;
public class NativeZonesTest {
    static int checks;static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
    static void at(NativeExplorationZones zones,int x,int y,int z,String expected){var found=zones.find(x,y,z);check(found!=null);check(found.name.equals(expected));}
    public static void main(String[] args)throws Exception{
        var zones=new NativeExplorationZones(Path.of(args[0]));check(zones.size()==362);check(zones.maskCount()==204);
        at(zones,83400,147800,-3400,"Giran Castle Town");at(zones,147725,-56517,-2780,"Town  of Goddard");
        at(zones,146990,-67128,-3640,"Goddard Territory");at(zones,137500,-90200,-3600,"Ketra Orc Outpost");
        at(zones,149548,-82014,-5592,"Ketra Orc Village");
        at(zones,114649,11115,-5120,"Tower of Insolence: 1st Floor");at(zones,114649,11115,-3000,"Tower of Insolence: 2nd Floor");
        at(zones,-83063,150791,-3133,"Gludin Village");
        check(zones.find(137500,-90200,30000)==null);check(zones.find(137500,-90200,-30000)==null);
        check(zones.find(900000,900000,0)==null);
        // Each represented zone/color/height combination must round-trip through a mask pixel.
        var factory=javax.xml.parsers.DocumentBuilderFactory.newInstance();
        var xml=factory.newDocumentBuilder().parse(Path.of(args[0],"native-zones.xml").toFile()).getElementsByTagName("zone");
        int reached=0;java.util.Set<String> names=new java.util.HashSet<>();
        java.nio.ByteBuffer raw=java.nio.ByteBuffer.wrap(Files.readAllBytes(Path.of(args[0],"zone-masks.bin"))).order(java.nio.ByteOrder.LITTLE_ENDIAN);
        raw.position(8);int count=raw.getInt();java.util.Map<String,byte[]> masks=new java.util.HashMap<>();
        for(int i=0;i<count;i++){int tx=raw.getInt(),ty=raw.getInt();byte[] p=new byte[16384];raw.get(p);masks.put(tx+","+ty,p);}
        for(int i=0;i<xml.getLength();i++){
            var e=(org.w3c.dom.Element)xml.item(i);int color=Integer.parseInt(e.getAttribute("color"));
            int tx=Integer.parseInt(e.getAttribute("tileX")),ty=Integer.parseInt(e.getAttribute("tileY"));
            double bottom=Double.parseDouble(e.getAttribute("bottom")),top=Double.parseDouble(e.getAttribute("top"));
            int z=(int)Math.floor((bottom+top)/2);if(z<=bottom)z=(int)Math.floor(bottom)+1;
            if(z>=top){System.out.println("Inactive integer-height interval: record "+e.getAttribute("record")+" "+e.getAttribute("name"));continue;}
            boolean matched=false;
            for(var tile:masks.entrySet()){
                String[] coordinates=tile.getKey().split(",");int mx=Integer.parseInt(coordinates[0]),my=Integer.parseInt(coordinates[1]);
                if(color>=200&&(mx!=tx||my!=ty))continue;
                byte[] pixels=tile.getValue();
                for(int j=0;j<pixels.length;j++)if((pixels[j]&255)==color){
                    var actual=zones.find((mx-20)*32768+(j%128)*256+128,(my-18)*32768+(j/128)*256+128,z);
                    if(actual==null)throw new AssertionError("Record "+e.getAttribute("record")+" no match for "+e.getAttribute("name")+" color="+color+" tile="+mx+","+my+" at z="+z);checks++;if(!actual.name.equals(e.getAttribute("name")))throw new AssertionError("Record "+e.getAttribute("record")+" expected "+e.getAttribute("name")+" got "+actual.name+" at z="+z);checks++;matched=true;break;
                }
                if(matched)break;
            }
            if(matched){reached++;names.add(e.getAttribute("name"));}
        }
        System.out.println("Represented records="+reached+", names="+names.size());
        check(reached==354);check(names.size()==240);
        System.out.println("PASS "+checks+" checks: native places, negative coordinates, vertical floors, strict height bounds and full mask-referenced catalogue.");
    }
}
