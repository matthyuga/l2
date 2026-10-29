package custom.GiranSiegeLab;

import java.util.*;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.Door;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Randomness stays inside playable stages; closed gates and native paths remain authoritative. */
final class GiranChaosAgenda {
 static final Random RNG=new Random();
 static final class Route {
  long nextChoice,pauseUntil;Location destination;int selections;final Set<String> choices=new HashSet<>();
  Route(Squad s){s.routeLane=RNG.nextBoolean()?0:1;}
 }
 static final int[][] COURT={{113650,145095,-2648},{114174,145058,-2648},{114650,145095,-2648}};
 static final int[][] HALL={{115700,145035,-2560},{116200,145095,-2560},{116650,145095,-2560},{117400,145064,-2640}};
 private static Location pick(int[][] points,Route r,long now){
  int[] xyz=points[RNG.nextInt(points.length)];Location point=SiegeAgenda.safe(xyz[0]+RNG.nextInt(161)-80,xyz[1]+RNG.nextInt(161)-80,xyz[2]);
  r.destination=point;r.nextChoice=now+8000+RNG.nextInt(15000);r.pauseUntil=now+RNG.nextInt(1800);r.selections++;r.choices.add(point.getX()+":"+point.getY()+":"+point.getZ());return point;
 }
 void update(Squad s,Route route,Player human,String orders,long now){
  s.leader=SiegeAgenda.captain(s);s.conquest=false;if(s.leader==null)return;
  if(s.id<5){defense(s,route,human,orders,now);return;}
  Player lead=s.leader;boolean north=s.routeLane==1;
  Door outer=door(north?23220001:23220002),inner=door(north?23220005:23220006);
  Creature enemy=s.members.stream().filter(a->a.p==lead).map(SiegeAgenda::escortTarget).filter(Objects::nonNull).findFirst().orElse(null);
  SiegeAgenda.Task barrier=lead.getX()<112950&&closed(outer)?(north?SiegeAgenda.OUTER_N:SiegeAgenda.OUTER_S):lead.getX()<115450&&closed(inner)?(north?SiegeAgenda.INNER_N:SiegeAgenda.INNER_S):null;
  if(barrier!=null){s.goal=SiegeAgenda.route(s,lead,barrier);Door gate=door(barrier.id());s.focus=enemy!=null&&lead.calculateDistance2D(enemy)<750?enemy:gate;s.objective=barrier.name()+" / combatir amenazas";return;}
  s.focus=enemy;
  if(lead.isClanLeader()){
   Creature artifact=GiranRules.castle().getArtefacts().iterator().next();s.goal=SiegeAgenda.captureApproach(s,lead,artifact);s.conquest=true;s.objective="Darion al artefacto; escolta combate";return;
  }
  if(lead.getX()<112950){s.goal=SiegeAgenda.route(s,lead,SiegeAgenda.COURT);s.objective="Entrada "+(north?"norte":"sur");return;}
  if(lead.getX()<115450){
   // Parties vary court pauses, then push toward the interior instead of roaming outside forever.
   if(route.destination==null||now>=route.nextChoice)pick(COURT,route,now);
   if(route.selections%3==0||lead.getX()>114300){s.goal=SiegeAgenda.route(s,lead,SiegeAgenda.HALL);s.objective="Presionar acceso interior";}
   else{s.goal=route.destination;s.objective="Hostigar patio / reagrupar";}
  }else{
   if(route.destination==null||route.destination.getX()<115450||now>=route.nextChoice||lead.calculateDistance2D(route.destination)<100)pick(HALL,route,now);
   s.goal=route.destination;s.objective=s.members.size()==1?"Incursion independiente":"Buscar defensores / cubrir otro grupo";
  }
  if(enemy==null&&now<route.pauseUntil)s.goal=new Location(lead);
 }
 private void defense(Squad s,Route route,Player human,String orders,long now){
  Player lead=s.leader;
  List<Creature> threats=new ArrayList<>();World.forEachVisibleObjectInRange(lead,Creature.class,1300,t->{if(t.isPlayable()&&!t.isInvul()&&!t.isInvisible()&&SiegeSquadBrain.allowed(t,lead)&&GeoEngine.getInstance().canSeeTarget(lead,t))threats.add(t);});
  Creature enemy=threats.stream().min(Comparator.comparingDouble(lead::calculateDistance2D)).orElse(null);s.focus=enemy;
  if(human!=null&&orders.equals("seguir")){s.goal=human;s.objective="Proteger a Hellkevin";if(human.getTarget() instanceof Creature t&&SiegeSquadBrain.allowed(t,lead))s.focus=t;return;}
  if(orders.equals("retirada")){s.goal=GiranChaosSiege.instance.spawnPoint(lead,s.id,0);s.objective="Retirada defensora";return;}
  int[] home=GiranChaosSiege.POSTS[s.id];
  if(enemy!=null){s.goal=new Location(enemy);s.objective="Interceptar atacante";return;}
  if(route.destination==null||now>=route.nextChoice||lead.calculateDistance2D(route.destination)<100){
   int[][] patrol=s.id==1?COURT:s.id==2?new int[][]{home,{116200,145095,-2560}}:s.id==4?new int[][]{home,{116650,145095,-2560}}:HALL;
   pick(patrol,route,now);
  }
  s.goal=now<route.pauseUntil?new Location(lead):route.destination;s.objective="Patrullar sector / acudir a amenazas";
 }
 static Door door(int id){return GiranRules.castle().getDoors().stream().filter(d->d.getId()==id).findFirst().orElse(null);}
 static boolean closed(Door d){return d!=null&&!d.isDead()&&!d.isOpen();}
}
