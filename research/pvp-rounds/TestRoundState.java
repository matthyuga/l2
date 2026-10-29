import custom.ElvenPvpRoom.RoundState;
import custom.ElvenPvpRoom.RoundState.*;
import java.util.*;
public class TestRoundState {
 static void check(boolean ok,String m){if(!ok)throw new AssertionError(m);}
 static RoundState round(Mode m){return new RoundState(m,List.of("elven","primeval","saints"),"elven",0,1800,300,60,new Random(42));}
 public static void main(String[] args)throws Exception{
  RoundState s=round(Mode.FREE);s.join(1,"A");s.join(2,"B");
  check(s.advance(1499)==Phase.BEFORE_VOTE,"Early voting");check(s.advance(1500)==Phase.VOTING,"Missing voting");
  check(s.vote(1,1,"primeval",1500),"Vote rejected");check(!s.vote(1,1,"saints",1501),"Duplicate allowed");
  check(!s.vote(3,1,"saints",1501),"Outsider vote");check(!s.vote(2,0,"saints",1501),"Stale vote");check(!s.vote(2,1,"bad",1501),"Invalid map");
  check(s.advance(1559)==Phase.VOTING,"Short ballot");check(s.advance(1560)==Phase.RESULT,"Vote didn't close");
  check(s.next().equals("primeval"),"Wrong winner");check(!s.vote(2,1,"saints",1560),"Late vote");
  check(s.advance(1799)==Phase.RESULT,"Map changed early");s.advance(1800);s.restart(1800);
  check(s.current().equals("primeval")&&s.generation()==2&&s.tally().get("primeval")==0,"Round reset");
  s.join(1,"A");check(!s.vote(1,1,"elven",3300),"Previous-round token accepted");
  Set<String> randomWinners=new HashSet<>();
  for(int seed=0;seed<100;seed++){RoundState r=new RoundState(Mode.FREE,List.of("elven","primeval","saints"),"elven",0,1800,300,60,new Random(seed));r.advance(1560);check(r.next()!=null,"No-vote fallback");randomWinners.add(r.next());}
  check(randomWinners.size()==3,"Fallback cannot choose all maps");
  RoundState tied=round(Mode.FREE);tied.join(1,"A");tied.join(2,"B");tied.vote(1,1,"primeval",1500);tied.vote(2,1,"saints",1500);tied.advance(1560);
  check(Set.of("primeval","saints").contains(tied.next()),"Tie selected a losing map");
  RoundState t=round(Mode.THREE_TEAMS);for(int i=1;i<=9;i++)check(t.join(i,"P"+i)==(i-1)%3+1,"Unbalanced team");
  check(!t.death(1,4),"Friendly kill scored");check(!t.death(2,4),"Duplicate death scored");t.alive(4);check(t.death(2,4),"Enemy kill missing");check(t.teamScore(2)==1,"Team score missing");
  t.leave(2);check(t.join(2,"P2")==2,"Rejoin changed team");check(!t.death(1,1),"Suicide scored");
  RoundState a=round(Mode.ARENA);for(int i=1;i<=15;i++)a.join(i,"P"+i);for(int i=2;i<=15;i++)a.death(1,i);
  check(a.top10().size()==10&&a.top10().get(0).id()==1&&a.top10().get(0).kills()==14,"Top 10 ordering");
  RoundState independent=round(Mode.TWO_TEAMS);check(independent.phase()==Phase.BEFORE_VOTE&&independent.participants()==0,"Rooms share state");
  RoundState concurrent=round(Mode.FREE);concurrent.join(1,"A");List<Thread> threads=new ArrayList<>();var accepted=new java.util.concurrent.atomic.AtomicInteger();
  for(int i=0;i<20;i++){Thread th=new Thread(()->{if(concurrent.vote(1,1,"elven",1500))accepted.incrementAndGet();});threads.add(th);th.start();}for(Thread th:threads)th.join();check(accepted.get()==1,"Concurrent duplicate vote");
  System.out.println("PASS timing 5m/60s/4m, eligibility, duplicate/concurrent/stale/late votes, winner/reset, random fallback, team balance/rejoin, scoring, duplicate deaths, Top 10 and independent rooms.");
 }
}
