import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.scripting.ScriptEngine;

public final class ReloadMaggieStickers {
 public static void agentmain(String directory,Instrumentation ignored)throws Exception {
  Path stage=Path.of(directory),root=stage.getParent().getParent();var voices=VoicedCommandHandler.getInstance();var previous=voices.getHandler("sticker");
  if(previous==null||!previous.getClass().getName().equals("custom.StickerEmotes.StickerEmotes"))throw new IllegalStateException("Expected existing sticker handler");
  for(var p:World.getPlayers())if(p.getClient()!=null)throw new IllegalStateException("Close player clients before reload");
  List<String> report=new ArrayList<>();
  try{
   ScriptEngine.getInstance().executeScript(root.resolve("server/game/data/scripts/custom/StickerEmotes/StickerEmotes.java"));
   var handler=voices.getHandler("sticker");
   if(handler==previous||voices.getHandler("stickers")!=handler)throw new AssertionError("Handler was not replaced");
   var type=handler.getClass();var namesField=type.getDeclaredField("NAMES");namesField.setAccessible(true);String[] names=(String[])namesField.get(null);
   if(names.length!=19)throw new AssertionError("Wrong live catalog size: "+names.length);
   var selection=type.getDeclaredMethod("selection",String.class);selection.setAccessible(true);
   for(int i=0;i<19;i++)if((int)selection.invoke(null,Integer.toString(i+1))!=i||(int)selection.invoke(null,names[i])!=i)throw new AssertionError("Selection "+i);
   for(String s:new String[]{"0","20","-1","19720","19 extra","999999999999999999"})if((int)selection.invoke(null,s)!=-1)throw new AssertionError("Invalid selection accepted");
   if(!handler.onCommand("sticker",null,"19"))throw new AssertionError("Null guard");
   report.add("PASS: normal ScriptEngine reload; 19 actual live numeric/name selections and invalid inputs checked; aliases share one handler.");
   report.add("PASS: no core patch, restart, player state mutation or effect emission during verification.");
   report.add("LIMIT: button-only recovery, sticker drawing/following/expiration and second-client visibility need in-game verification.");
   Files.write(stage.resolve("live-verification.txt"),report);
  }catch(Throwable ex){voices.registerHandler(previous);Files.writeString(stage.resolve("live-verification.txt"),"FAILED; previous handler restored: "+ex);throw new IllegalStateException(ex);}
 }
}
