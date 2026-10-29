import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.templates.CreatureTemplate;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
/** Temporary adapter for the already running module; source has identical dimensions. */
public final class BehemothVisualPatch {
 public static void agentmain(String directory,Instrumentation instrumentation)throws Exception {
  Object service=null;
  for(Class<?> c:instrumentation.getAllLoadedClasses())if(c.getName().equals("custom.BehemothTransport.BehemothTransport")){var f=c.getDeclaredField("instance");f.setAccessible(true);if(f.get(null)!=null){service=f.get(null);break;}}
  if(service==null)throw new IllegalStateException("No module instance");
  final Object target=service;var ownedField=target.getClass().getDeclaredField("owned");ownedField.setAccessible(true);
  var previous=VoicedCommandHandler.getInstance().getHandler("behemoth");
  VoicedCommandHandler.getInstance().registerHandler(new IVoicedCommandHandler(){
   public String[] getCommandList(){return new String[]{"behemoth"};}
   public boolean onCommand(String command,Player p,String params){
    String action=params==null?"":params.trim().split("\\s+",2)[0].toLowerCase(Locale.ROOT);
    if(Set.of("conducir","subir").contains(action)){p.sendMessage("Montaje pausado: falta corregir y validar la union visual al asiento. Tu personaje permanece libre.");return true;}
    synchronized(target){boolean result=previous.onCommand(command,p,params);
     if(action.equals("invocar"))try{Object trip=((Map<?,?>)ownedField.get(target)).get(p.getObjectId());if(trip!=null){var field=trip.getClass().getDeclaredField("npc");field.setAccessible(true);Npc npc=(Npc)field.get(trip);if(npc.getId()!=902791)throw new IllegalStateException("Unexpected NPC");var template=npc.getTemplate();for(String key:List.of("_collisionRadius","_collisionHeight","_fCollisionRadius","_fCollisionHeight")){var f=CreatureTemplate.class.getDeclaredField(key);f.setAccessible(true);int value=key.endsWith("Radius")?63:54;if(f.getType()==int.class)f.setInt(template,value);else f.setFloat(template,value);}npc.broadcastInfo();}}
     catch(Exception e){p.sendMessage("No se pudo aplicar el ajuste visual del laboratorio.");throw new RuntimeException(e);}
     return result;
    }
   }
  });
  Player p=World.getPlayer("Hellkevin");String state=p==null?"offline":("online="+p.isOnline()+", seat="+BehemothSeatSync.isSeated(p)+", movementDisabled="+p.isMovementDisabled());
  Files.writeString(Path.of(directory,"visual-patch.txt"),"Visual-only test mode; collision radius63 height54. Real boarding blocked.\nHellkevin: "+state+"\n");
 }
}
