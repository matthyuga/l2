import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.data.xml.NpcData;
public class LabelRuntimeCheck {
    public static void agentmain(String dir, Instrumentation ignored) throws Exception {
        List<String> report = new ArrayList<>();
        try {
            var template = NpcData.getInstance().getTemplate(902530);
            if (template == null || template.getDisplayId() != 59030 || !template.isUndying())
                throw new AssertionError("Wrong test template");
            int count = 0;
            for (var obj : World.getVisibleObjects()) {
                if (obj instanceof Npc npc && npc.getId() == 902530) {
                    count++;
                    if (npc.getX() != 149140 || npc.getY() != 46700 || npc.getZ() != -3400)
                        throw new AssertionError("Unexpected test spawn coordinates");
                    if (npc.isAutoAttackable(null) || npc.isInCombat())
                        throw new AssertionError("Test NPC must be passive");
                    report.add("PASS: live NPC " + npc.getId() + " display=" + template.getDisplayId()
                        + " xyz=" + npc.getX() + "," + npc.getY() + "," + npc.getZ());
                }
            }
            if (count != 1) throw new AssertionError("Expected one live NPC, found " + count);
            report.add("PASS: read-only runtime check. In-client graphics still need visual review.");
        } catch (Throwable e) {
            report.add("FAILED: " + e);
            throw e;
        } finally {
            Files.write(Path.of(dir, "runtime-verification.txt"), report);
        }
    }
}
