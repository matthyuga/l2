package custom.ElvenPvpRoom;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.nio.file.*;
import java.lang.reflect.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.ScriptManager;
public final class RoundSetsFixtureV2 extends PvpRoundRooms{
 public RoundSetsFixtureV2(PvpRoomConfig config,AtomicLong clock){super(config,clock::get,0,false);}
 public static void verify(Path dir)throws Exception{
  Object real=VoicedCommandHandler.getInstance().getHandler("salas");Object registered=ScriptManager.getInstance().getScript("PvpRoundRooms");
  Player human=World.getPlayer("Hellkevin");Object party=human==null?null:human.getParty();int instance=human==null?-1:human.getInstanceId();
  PvpRoomConfig config=new PvpRoomConfig(Path.of("config/Custom/PvpRooms.properties"));AtomicLong now=new AtomicLong();RoundSetsFixtureV2 fixture;
  Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);Object prior=loading.get(null);if(prior!=null)throw new IllegalStateException("Script loader busy");
  try{loading.set(null,dir.resolve("test-src/custom/ElvenPvpRoom/RoundSetsFixtureV2.java"));fixture=new RoundSetsFixtureV2(config,now);}finally{loading.set(null,prior);}
  Field f=PvpRoundRooms.class.getDeclaredField("bots");f.setAccessible(true);PvpRoomBots bots=(PvpRoomBots)f.get(fixture);
  Set<Integer> old=new HashSet<>(),fresh=new HashSet<>();String production;
  try{
   bots.start(RoundState.Mode.TWO_TEAMS,2,PvpRoomBots.Profile.EMPATE);
   for(Player p:fixture.botParticipants(RoundState.Mode.TWO_TEAMS))old.add(p.getObjectId());
   fixture.tick();long deadline=System.currentTimeMillis()+45000;
   while(!PvpRoundSets.status(bots).contains("2/2")){if(System.currentTimeMillis()>deadline)throw new IllegalStateException("Preparation timed out: "+bots.status());Thread.sleep(250);}
   RoundState state=fixture.botState(RoundState.Mode.TWO_TEAMS);state.death(old.iterator().next(),old.stream().skip(1).findFirst().orElseThrow());
   now.set(config.roundNanos);fixture.tick();
   List<Player> active=fixture.botParticipants(RoundState.Mode.TWO_TEAMS);
   for(Player p:active)fresh.add(p.getObjectId());
   if(active.size()!=2||fresh.size()!=2||!Collections.disjoint(old,fresh))throw new IllegalStateException("Batch not replaced");
   for(int id:old)if(World.getPlayer(id)!=null)throw new IllegalStateException("Old actor retained: "+id);
   if(state.generation()!=2||state.teamScore(1)!=0||state.teamScore(2)!=0||state.participants()!=2)throw new IllegalStateException("Round/score reset failed");
   if(state.team(active.get(0).getObjectId())==state.team(active.get(1).getObjectId()))throw new IllegalStateException("Teams not balanced");
   // Verify randomized admission can change memberships without changing team-size balance.
   Set<String> partitions=new HashSet<>();Random rng=new Random(73);
   for(int n=0;n<100;n++){RoundState sample=new RoundState(RoundState.Mode.THREE_TEAMS,List.of("elven","primeval","saints"),"elven",0,100,30,10,rng);List<Integer> ids=new ArrayList<>(List.of(1,2,3,4,5,6));Collections.shuffle(ids,rng);int[] counts=new int[4];for(int id:ids)counts[sample.join(id,"Test"+id)]++;if(counts[1]!=2||counts[2]!=2||counts[3]!=2)throw new IllegalStateException("Unbalanced shuffle");partitions.add(sample.team(1)+":"+sample.team(2)+":"+sample.team(3)+":"+sample.team(4));}
   if(partitions.size()<10)throw new IllegalStateException("Shuffle repeats fixed membership");
   synchronized(real){PvpRoomBots prod=(PvpRoomBots)f.get(real);production=prod.status();}
   Files.writeString(dir.resolve("verification.txt"),"PASS distinct prepared batch replaced original actors; old world registrations removed; generation advanced, scores reset, two balanced teams. 100 shuffle simulations balanced with "+partitions.size()+" distinct partitions.\nold="+old+" new="+fresh+"\nproduction="+production+"\n");
  }finally{fixture.closeForVerification();ScriptManager.getInstance().getScripts().remove("RoundSetsFixtureV2",fixture);}
  if(VoicedCommandHandler.getInstance().getHandler("salas")!=real||ScriptManager.getInstance().getScript("PvpRoundRooms")!=registered)throw new IllegalStateException("Production registry changed");
  if(human!=null&&(human.getParty()!=party||human.getInstanceId()!=instance))throw new IllegalStateException("Human party/instance changed during isolated test");
  for(int id:fresh)if(World.getPlayer(id)!=null)throw new IllegalStateException("Fixture actor not released");
  Files.writeString(dir.resolve("verification.txt"),"PASS fixture cleanup and production lobby registry, human party and instance unchanged.\n",StandardOpenOption.APPEND);
 }
}
