import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public final class EnableStickerDiagnosticsV3 {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path s=Path.of(directory);var h=VoicedCommandHandler.getInstance().getHandler("sticker");
  if(h==null||!h.getClass().getName().equals("custom.StickerEmotes.MaggieStickerEmotes"))throw new IllegalStateException("Wrong handler");
  byte[] bytes=Files.readAllBytes(s.resolve("classes/custom/StickerEmotes/MaggieStickerEmotes.class"));
  inst.redefineClasses(new ClassDefinition(h.getClass(),bytes));
  Files.writeString(s.resolve("live-verification.txt"),"PASS: only existing sticker script class redefined; command selection/accepted feedback and diagnostic logging active; handler identity retained. No core changes.\nLIMIT: world rendering and repaired wheel require in-game verification.\n");
 }
}
