import java.io.File;
import java.lang.instrument.Instrumentation;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.commons.network.buffer.WriteBuffer;
import org.l2jmobius.commons.network.pool.ResourcePool;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.item.ItemTemplate;
import org.l2jmobius.gameserver.mechanics.multisell.ListContainer;
import org.l2jmobius.gameserver.network.serverpackets.MultiSellList;
import org.l2jmobius.gameserver.util.DocumentItem;

/** Modify only seven display IDs, preserving every purchased item and its template object. */
public class FafurionDisplayFixV2 {
    static List<String> report=new ArrayList<>();
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);report.add("PASS "+message);}
    static List<Integer> packetIds(ListContainer list,Path output)throws Exception {
        WriteBuffer out=new WriteBuffer(new ResourcePool(),MultiSellList.class);
        byte[] bytes;
        try {new MultiSellList(list,0).writeImpl(null,out);bytes=out.toByteArray();}
        finally {out.releaseResources();}
        Files.write(output,bytes);
        ByteBuffer b=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        b.get();check(b.getInt()==50035413,"serialized list ID");
        b.getInt();b.getInt();b.getInt();int count=b.getInt();check(count==7,"serialized seven entries");
        List<Integer> ids=new ArrayList<>();
        for(int i=0;i<count;i++) {
            b.getInt();b.getInt();b.getInt();b.get();
            int products=Short.toUnsignedInt(b.getShort()),costs=Short.toUnsignedInt(b.getShort());
            check(products==1 && costs==1,"one product and one cost in serialized entry");
            for(int j=0;j<products;j++){ids.add((int)b.getShort());b.position(b.position()+20);}
            for(int j=0;j<costs;j++){check(b.getShort()==57,"serialized Adena ingredient");b.getShort();check(b.getInt()==48800000,"serialized unchanged NPC price");b.position(b.position()+10);}
        }
        return ids;
    }
    @SuppressWarnings("unchecked")
    public static void agentmain(String directory,Instrumentation inst)throws Exception {
        Path path=Path.of(directory);ItemData items=ItemData.getInstance();
        var field=ItemTemplate.class.getDeclaredField("_displayId");field.setAccessible(true);
        Map<ItemTemplate,Integer> previous=new LinkedHashMap<>();
        try {
            check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"client disconnected before display ID activation");
            DocumentItem parsed=new DocumentItem(path.getParent().getParent().resolve("server/game/data/stats/items/54100-54199.xml").toFile());parsed.parse();
            check(parsed.getItemList().size()==7,"persisted XML parses seven weapons");
            for(ItemTemplate t:parsed.getItemList())check(t.getDisplayId()==t.getId()-30000,"persisted compatible display alias "+t.getId());
            var mf=MultisellData.class.getDeclaredField("_entries");mf.setAccessible(true);
            ListContainer list=((Map<Integer,ListContainer>)mf.get(MultisellData.getInstance())).get(50035413);
            check(list!=null && list.isNpcAllowed(50010),"existing Mirella list and access restriction preserved");
            List<Integer> before=packetIds(list,path.resolve("client-fix-v2/multisell-before.bin"));
            for(int id:before)check(id<0,"reproduced signed-short overflow of old display ID "+id);
            for(int id=54130;id<=54136;id++) {
                ItemTemplate t=items.getTemplate(id);check(t!=null && t.getDisplayId()==id,"original runtime template "+id);
                previous.put(t,t.getDisplayId());field.setInt(t,id-30000);
            }
            List<Integer> after=packetIds(list,path.resolve("client-fix-v2/multisell-after.bin"));
            for(int i=0;i<7;i++)check(after.get(i)==24130+i,"serialized positive compatible display ID "+after.get(i));
            for(var entry:previous.entrySet())check(items.getTemplate(entry.getKey().getId())==entry.getKey(),"template identity preserved "+entry.getKey().getId());
            for(var e:list.getEntries())check(e.getProducts().getFirst().getItemId()>=54130 && e.getProducts().getFirst().getItemId()<=54136,"purchase still awards original server item ID");
            report.add("SUCCESS: stats, prices, item IDs, object IDs and all existing inventories preserved; no database updates");
        }catch(Throwable e){for(var entry:previous.entrySet())field.setInt(entry.getKey(),entry.getValue());report.add("FAILED "+e);throw e;}
        finally {Files.writeString(path.resolve("client-fix-v2/runtime-verification.txt"),String.join("\n",report)+"\n");}
    }
}
