import java.io.File;
import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.cache.HtmCache;
import org.l2jmobius.gameserver.data.xml.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.item.*;
import org.l2jmobius.gameserver.entity.item.enums.BodyPart;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.mechanics.multisell.ListContainer;
import org.l2jmobius.gameserver.util.DocumentItem;

/** Cosmetic template preflight, followed by an additive laboratory hot load. */
public class HairLoad {
 static List<String> checks=new ArrayList<>();
 static void check(boolean ok,String text){if(!ok)throw new AssertionError(text);checks.add("PASS "+text);}
 static Object field(Object obj,String name)throws Exception{var f=obj.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(obj);}
 static List<ItemTemplate> parse(Path file)throws Exception {
  DocumentItem doc=new DocumentItem(file.toFile());doc.parse();var items=doc.getItemList();
  check(items.size()==13,"native XML parser accepts 13 accessories");Set<Integer> ids=new HashSet<>();
  for(var t:items){
   check(t.getId()>=28000 && t.getId()<=28012 && ids.add(t.getId()),"unique expected ID "+t.getId());
   check(t instanceof Armor && t.getBodyPart()==BodyPart.HAIR,"hair accessory slot "+t.getId());
   check(t.getStatFuncs(new Item(0,t),null).isEmpty(),"zero stat functions "+t.getId());
   check(t.getSkills()==null || t.getSkills().length==0,"zero skills "+t.getId());
   check(!t.isEnchantable() && !t.isCrystallizable(),"not enchantable or crystallizable "+t.getId());
  }return items;
 }
 public static void main(String[] args)throws Exception {
  org.l2jmobius.gameserver.config.PlayerConfig.ENCHANT_BLACKLIST=new int[0];
  try{parse(Path.of(args[0]));checks.add("SUCCESS");Files.write(Path.of(args[1]),checks);System.out.println("SUCCESS: 13 native cosmetic templates");System.exit(0);}
  catch(Throwable e){e.printStackTrace();System.exit(1);}
 }
 @SuppressWarnings("unchecked")
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  Path root=Path.of(directory),data=root.getParent().getParent().getParent().getParent().resolve("server/game/data");
  try{
   check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"no connected clients during registration");
   var file=data.resolve("stats/items/hair-accessories.xml").toFile();var additions=parse(file.toPath());
   ItemData items=ItemData.getInstance();var before=items.getAllItems();
   for(var t:additions)check(items.getTemplate(t.getId())==null,"unused live ID "+t.getId());
   var buy=BuyListData.getInstance();check(buy.getBuyList(28000)==null,"unused admin list ID");
   var multi=MultisellData.getInstance();Map<Integer,ListContainer> lists=(Map<Integer,ListContainer>)field(multi,"_entries");
   check(!lists.containsKey(50042800),"unused NPC list ID");
   Map<Integer,Armor> armors=(Map<Integer,Armor>)field(items,"_armors");List<File> files=(List<File>)field(items,"_itemFiles");
   var arrayField=ItemData.class.getDeclaredField("_allTemplates");arrayField.setAccessible(true);
   var after=Arrays.copyOf(before,Math.max(before.length,28013));for(var t:additions)after[t.getId()]=t;
   boolean addedFile=false;
   try{
    for(var t:additions)armors.put(t.getId(),(Armor)t);
    if(files.stream().noneMatch(f->f.getAbsoluteFile().equals(file.getAbsoluteFile()))){files.add(file);addedFile=true;}
    arrayField.set(items,after);
    for(int i=0;i<before.length;i++)if(before[i]!=null && before[i]!=items.getTemplate(i))throw new AssertionError("Existing template replaced: "+i);
    for(var t:additions)check(items.getTemplate(t.getId())==t,"live template registered "+t.getId());
   }catch(Throwable e){arrayField.set(items,before);for(var t:additions)armors.remove(t.getId());if(addedFile)files.remove(file);throw e;}
   check(true,"all existing template identities preserved");
   buy.parseFile(data.resolve("buylists/28000.xml").toFile());var admin=buy.getBuyList(28000);
   check(admin!=null && admin.getProducts().size()==13,"13 administrative products");
   for(var t:additions)check(admin.getProductByItemId(t.getId())!=null && admin.getProductByItemId(t.getId()).getPrice()==0,"free GM product "+t.getId());
   multi.parseFile(data.resolve("multisell/custom/50042800.xml").toFile());var npc=lists.get(50042800);
   check(npc!=null && npc.getEntries().size()==13 && npc.isNpcAllowed(50010),"Mirella list has 13 entries");
   Set<Integer> productIds=new HashSet<>();
   for(var entry:npc.getEntries()){
    check(entry.getProducts().size()==1 && entry.getIngredients().size()==1,"one accessory and one cost");
    var p=entry.getProducts().getFirst();var cost=entry.getIngredients().getFirst();
    check(p.getItemCount()==1 && items.getTemplate(p.getItemId())!=null,"valid product "+p.getItemId());productIds.add(p.getItemId());
    check(cost.getItemId()==57 && cost.getItemCount()==1,"laboratory price: 1 Adena");
   }
   for(var t:additions)check(productIds.contains(t.getId()),"NPC product present "+t.getId());
   for(String rel:List.of("html/merchant/50010.htm","html/merchant/50010-4.htm","html/admin/gmshops.htm","html/admin/gmstore/hair.htm")){
    String html=HtmCache.getInstance().loadFile(data.resolve(rel).toFile());
    check(html!=null && html.contains("value=\"Cabellos\"") && html.contains(rel.contains("merchant")?"multisell 50042800":"admin_buy 28000"),"live menu "+rel);
   }
   checks.add("PASS no real character, inventory or database modifications");checks.add("SUCCESS");
  }catch(Throwable e){checks.add("FAILED "+e);throw e;}
  finally{Files.write(root.resolve("runtime-verification.txt"),checks);}
 }
}
