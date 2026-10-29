import java.io.File;
import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.cache.HtmCache;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.mechanics.multisell.ListContainer;

/** Load only two new lists and four edited menus into the running server. */
public class FafurionShopLoad {
    static List<String> report=new ArrayList<>();
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);report.add("PASS "+message);}
    @SuppressWarnings("unchecked")
    public static void agentmain(String directory,Instrumentation inst)throws Exception {
        Path root=Path.of(directory).getParent().getParent(),data=root.resolve("server/game/data");
        try {
            BuyListData buy=BuyListData.getInstance();
            check(buy.getBuyList(54130)==null,"new administrative list ID available");
            buy.parseFile(data.resolve("buylists/54130.xml").toFile());
            var list=buy.getBuyList(54130);check(list!=null && list.getProducts().size()==7,"native admin list contains seven weapons");
            for(int id=54130;id<=54136;id++)check(list.getProductByItemId(id)!=null && list.getProductByItemId(id).getPrice()==0,"GM product and price: "+id);
            MultisellData multi=MultisellData.getInstance();
            var field=MultisellData.class.getDeclaredField("_entries");field.setAccessible(true);
            Map<Integer,ListContainer> lists=(Map<Integer,ListContainer>)field.get(multi);
            check(!lists.containsKey(50035413),"new NPC list ID available");
            multi.parseFile(data.resolve("multisell/custom/50035413.xml").toFile());
            ListContainer npc=lists.get(50035413);
            check(npc!=null && npc.getEntries().size()==7 && npc.isNpcAllowed(50010),"native NPC list contains seven weapons and permits Mirella");
            Set<Integer> ids=new HashSet<>();
            for(var entry:npc.getEntries()) {
                check(entry.getProducts().size()==1 && entry.getIngredients().size()==1,"one weapon per exchange");
                var product=entry.getProducts().getFirst();var cost=entry.getIngredients().getFirst();
                check(product.getItemCount()==1 && ItemData.getInstance().getTemplate(product.getItemId())!=null,"valid registered weapon product "+product.getItemId());
                check(cost.getItemId()==57 && cost.getItemCount()==48800000,"NPC price 48,800,000 Adena");ids.add(product.getItemId());
            }
            for(int id=54130;id<=54136;id++)check(ids.contains(id),"NPC product: "+id);
            for(String rel:List.of("html/merchant/50010.htm","html/merchant/50010-1.htm","html/admin/gmshops.htm","html/admin/gmstore/gear/weapons.htm")) {
                String html=HtmCache.getInstance().loadFile(data.resolve(rel).toFile());
                check(html!=null && html.contains("value=\"Fafurion\"") && html.contains(rel.contains("merchant")?"multisell 50035413":"admin_buy 54130"),"updated live menu "+rel);
            }
            report.add("SUCCESS: only new lists and specified HTML loaded; no restart or character/inventory changes");
        }catch(Throwable e){report.add("FAILED "+e);throw e;}
        finally{Files.writeString(Path.of(directory,"shop-verification.txt"),String.join("\n",report)+"\n");}
    }
}
