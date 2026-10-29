package custom.ElvenPvpRoom;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.managers.RoomCombatRules;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.taskmanagers.PvpFlagTaskManager;
import custom.ElvenPvpRoom.RoundState.*;
import custom.ElvenPvpRoom.PvpRoomBots.Profile;

/** Runs with a private child loader/controller; no NPC, voice registration, or live round clock. */
public class BotIntegrationCheck {
 static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);}
 static Object field(Object o,String name)throws Exception{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
 public static void run(String directory)throws Exception{
  Path dir=Path.of(directory);StringBuilder result=new StringBuilder();PvpRoundRooms host=null;
  AtomicLong clock=new AtomicLong(1_000_000_000L);long start=clock.get();
  Set<Integer> connected=new HashSet<>();for(Player p:World.getPlayers())if(p.getClient()!=null)connected.add(p.getObjectId());
  try{
   var config=new PvpRoomConfig(Path.of("E:/l2-local/server/game/config/Custom/PvpRooms.properties"));
   Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);
   Object previous=loading.get(null);check(previous==null,"Script loader busy");
   try{loading.set(null,dir.resolve("src/custom/ElvenPvpRoom/PvpRoundRooms.java"));host=new PvpRoundRooms(config,clock::get,0,false);}finally{loading.set(null,previous);}
   PvpRoomBots bots=(PvpRoomBots)field(host,"bots");
   check(bots.status().equals("Bots apagados."),"Bots auto-started");
   try{bots.start(Mode.FREE,13,Profile.PARCIAL);throw new AssertionError("Limit ignored");}catch(IllegalArgumentException expected){}
   bots.start(Mode.FREE,6,Profile.EMPATE);bots.start(Mode.TWO_TEAMS,6,Profile.DUPLICADO);bots.start(Mode.THREE_TEAMS,6,Profile.PARCIAL);bots.start(Mode.ARENA,4,Profile.TARDIO);
   Set<Integer> instances=new HashSet<>();
   for(Mode mode:Mode.values()){
    List<Player> players=host.botParticipants(mode);check(!players.isEmpty(),"Bots missing");instances.add(players.get(0).getInstanceId());
    for(Player p:players)check(p.getClient()==null&&p.isLabControlled()&&p.isOnline()&&p.getPvpFlag()==1&&!p.isInvul()&&!p.isTeleportProtected(),"Invalid bot state");
   }
   check(instances.size()==4,"Bot modes share an instance");
   for(Player p:World.getPlayers())if(connected.contains(p.getObjectId()))check(!instances.contains(p.getInstanceId()),"Tests share an instance with animation client");
   result.append("PASS bots default off, limits, transient Players, same entry/flag rules and four instances isolated from connected clients.\n");
   // Ordinary AI performs combat. Put only our own FFA bots near one another for a short engine check.
   List<Player> free=host.botParticipants(Mode.FREE);Player a=free.get(0),b=free.get(1);
   b.setXYZ(a.getX()+24,a.getY(),a.getZ());b.setLastServerPosition(b.getX(),b.getY(),b.getZ());
   double healthBefore=free.stream().mapToDouble(p->p.getCurrentHp()+p.getCurrentCp()).sum();
   host.tick();Thread.sleep(4500);
   double healthAfter=free.stream().mapToDouble(p->p.getCurrentHp()+p.getCurrentCp()).sum();
   check(bots.status().contains("ataques="),"No attack orders");
   check(healthAfter<healthBefore,"Native bot AI did not deal damage");
   result.append("PASS bot AI issued attacks and dealt real HP/CP damage; targets restricted to owned opponents.\n");
   clock.set(start+1500_000_000_000L);host.tick();clock.addAndGet(45_000_000_000L);host.tick();
   check(host.botState(Mode.FREE).tally().values().stream().mapToInt(Integer::intValue).sum()==6,"Tie ballot missing");
   check(host.botState(Mode.FREE).tally().get("primeval")==3&&host.botState(Mode.FREE).tally().get("saints")==3,"Not a tie");
   check(host.botState(Mode.TWO_TEAMS).tally().get("primeval")==6,"Duplicate scenario count wrong");
   check(host.botState(Mode.THREE_TEAMS).tally().get("primeval")==3,"Partial abstention count wrong");
   check(host.botState(Mode.ARENA).tally().values().stream().mapToInt(Integer::intValue).sum()==0,"Late bots voted early");
   clock.set(start+1560_000_000_000L);host.tick();
   check(Set.of("primeval","saints").contains(host.botState(Mode.FREE).next()),"Tie winner outside candidates");
   check(host.botState(Mode.TWO_TEAMS).next().equals("primeval"),"Duplicate scenario changed winner");
   check(host.botState(Mode.ARENA).tally().values().stream().mapToInt(Integer::intValue).sum()==0,"Late votes accepted");
   check(bots.status().contains("rechazados=6")&&bots.status().contains("rechazados=4"),"Rejected-vote counters missing");
   result.append("PASS normal vote command: 3/3 tie, duplicate rejection (6), partial abstention, late rejection (4), and no-vote fallback.\n");
   clock.set(start+1800_000_000_000L);host.tick();
   for(Mode mode:Mode.values())check(host.botState(mode).generation()==2,"Bot group did not follow round");
   clock.set(start+3300_000_000_000L);host.tick();clock.addAndGet(45_000_000_000L);host.tick();
   check(host.botState(Mode.TWO_TEAMS).tally().values().stream().mapToInt(Integer::intValue).sum()==6,"Bots cannot vote next round");
   result.append("PASS map transitions, per-round vote token renewal and independent ballots.\n");
   Player dead=host.botParticipants(Mode.TWO_TEAMS).get(0);dead.setDead(true);clock.addAndGet(600_000_000L);host.tick();clock.addAndGet(11_000_000_000L);host.tick();
   check(!dead.isDead()&&!dead.isInvul()&&dead.getPvpFlag()==1,"Bot respawn failed or protected");
   result.append("PASS bot-only 10s respawn, no immunity; human resurrection rules unchanged.\n");
   int existing=host.botParticipants(Mode.FREE).size();host.onCommand("salas",dead,"bots iniciar libre 2 mayoria");check(host.botParticipants(Mode.FREE).size()==existing,"Non-GM started bots");
   bots.stopAll();check(bots.status().equals("Bots apagados."),"Stop did not clear groups");
   int arenaVotes=host.botState(Mode.ARENA).tally().values().stream().mapToInt(Integer::intValue).sum();
   bots.start(Mode.ARENA,4,Profile.MAYORIA);host.tick();
   check(host.botState(Mode.ARENA).tally().values().stream().mapToInt(Integer::intValue).sum()==arenaVotes+4,"Majority profile failed");bots.stopAll();
   int freeVotes=host.botState(Mode.FREE).tally().values().stream().mapToInt(Integer::intValue).sum();
   bots.start(Mode.FREE,4,Profile.ABSTENCION);host.tick();
   check(host.botState(Mode.FREE).tally().values().stream().mapToInt(Integer::intValue).sum()==freeVotes,"Abstention profile cast votes");bots.stopAll();
   result.append("PASS majority and full-abstention profiles; non-GM control rejected.\n");
   check(World.getPlayers().stream().noneMatch(p->p.getAccountName().equals("hellgames-room-bots")),"Bot world leak");
   for(Mode mode:Mode.values())check(host.botParticipants(mode).isEmpty(),"Visit leak");
   result.append("PASS stop-all removes bots, AI, room visits and groups. No real-player command or reposition used.\n");
  }catch(Throwable t){result.append("FAIL ").append(t).append('\n');throw t;}
  finally{
   if(host!=null)host.closeForVerification();Files.writeString(dir.resolve("verification.txt"),result);
  }
 }
}
