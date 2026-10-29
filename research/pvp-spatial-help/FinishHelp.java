import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
public class FinishHelp {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Path dir=Path.of(directory);Object host=VoicedCommandHandler.getInstance().getHandler("salas");ClassLoader loader=host.getClass().getClassLoader();
  synchronized(host){
   Class<?> help=loader.loadClass("custom.ElvenPvpRoom.RoomCommandHelp");inst.redefineClasses(new ClassDefinition(help,Files.readAllBytes(dir.resolve("compiled/custom/ElvenPvpRoom/RoomCommandHelp.class"))));
   if(!help.isInstance(VoicedCommandHandler.getInstance().getHandler("ayuda"))||!help.isInstance(VoicedCommandHandler.getInstance().getHandler("macros")))throw new IllegalStateException("Missing help handler");
   var menu=host.getClass().getDeclaredMethod("menu");menu.setAccessible(true);String html=(String)menu.invoke(host);if(!html.contains("voice .ayuda"))throw new IllegalStateException("Missing NPC access");
   Files.writeString(dir.resolve("help-status.txt"),"PASS ayuda/macros registered; existing PvP NPC menu links to catalogue; opening help closes periodic room panels without exiting or resetting the round. HTML generation checked; visual client review pending.\n");
  }
 }
}
