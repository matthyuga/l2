import java.lang.instrument.Instrumentation;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Map;
import org.l2jmobius.gameserver.data.xml.ItemData;
import org.l2jmobius.gameserver.entity.item.ItemTemplate;
import org.l2jmobius.gameserver.entity.item.Weapon;
import org.l2jmobius.gameserver.util.DocumentItem;

/** Explicitly attached transient registration only. Does not grant items or write DB/files in server. */
public class RiflePrototypeItems {
    @SuppressWarnings("unchecked")
    public static void agentmain(String stageDirectory, Instrumentation instrumentation) throws Exception {
        Path directory = Path.of(stageDirectory).toAbsolutePath().normalize();
        Path xml = directory.resolve("32580-rifle-prototypes.xml");
        if (!Files.isRegularFile(xml)) throw new IllegalArgumentException("Missing staged XML: " + xml);
        DocumentItem document = new DocumentItem(xml.toFile());
        document.parse();
        var prototypes = document.getItemList();
        if (prototypes.isEmpty()) throw new IllegalArgumentException("No prototype items parsed");
        Path runtimeXml=Path.of("data/stats/items/32580-rifle-prototypes.xml").toAbsolutePath().normalize();
        if(!Files.isRegularFile(runtimeXml) || !java.util.Arrays.equals(Files.readAllBytes(runtimeXml),Files.readAllBytes(xml)))throw new IllegalStateException("Runtime XML missing or differs from staged prototype");
        ItemData data = ItemData.getInstance();
        Field templatesField = ItemData.class.getDeclaredField("_allTemplates");
        Field weaponsField = ItemData.class.getDeclaredField("_weapons");
        templatesField.setAccessible(true);
        weaponsField.setAccessible(true);
        synchronized (data) {
            ItemTemplate[] original = (ItemTemplate[]) templatesField.get(data);
            Map<Integer, Weapon> weapons = (Map<Integer, Weapon>) weaponsField.get(data);
            int highest = original.length - 1;
            java.util.HashSet<Integer> seen = new java.util.HashSet<>();
            for (ItemTemplate item : prototypes) {
                int id = item.getId();
                if (!(item instanceof Weapon) || id < 32580 || id > 32589 || !seen.add(id))
                    throw new IllegalStateException("Invalid or duplicate prototype: " + id);
                if (data.getTemplate(id) != null || weapons.containsKey(id))
                    throw new IllegalStateException("Existing item id: " + id);
                highest = Math.max(highest, id);
            }
            ItemTemplate[] updated = Arrays.copyOf(original, highest + 1);
            try {
                for (ItemTemplate item : prototypes) {
                    updated[item.getId()] = item;
                    weapons.put(item.getId(), (Weapon) item);
                }
                templatesField.set(data, updated);
                for(int n=0;n<original.length;n++)if(original[n]!=null && updated[n]!=original[n])throw new IllegalStateException("Unrelated template changed");
                Field fileListField=ItemData.class.getDeclaredField("_itemFiles");fileListField.setAccessible(true);
                java.util.List<java.io.File> itemFiles=(java.util.List<java.io.File>)fileListField.get(data);
                if(itemFiles.stream().noneMatch(f->f.toPath().toAbsolutePath().normalize().equals(runtimeXml)))itemFiles.add(runtimeXml.toFile());
            } catch (Exception error) {
                templatesField.set(data, original);
                for (ItemTemplate item : prototypes) weapons.remove(item.getId());
                throw error;
            }
        }
        Files.writeString(directory.resolve("registration.log"),
            "REGISTERED transient templates: " + prototypes.stream().map(x -> Integer.toString(x.getId())).toList()
            + "\nNo item grants, no character changes, no server XML or database writes.\n"
            + "Runtime XML also registered for reload; new templates persist on subsequent startup/reload. Existing template identities verified unchanged.\n");
    }
}
