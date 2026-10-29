import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.entity.World;
public class StartSiegeRoomBots {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  Object host=VoicedCommandHandler.getInstance().getHandler("salas");StringBuilder out=new StringBuilder();
  synchronized(host){
   var f=host.getClass().getDeclaredField("bots");f.setAccessible(true);Object bots=f.get(host);ClassLoader loader=host.getClass().getClassLoader();
   Class<?> mode=loader.loadClass("custom.ElvenPvpRoom.RoundState$Mode"),profile=loader.loadClass("custom.ElvenPvpRoom.PvpRoomBots$Profile");
   var start=bots.getClass().getDeclaredMethod("start",mode,int.class,profile);start.setAccessible(true);
   Object partial=Enum.valueOf((Class)profile,"PARCIAL");
   for(Object m:mode.getEnumConstants()){start.invoke(bots,m,6,partial);out.append(m).append(": 6 native roster bots started\n");}
   out.append(bots.getClass().getMethod("status").invoke(bots)).append('\n');
   out.append("Connected real players untouched: ").append(World.getPlayers().stream().filter(p->p.getClient()!=null).count()).append('\n');
  }
  Files.writeString(Path.of(directory,"live-start.txt"),out);
 }
}
