import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.scripting.ScriptEngine;

/** Loads through the normal script engine, without restarting or patching the core. */
public final class ActivateStickers {
    public static void agentmain(String directory, Instrumentation ignored) throws Exception {
        Path stage=Path.of(directory), root=stage.getParent().getParent();
        List<String> report=new ArrayList<>();
        var voices=VoicedCommandHandler.getInstance();
        try {
            for(var p:World.getPlayers()) if(p.getClient()!=null) throw new IllegalStateException("A player client is connected; activation refused");
            if(voices.getHandler("sticker")!=null || voices.getHandler("stickers")!=null) throw new IllegalStateException("Sticker handler already exists");
            ScriptEngine.getInstance().executeScript(root.resolve("server/game/data/scripts/custom/StickerEmotes/StickerEmotes.java"));
            var handler=voices.getHandler("sticker");
            if(handler==null || !handler.getClass().getName().equals("custom.StickerEmotes.StickerEmotes") || voices.getHandler("stickers")!=handler) throw new AssertionError("Handler registration failed");
            report.add("PASS: normal ScriptEngine load; both voiced aliases registered; no core redefinition or server restart.");
            var type=handler.getClass();
            var selection=type.getDeclaredMethod("selection",String.class);selection.setAccessible(true);
            String[] names={"risa","gg","corazon","enojo","llanto","sorpresa","duda","saludo"};
            for(int i=0;i<8;i++) {
                if((int)selection.invoke(null,Integer.toString(i+1))!=i || (int)selection.invoke(null,names[i].toUpperCase(Locale.ROOT))!=i) throw new AssertionError("Selection "+i);
            }
            for(String value:new String[]{"","0","9","-1","19720","1 extra","<script>","999999999999999999999"}) if((int)selection.invoke(null,value)!=-1) throw new AssertionError("Invalid selection accepted");
            if((int)selection.invoke(null,new Object[]{null})!=-1 || (int)selection.invoke(null,"  gg  ")!=1) throw new AssertionError("Null/trim selection");
            report.add("PASS: all 8 numeric/name/uppercase selections, whitespace, null and 8 invalid/oversized inputs.");
            var elapsed=type.getDeclaredMethod("elapsed",Long.class,long.class);elapsed.setAccessible(true);
            long now=10_000_000_000L;
            if(!(boolean)elapsed.invoke(null,null,now) || (boolean)elapsed.invoke(null,now,now) || (boolean)elapsed.invoke(null,now,now+4_999_999_999L) || !(boolean)elapsed.invoke(null,now,now+5_000_000_000L)) throw new AssertionError("Cooldown boundary");
            if(!handler.onCommand("sticker",null,"1")) throw new AssertionError("Null player guard");
            report.add("PASS: exact monotonic 5-second cooldown boundary and null-player guard.");
            report.add("LIMIT: packet presentation, moving character attachment, menu input and second-client visibility still require an in-game visual check.");
            Files.write(stage.resolve("live-verification.txt"),report);
        } catch(Throwable ex) {
            var added=voices.getHandler("sticker");
            if(added!=null && added.getClass().getName().equals("custom.StickerEmotes.StickerEmotes")) voices.removeHandler(added);
            report.add("FAILED: "+ex);Files.write(stage.resolve("live-verification.txt"),report);throw new IllegalStateException(ex);
        }
    }
}
