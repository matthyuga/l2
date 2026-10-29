import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.config.ServerConfig;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.mechanics.multisell.ListContainer;
public class VerifyShops {
 static class DetachedLists extends MultisellData { @Override public void load(){} }
 @SuppressWarnings("unchecked")
 public static void main(String[] args)throws Exception {
  ServerConfig.DATAPACK_ROOT=Path.of(args[0]).toFile();
  var items=ItemData.getInstance();var multi=new DetachedLists();int count=0,lists=0;
  var f=MultisellData.class.getDeclaredField("_entries");f.setAccessible(true);var entries=(Map<Integer,ListContainer>)f.get(multi);
  var seen=new HashSet<Integer>();
  try(var stream=Files.list(Path.of(args[0],"data/multisell/custom"))){for(var file:stream.filter(p->p.getFileName().toString().startsWith("500370")).toList()){
   multi.parseFile(file.toFile());var list=entries.get(Integer.parseInt(file.getFileName().toString().replace(".xml","")));
   if(list==null||!list.isNpcAllowed(50010))throw new AssertionError("Invalid Mirella list "+file);
   for(var entry:list.getEntries()){
    var product=entry.getProducts().getFirst();var cost=entry.getIngredients().getFirst();int id=product.getItemId();
    if(items.getTemplate(id)==null||product.getTemplate()==null||id>=32768||cost.getItemId()!=57||!seen.add(id))throw new AssertionError("Invalid shop product "+id);
    count++;
   }lists++;
  }}
  Files.writeString(Path.of(args[1]),"SUCCESS: native ItemData loaded "+items.getAllItems().length+" template slots; "+lists+" native multisell lists, "+count+" distinct products, Mirella NPC 50010, positive display IDs below 32768. No server or database started.\n");
  System.out.println("SUCCESS "+lists+" lists "+count+" products");System.exit(0);
 }
}
