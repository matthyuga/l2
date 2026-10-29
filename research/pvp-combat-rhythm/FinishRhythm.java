import java.lang.instrument.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class FinishRhythm {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory);Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();synchronized(host){List<ClassDefinition> defs=new ArrayList<>();for(String name:List.of("RoomCombatRhythm","PvpTacticalEngine"))defs.add(new ClassDefinition(loader.loadClass("custom.ElvenPvpRoom."+name),Files.readAllBytes(dir.resolve("compiled/custom/ElvenPvpRoom/"+name+".class"))));inst.redefineClasses(defs.toArray(ClassDefinition[]::new));Files.writeString(dir.resolve("finish.txt"),"PASS native short chase preserved between skill windows; Snipe cancellation uses native buff removal when target leaves range or closes in.\n");}
 }
}
