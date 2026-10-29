import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.instancezone.Instance;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.InstanceManager;
public class AuditPvpActivation {
 static Object field(Object o,String n)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(o);}
 public static void agentmain(String dir,Instrumentation inst)throws Exception{
  Object h=VoicedCommandHandler.getInstance().getHandler("salas");
  if(h==null||!h.getClass().getName().equals("custom.ElvenPvpRoom.PvpRoundRooms"))throw new IllegalStateException("Four-room lobby not registered");
  synchronized(h){
   Map<?,?> rooms=(Map<?,?>)field(h,"rooms");if(rooms.size()!=4)throw new IllegalStateException("Four modes missing");
   if(InstanceManager.getInstance().getInstanceTemplateFileName(3060)==null)throw new IllegalStateException("Template 3060 missing");
   int hosts=(int)World.getVisibleObjects().stream().filter(o->o.isNpc()&&o.asNpc().getId()==902600).count();if(hosts!=2)throw new IllegalStateException("Lobby NPC count="+hosts);
   Object config=field(h,"config");Field maps=config.getClass().getField("maps");if(((Map<?,?>)maps.get(config)).size()!=3)throw new IllegalStateException("Three maps missing");
   Object bots=field(h,"bots");String botStatus=(String)bots.getClass().getMethod("status").invoke(bots);if(!botStatus.equals("Bots apagados."))throw new IllegalStateException("Bots unexpectedly active");
   if(!field(h,"roomUi").getClass().getName().equals("custom.ElvenPvpRoom.PvpRoomUi"))throw new IllegalStateException("Native UI missing");
   Set<Integer> ids=new HashSet<>();StringBuilder modes=new StringBuilder();
   for(var row:rooms.entrySet()){
    Object room=row.getValue();Method instance=h.getClass().getDeclaredMethod("instance",room.getClass());instance.setAccessible(true);Instance i=(Instance)instance.invoke(h,room);
    if(!ids.add(i.getId())||i.getTemplateId()!=3060||!i.isPvP())throw new IllegalStateException("Room instance isolation/template/PvP mismatch");
    if(modes.length()>0)modes.append(',');modes.append('"').append(row.getKey()).append("\":").append(i.getId());
   }
   if(!((Map<?,?>)field(h,"visits")).isEmpty())throw new IllegalStateException("Unexpected occupants before activation audit");
   Files.writeString(Path.of(dir,"activation-audit.json"),"{\"status\":\"PASS\",\"lobby\":\""+h.getClass().getName()+"\",\"hosts\":"+hosts+",\"maps\":3,\"room_instances\":{"+modes+"},\"bots\":\"OFF\",\"native_ui\":true}\n");
  }
 }
}
