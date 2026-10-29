import java.io.File;
import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.data.xml.ItemData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.item.*;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.mechanics.stats.functions.AbstractFunction;
import org.l2jmobius.gameserver.util.DocumentItem;

/** Add seven data templates to the running laboratory, without replacing existing templates. */
public class FafurionLoad {
    static List<String> checks=new ArrayList<>();
    static void check(boolean ok,String text){if(!ok)throw new AssertionError(text);checks.add("PASS "+text);}
    static Object field(Object owner,String name)throws Exception{var f=owner.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(owner);}
    static List<String> stats(ItemTemplate template) {
        Item sample=new Item(0,template);
        return template.getStatFuncs(sample,null).stream().map(f->f.getClass().getSimpleName()+":"+f.getStat()+":"+f.getOrder()+":"+f.getValue()).sorted().toList();
    }
    @SuppressWarnings("unchecked")
    public static void agentmain(String directory,Instrumentation instrumentation)throws Exception {
        Path output=Path.of(directory,"runtime-verification.txt");
        try {
            check(World.getPlayers().stream().noneMatch(p->p.getClient()!=null),"no connected clients during template registration");
            File file=Path.of(directory).getParent().getParent().resolve("server/game/data/stats/items/54100-54199.xml").toFile();
            DocumentItem doc=new DocumentItem(file);doc.parse();
            List<ItemTemplate> additions=doc.getItemList();check(additions.size()==7,"native parser accepts all seven XML weapons");
            int[] baseIds={6365,6364,6371,6366,6367,6370,6580};
            ItemData data=ItemData.getInstance();ItemTemplate[] before=data.getAllItems();
            for(int i=0;i<7;i++) {
                int id=54130+i;
                ItemTemplate item=additions.stream().filter(t->t.getId()==id).findFirst().orElseThrow();
                check(item instanceof Weapon && data.getTemplate(id)==null,"new weapon ID available: "+id);
                Weapon weapon=(Weapon)item,base=(Weapon)data.getTemplate(baseIds[i]);
                check(weapon.getItemType()==base.getItemType() && weapon.isMagicWeapon()==base.isMagicWeapon(),"weapon type and magic flag: "+id);
                check(stats(item).equals(stats(base)),"native stat functions match S base: "+id);
                check(weapon.getEnchant4Skill()==null,"no inherited enchant +4 special: "+id);
                int count=item.getSkills()==null?0:item.getSkills().length;
                check(count==(id==54135?1:0),"only normal polearm multiattack is retained: "+id);
                checks.add("STATS "+id+" "+item.getName()+" "+stats(item));
            }
            Map<Integer,Weapon> weapons=(Map<Integer,Weapon>)field(data,"_weapons");
            List<File> files=(List<File>)field(data,"_itemFiles");
            var arrayField=ItemData.class.getDeclaredField("_allTemplates");arrayField.setAccessible(true);
            ItemTemplate[] after=Arrays.copyOf(before,Math.max(before.length,54137));
            for(ItemTemplate item:additions)after[item.getId()]=item;
            boolean addedFile=false;
            try {
                for(ItemTemplate item:additions)weapons.put(item.getId(),(Weapon)item);
                if(files.stream().noneMatch(f->f.getAbsoluteFile().equals(file.getAbsoluteFile()))){files.add(file);addedFile=true;}
                arrayField.set(data,after);
                for(int i=0;i<before.length;i++)check(before[i]==null||before[i]==data.getTemplate(i),"preserved existing template "+i);
                for(ItemTemplate item:additions)check(data.getTemplate(item.getId())==item,"registered runtime weapon "+item.getId());
            }catch(Throwable e){arrayField.set(data,before);for(ItemTemplate item:additions)weapons.remove(item.getId());if(addedFile)files.remove(file);throw e;}
            checks.removeIf(s->s.startsWith("PASS preserved existing template "));
            checks.add("PASS all existing template identities preserved; no character/inventory/database modifications");
            checks.add("SUCCESS");
        }catch(Throwable e){checks.add("FAILED "+e);throw e;}
        finally{Files.writeString(output,String.join("\n",checks)+"\n");}
    }
}
