package custom.ElvenPvpRoom;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.network.serverpackets.ConfirmDlg;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;
import org.l2jmobius.gameserver.network.SystemMessageId;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerDlgAnswer;
import org.l2jmobius.gameserver.mechanics.events.listeners.FunctionEventListener;
import org.l2jmobius.gameserver.mechanics.events.returns.TerminateReturn;

/** Server UI only. Native timed confirmations plus graphical HTML progress. */
public final class PvpRoomUi {
 public enum Kind { EXIT, VOTE }
 public record Pending(Kind kind,int token,long round,String map,long until){}
 private static final AtomicInteger TOKENS=new AtomicInteger(0x61000000);
 private final PvpRoundRooms host;
 private final Map<Integer,Pending> dialogs=new HashMap<>();
 private final Map<Integer,FunctionEventListener> listeners=new HashMap<>();
 PvpRoomUi(PvpRoundRooms host){this.host=host;}
 void attach(Player player){
  if(listeners.containsKey(player.getObjectId()))return;
  FunctionEventListener listener=new FunctionEventListener(player,EventType.ON_PLAYER_DLG_ANSWER,(OnPlayerDlgAnswer event)->answer(event),this);
  listeners.put(player.getObjectId(),listener);player.addListener(listener);
 }
 void detach(Player player){dialogs.remove(player.getObjectId());FunctionEventListener l=listeners.remove(player.getObjectId());if(l!=null)player.removeListener(l);}
 void exit(Player player,long now,long until){
  send(player,new Pending(Kind.EXIT,TOKENS.incrementAndGet(),0,null,until),
   "Salida a Giran. Aceptar mantiene la cuenta; Cancelar te devuelve a tu ultima posicion dentro de la arena.",now);
 }
 void choose(Player player,long round,String map,String label,long now,long until){
  Pending pending=dialogs.get(player.getObjectId());
  if(pending!=null&&pending.kind()==Kind.EXIT&&pending.until()>now){player.sendMessage("Primero termina o cancela tu salida.");return;}
  send(player,new Pending(Kind.VOTE,TOKENS.incrementAndGet(),round,map,until),"Votar por "+label+"?",now);
 }
 private void send(Player player,Pending pending,String text,long now){
  if(pending.until()<=now)return;
  attach(player);dialogs.put(player.getObjectId(),pending);
  int millis=(int)Math.min(Integer.MAX_VALUE,Math.max(1,(pending.until()-now+999999)/1000000));
  player.sendPacket(packet(text,millis,pending.token()));
 }
 static ConfirmDlg packet(String text,int millis,int token){
  // S1_2 is the client's plain "$s1" string; S1_3 is reserved by several native actions.
  ConfirmDlg packet=new ConfirmDlg(SystemMessageId.S1_2);packet.getSystemMessage().addString(text);
  return packet.addTime(millis).addRequesterId(token);
 }
 /** Returns null for every unrelated resurrection, party/trade/clan or other script dialog. */
 private TerminateReturn answer(OnPlayerDlgAnswer event){
  synchronized(host){
   Pending pending=dialogs.get(event.getPlayer().getObjectId());
   if(event.getMessageId()!=SystemMessageId.S1_2.getId()||pending==null||pending.token()!=event.getRequesterId())return null;
   dialogs.remove(event.getPlayer().getObjectId());
   if(host.botNow()<pending.until()){
    if(pending.kind()==Kind.VOTE){if(event.getAnswer()==1)host.onCommand("salas",event.getPlayer(),"votar "+pending.round()+" "+pending.map());else host.onCommand("salas",event.getPlayer(),"votar");}
    else if(event.getAnswer()==0)host.uiCancelExit(event.getPlayer());
   }
   return new TerminateReturn(true,false,false);
  }
 }
 void invalidate(Player p,Kind kind){Pending pending=dialogs.get(p.getObjectId());if(pending!=null&&pending.kind()==kind)dialogs.remove(p.getObjectId());}
 public static String progress(long remaining,long total){
  if(total<=0)throw new IllegalArgumentException("Positive duration required");
  int width=240,filled=(int)Math.round(width*Math.max(0,Math.min(1,(double)remaining/total)));
  StringBuilder b=new StringBuilder("<table width=240 cellspacing=0 cellpadding=0><tr>");
  if(filled>0)b.append("<td width=").append(filled).append("><img src=\"L2UI.SquareWhite\" width=").append(filled).append(" height=8></td>");
  if(filled<width)b.append("<td width=").append(width-filled).append("><img src=\"L2UI.SquareGray\" width=").append(width-filled).append(" height=8></td>");
  return b.append("</tr></table>").toString();
 }
}
