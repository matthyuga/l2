package custom.ElvenPvpRoom;

import java.util.*;
import java.util.random.RandomGenerator;

/** Pure round state. Times use one monotonic clock supplied by the caller. */
public final class RoundState {
 public enum Mode {
  FREE("Libre",0), TWO_TEAMS("Rojos vs Azules",2), THREE_TEAMS("Rojos vs Azules vs Verdes",3), ARENA("Arena - Top 10",0);
  public final String label; public final int teams;
  Mode(String label,int teams){this.label=label;this.teams=teams;}
 }
 public enum Phase { BEFORE_VOTE, VOTING, RESULT, FINISHED }
 public record Standing(int id,String name,int team,int kills,int deaths) {}
 private static final class Score {
  final int id,team; String name; int kills,deaths;
  Score(int id,String name,int team){this.id=id;this.name=name;this.team=team;}
  Standing standing(){return new Standing(id,name,team,kills,deaths);}
 }
 public final Mode mode;
 private final List<String> maps;
 private final long duration,voteLead,voteDuration;
 private final RandomGenerator random;
 private final Map<Integer,String> votes=new HashMap<>();
 private final Map<Integer,Score> scores=new HashMap<>();
 private final Set<Integer> active=new HashSet<>(),dead=new HashSet<>();
 private final int[] teamScores=new int[4];
 private long started,generation=1;
 private String current,next;
 private Phase phase=Phase.BEFORE_VOTE;
 public RoundState(Mode mode,List<String> maps,String current,long now,long duration,long voteLead,long voteDuration,RandomGenerator random){
  if(maps.isEmpty()||new HashSet<>(maps).size()!=maps.size()||!maps.contains(current)||voteDuration<=0||voteLead<voteDuration||duration<=voteLead)throw new IllegalArgumentException("Invalid round configuration");
  this.mode=Objects.requireNonNull(mode);this.maps=List.copyOf(maps);this.current=current;started=now;
  this.duration=duration;this.voteLead=voteLead;this.voteDuration=voteDuration;this.random=Objects.requireNonNull(random);
 }
 public synchronized Phase advance(long now){
  long elapsed=now-started;
  if(phase==Phase.BEFORE_VOTE && elapsed>=duration-voteLead)phase=Phase.VOTING;
  if(phase==Phase.VOTING && elapsed>=duration-voteLead+voteDuration){next=choose();phase=Phase.RESULT;}
  if(elapsed>=duration)phase=Phase.FINISHED;
  return phase;
 }
 private String choose(){
  Map<String,Integer> tally=tally();int max=Collections.max(tally.values());
  List<String> tied=maps.stream().filter(m->tally.get(m)==max).toList();
  return tied.get(random.nextInt(tied.size()));
 }
 public synchronized boolean vote(int id,long round,String map,long now){
  advance(now);
  if(round!=generation || phase!=Phase.VOTING || !active.contains(id) || !maps.contains(map) || votes.containsKey(id))return false;
  votes.put(id,map);return true;
 }
 public synchronized Map<String,Integer> tally(){
  Map<String,Integer> result=new LinkedHashMap<>();for(String m:maps)result.put(m,0);
  for(String m:votes.values())result.merge(m,1,Integer::sum);
  return Collections.unmodifiableMap(result);
 }
 public synchronized void restart(long now){
  if(phase!=Phase.FINISHED || next==null)throw new IllegalStateException("Round not finished");
  current=next;next=null;started=now;generation++;phase=Phase.BEFORE_VOTE;
  votes.clear();scores.clear();active.clear();dead.clear();Arrays.fill(teamScores,0);
 }
 public synchronized int join(int id,String name){
  Score previous=scores.get(id);
  if(previous!=null){previous.name=name;active.add(id);return previous.team;}
  int team=0;
  if(mode.teams>0){int[] count=new int[4];for(int member:active)count[scores.get(member).team]++;
   team=1;for(int t=2;t<=mode.teams;t++)if(count[t]<count[team])team=t;
  }
  scores.put(id,new Score(id,name,team));active.add(id);return team;
 }
 public synchronized void leave(int id){active.remove(id);}
 public synchronized void alive(int id){dead.remove(id);}
 public synchronized boolean death(int killer,int victim){
  if(!active.contains(victim)||!dead.add(victim))return false;
  Score v=scores.get(victim);v.deaths++;
  if(killer==victim || !active.contains(killer))return false;
  Score k=scores.get(killer);
  if(mode.teams>0 && k.team==v.team)return false;
  k.kills++;if(k.team>0)teamScores[k.team]++;return true;
 }
 public synchronized List<Standing> top10(){return scores.values().stream().map(Score::standing)
  .sorted(Comparator.comparingInt(Standing::kills).reversed().thenComparingInt(Standing::deaths).thenComparingInt(Standing::id)).limit(10).toList();}
 public synchronized int team(int id){Score s=scores.get(id);return s==null?-1:s.team;}
 public synchronized int teamScore(int team){return teamScores[team];}
 public synchronized int participants(){return active.size();}
 public synchronized String current(){return current;}
 public synchronized String next(){return next;}
 public synchronized long generation(){return generation;}
 public synchronized Phase phase(){return phase;}
 public synchronized boolean hasVoted(int id){return votes.containsKey(id);}
 public synchronized long remaining(long now){return Math.max(0,duration-(now-started));}
 public synchronized long voteRemaining(long now){return Math.max(0,duration-voteLead+voteDuration-(now-started));}
 public List<String> maps(){return maps;}
}
