package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.network.SystemMessageId;
import org.l2jmobius.gameserver.mechanics.events.*;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerDlgAnswer;
import org.l2jmobius.gameserver.mechanics.events.returns.TerminateReturn;
import custom.ElvenPvpRoom.RoundState.*;
import custom.ElvenPvpRoom.PvpRoomBots.Profile;
public class UiIntegrationCheck {
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 static Object field(Object o,String name)throws Exception{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
 static void answer(Player p,int message,int value,int token){EventDispatcher.getInstance().notifyEvent(new OnPlayerDlgAnswer(p,message,value,token),p,TerminateReturn.class);}
 static PvpRoomUi.Pending pending(PvpRoomUi ui,Player p)throws Exception{return (PvpRoomUi.Pending)((Map<?,?>)field(ui,"dialogs")).get(p.getObjectId());}
 public static void run(String directory)throws Exception{
  Path dir=Path.of(directory);StringBuilder result=new StringBuilder();PvpRoundRooms host=null;
  AtomicLong clock=new AtomicLong(1_000_000_000L);long start=clock.get();
  try{
   var config=new PvpRoomConfig(Path.of("E:/l2-local/server/game/config/Custom/PvpRooms.properties"));
   Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);Object previous=loading.get(null);check(previous==null,"Script loader busy");
   try{loading.set(null,dir.resolve("src/custom/ElvenPvpRoom/PvpRoundRooms.java"));host=new PvpRoundRooms(config,clock::get,0,false);}finally{loading.set(null,previous);}
   PvpRoomBots bots=(PvpRoomBots)field(host,"bots");PvpRoomUi ui=(PvpRoomUi)field(host,"roomUi");bots.start(Mode.FREE,2,Profile.ABSTENCION);
   Player p=host.botParticipants(Mode.FREE).get(0),q=host.botParticipants(Mode.FREE).get(1);
   p.abortAttack();q.abortAttack();p.stopMove(null);q.stopMove(null);host.tick();
   Location origin=new Location(p);double hp=p.getCurrentHp(),mp=p.getCurrentMp(),cp=p.getCurrentCp();
   p.setXYZ(49240,p.getY(),p.getZ());clock.addAndGet(100_000_000L);host.tick();PvpRoomUi.Pending exit=pending(ui,p);
   check(exit!=null&&exit.kind()==PvpRoomUi.Kind.EXIT&&exit.until()-clock.get()==4_000_000_000L,"Native exit time/identity");
   answer(p,SystemMessageId.S1_3.getId(),0,exit.token());check(p.getX()==49240&&pending(ui,p)!=null,"Unrelated dialog handled");
   answer(p,SystemMessageId.S1_2.getId(),0,exit.token()+1);check(p.getX()==49240,"Wrong token accepted");
   answer(p,SystemMessageId.S1_2.getId(),0,exit.token());
   check(p.getX()==origin.getX()&&p.getY()==origin.getY()&&p.getInstanceId()==q.getInstanceId()&&p.getPvpFlag()==1,"Cancel did not return to last interior point");
   check(p.getCurrentHp()==hp&&p.getCurrentMp()==mp&&p.getCurrentCp()==cp&&!p.isInvul()&&!p.isTeleportProtected(),"Cancel changed state or granted protection");
   p.setXYZ(49240,p.getY(),p.getZ());clock.addAndGet(100_000_000L);host.tick();exit=pending(ui,p);answer(p,SystemMessageId.S1_2.getId(),1,exit.token());
   clock.addAndGet(3_800_000_000L);host.tick();check(p.getInstanceId()==q.getInstanceId(),"Accept exited early");clock.addAndGet(300_000_000L);host.tick();check(p.getInstanceId()==0,"Timeout did not exit");
   answer(p,SystemMessageId.S1_2.getId(),0,exit.token());check(p.getInstanceId()==0,"Late answer moved departed player");
   bots.stopAll();bots.start(Mode.FREE,2,Profile.ABSTENCION);p=host.botParticipants(Mode.FREE).get(0);
   clock.set(start+1500_000_000_000L);host.tick();long generation=host.botState(Mode.FREE).generation();
   host.onCommand("salas",p,"elegir "+generation+" primeval");PvpRoomUi.Pending vote=pending(ui,p);check(vote!=null&&vote.kind()==PvpRoomUi.Kind.VOTE,"Vote confirmation missing");
   check(host.botState(Mode.FREE).tally().get("primeval")==0,"Selection voted before confirmation");
   answer(p,SystemMessageId.S1_2.getId(),0,vote.token());check(host.botState(Mode.FREE).tally().get("primeval")==0,"Rejected selection voted");
   host.onCommand("salas",p,"elegir "+generation+" primeval");vote=pending(ui,p);answer(p,SystemMessageId.S1_2.getId(),1,vote.token());
   check(host.botState(Mode.FREE).tally().get("primeval")==1,"Confirmed vote not counted");answer(p,SystemMessageId.S1_2.getId(),1,vote.token());check(host.botState(Mode.FREE).tally().get("primeval")==1,"Replayed confirmation voted twice");
   Player other=host.botParticipants(Mode.FREE).get(1);host.onCommand("salas",other,"elegir "+generation+" saints");vote=pending(ui,other);clock.set(start+1560_000_000_000L);host.tick();answer(other,SystemMessageId.S1_2.getId(),1,vote.token());
   check(host.botState(Mode.FREE).tally().get("saints")==0,"Expired confirmation accepted");
   var packet=PvpRoomUi.packet("Example",4000,123);check(packet.getSystemMessage().getId()==1983&&(int)field(packet,"_time")==4000&&(int)field(packet,"_requesterId")==123,"ConfirmDlg fields invalid");
   String full=PvpRoomUi.progress(60,60),half=PvpRoomUi.progress(30,60),empty=PvpRoomUi.progress(0,60);
   check(full.contains("width=240 height=8")&&half.contains("width=120 height=8")&&!empty.contains("SquareWhite")&&!half.contains("|||"),"Graphical bar invalid");
   bots.stopAll();check(((Map<?,?>)field(ui,"dialogs")).isEmpty()&&((Map<?,?>)field(ui,"listeners")).isEmpty(),"UI listener/dialog leak");
   result.append("PASS native dialog id/time/token fields; unrelated/wrong-token replies ignored.\n");
   result.append("PASS Cancel returns from outside to last interior point without healing/protection; Accept preserves 4s deadline; expired replies cannot move departed players.\n");
   result.append("PASS map selection requires confirmation; reject/replay/late replies do not vote; valid confirmation counts once through normal command.\n");
   result.append("PASS graphical image bar full/half/empty, no text segments; all UI listeners/dialogs removed. Client rendering still requires observation.\n");
  }catch(Throwable t){result.append("FAIL ").append(t).append('\n');throw t;}
  finally{if(host!=null)host.closeForVerification();Files.writeString(dir.resolve("ui-verification.txt"),result);}
 }
}
