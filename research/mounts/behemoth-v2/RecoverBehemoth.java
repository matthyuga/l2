import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.*;
import org.l2jmobius.gameserver.managers.BehemothSeatSync;
/** Release only occupants of the experimental Behemoth and pause real boarding. */
public final class RecoverBehemoth {
 public static void agentmain(String directory,Instrumentation inst)throws Exception {
  var handlers=VoicedCommandHandler.getInstance();var previous=handlers.getHandler("behemoth");
  if(previous==null)throw new IllegalStateException("Behemoth handler not loaded");
  var service=previous;Class<?> type=service.getClass();
  var ownedField=type.getDeclaredField("owned");ownedField.setAccessible(true);
  var membersField=type.getDeclaredField("members");membersField.setAccessible(true);
  var members=(Map<?,?>)membersField.get(service);var players=new ArrayList<Player>();
  for(Object member:List.copyOf(members.values())){var accessor=member.getClass().getDeclaredMethod("player");accessor.setAccessible(true);players.add((Player)accessor.invoke(member));}
  synchronized(service){for(Object trip:List.copyOf(((Map<?,?>)ownedField.get(service)).values())){var close=type.getDeclaredMethod("close",trip.getClass(),String.class);close.setAccessible(true);close.invoke(service,trip,"Prueba pausada: recuperando al personaje.");}}
  for(Player player:players){BehemothSeatSync.unbind(player);if(player.isOnline()){player.teleToLocation(player.getX(),player.getY(),player.getZ());player.sendMessage("Personaje liberado. Montaje del Behemoth pausado hasta corregir su posicion visual.");}}
  handlers.registerHandler(new IVoicedCommandHandler(){public String[] getCommandList(){return new String[]{"behemoth"};}public boolean onCommand(String command,Player p,String params){String action=params==null?"":params.trim().split("\\s+",2)[0];if(Set.of("conducir","subir").contains(action.toLowerCase(Locale.ROOT))){p.sendMessage("Montaje en revision: los asientos visuales aun no estan validados. Tu personaje permanece libre.");return true;}return previous.onCommand(command,p,params);}});
  Files.writeString(Path.of(directory,"player-recovery.txt"),"Released experimental occupants: "+players.stream().map(Player::getName).toList()+"\nBoarding paused; ordinary players untouched.\n");
 }
}
