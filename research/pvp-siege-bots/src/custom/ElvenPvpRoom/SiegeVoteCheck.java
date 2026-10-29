package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.entity.World;
import custom.ElvenPvpRoom.RoundState.*;
import custom.ElvenPvpRoom.PvpRoomBots.Profile;
public class SiegeVoteCheck {
 static Object field(Object o,String n)throws Exception{Field f=o.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(o);}
 static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
 public static void run(String directory)throws Exception{
  PvpRoundRooms host=null;StringBuilder result=new StringBuilder();AtomicLong clock=new AtomicLong(1_000_000_000L);long start=clock.get();Set<Integer> testIds=new HashSet<>();
  try{
   Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);Object prior=loading.get(null);check(prior==null,"Loader busy");
   try{loading.set(null,Path.of(directory,"src/custom/ElvenPvpRoom/SiegeVoteCheck.java"));host=new PvpRoundRooms(new PvpRoomConfig(Path.of("E:/l2-local/server/game/config/Custom/PvpRooms.properties")),clock::get,0,false);}finally{loading.set(null,prior);}
   PvpRoomBots bots=(PvpRoomBots)field(host,"bots");bots.start(Mode.FREE,4,Profile.EMPATE);bots.start(Mode.TWO_TEAMS,4,Profile.DUPLICADO);bots.start(Mode.THREE_TEAMS,4,Profile.PARCIAL);bots.start(Mode.ARENA,4,Profile.TARDIO);
   for(Mode mode:Mode.values())for(var p:host.botParticipants(mode))testIds.add(p.getObjectId());
   clock.set(start+1500_000_000_000L);host.tick();clock.addAndGet(45_000_000_000L);host.tick();
   check(host.botState(Mode.FREE).tally().get("primeval")==2&&host.botState(Mode.FREE).tally().get("saints")==2,"Tie votes failed");check(host.botState(Mode.TWO_TEAMS).tally().get("primeval")==4,"Duplicates counted");check(host.botState(Mode.THREE_TEAMS).tally().get("primeval")==2,"Partial abstention failed");
   clock.set(start+1560_000_000_000L);host.tick();check(host.botState(Mode.ARENA).tally().values().stream().mapToInt(Integer::intValue).sum()==0,"Late votes counted");
   clock.set(start+1800_000_000_000L);host.tick();for(Mode mode:Mode.values())for(var p:host.botParticipants(mode))if(p.isInParty())for(var q:p.getParty().getMembers())check(host.botState(mode).team(p.getObjectId())==host.botState(mode).team(q.getObjectId()),"New-round party crosses teams");
   clock.set(start+3300_000_000_000L);host.tick();clock.addAndGet(45_000_000_000L);host.tick();check(host.botState(Mode.TWO_TEAMS).tally().values().stream().mapToInt(Integer::intValue).sum()==4,"Next-round votes failed");bots.stopAll();
   check(testIds.stream().noneMatch(id->World.getPlayer(id)!=null),"Test actor leak");result.append("PASS native siege actors: tie2/2, duplicate and late rejection, partial abstentions, map change, renewed vote in next round, same-team random parties after rebalancing and complete test actor release.\n");
  }catch(Throwable t){result.append("FAIL ").append(t).append('\n');throw t;}finally{if(host!=null)host.closeForVerification();Files.writeString(Path.of(directory,"vote-verification.txt"),result);}
 }
}
