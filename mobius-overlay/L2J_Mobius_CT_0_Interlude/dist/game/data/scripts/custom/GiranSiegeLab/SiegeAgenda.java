package custom.GiranSiegeLab;

import java.util.*;
import java.util.logging.Logger;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.*;
import org.l2jmobius.gameserver.entity.actor.instance.Door;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.managers.CastleManager;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Each party owns its objective, captain and route; rival leaders contest the native artifact. */
final class SiegeAgenda {
 private static final Logger LOG=Logger.getLogger(SiegeAgenda.class.getName());
 record Task(String name,int id,int x,int y,int z,int radius){}
 static final Task OUTER_N=new Task("Puerta exterior norte",23220001,112857,144795,-2832,0),OUTER_S=new Task("Puerta exterior sur",23220002,112857,144930,-2832,0);
 static final Task INNER_N=new Task("Puerta interior norte",23220005,115402,145035,-2560,0),INNER_S=new Task("Puerta interior sur",23220006,115402,145160,-2560,0);
 static final Task CT1=new Task("Cristal de entrada",13002,113115,144829,-2446,0),CT2=new Task("Cristal oriental",13002,118828,145106,-2447,0),CT3=new Task("Cristal central",13002,117329,145041,-2412,0);
 static final Task FT1=new Task("Torre de fuego oriental",13004,118331,145055,-2627,0),FT2=new Task("Torre de fuego norte",13004,117768,143880,-2451,0);
 static final Task ARES=new Task("Ares",903200,114174,145058,-2752,0),NYX=new Task("Nyx",903201,117700,145150,-2640,0);
 static final Task NORTH=new Task("Limpiar patio norte",0,114000,144150,-2752,650),SOUTH=new Task("Limpiar patio sur",0,114000,145800,-2752,650);
 static final Task ESCORT=new Task("Proteger al conquistador",-1,117750,145096,-2640,0);
 static final List<List<Task>> PLANS=List.of(List.of(ESCORT),List.of(OUTER_N,CT1,INNER_N,FT1,ESCORT),List.of(OUTER_S,SOUTH,INNER_S,CT2,ESCORT),List.of(OUTER_N,ARES,INNER_N,CT3,ESCORT),List.of(OUTER_S,NORTH,INNER_S,FT2,NYX,ESCORT));
 static final Task COURT=new Task("Avanzar por el patio",0,114650,145095,-2648,180),HALL=new Task("Despejar sala del trono",0,116650,145095,-2560,180),PASSAGE=new Task("Cruzar al artefacto",0,117544,145064,-2640,60);
 static final List<List<Task>> ASSAULT_PLANS=List.of(List.of(ESCORT),List.of(OUTER_N,COURT,INNER_N,HALL,PASSAGE,ESCORT),List.of(OUTER_S,COURT,INNER_S,HALL,PASSAGE,ESCORT),List.of(OUTER_N,COURT,INNER_N,HALL,PASSAGE,ESCORT),List.of(OUTER_S,COURT,INNER_S,HALL,PASSAGE,ESCORT));
 private final List<Creature> defenders=new ArrayList<>();private final Set<Task> known=new HashSet<>();long refreshAt;
 void clear(){defenders.clear();known.clear();refreshAt=0;SiegeTactics.reset();}
 void refresh(){if(System.currentTimeMillis()<refreshAt)return;refreshAt=System.currentTimeMillis()+5000;defenders.clear();var castle=CastleManager.getInstance().getCastleById(3);
  defenders.addAll(castle.getDoors());for(WorldObject o:World.getVisibleObjects())if(o instanceof Npc n&&(n instanceof Tower||SiegeSquadBrain.GUARDS.contains(n.getId()))&&castle.checkIfInZone(n.getX(),n.getY(),n.getZ()))defenders.add(n);
  for(List<Task> plan:PLANS)for(Task task:plan)if(task.id()>0&&find(task)!=null)known.add(task);
 }
 static Player captain(Squad s){return s.members.stream().filter(a->!a.p.isDead()&&a.slot==0).map(a->a.p).findFirst().orElseGet(()->s.members.stream().filter(a->!a.p.isDead()).map(a->a.p).findFirst().orElse(null));}
 void update(Squad s,Player human,String mode){
  mode=GiranOrders.effective(s,human,mode);
  refresh();Player lead=captain(s);if(lead==null)return;
  s.leader=lead;
  s.conquest=false;
  if(GiranRules.castle().getOwnerId()!=0){competitive(s,human,mode);return;}
  if(mode.equals("seguir")){s.goal=human;s.objective="Escolta y proteccion aliada";s.focus=human.getTarget() instanceof Creature c&&SiegeSquadBrain.allowed(c,lead)?c:threat(s,lead,700);return;}
  Task task=PLANS.get(s.id).get(Math.min(s.step,PLANS.get(s.id).size()-1));
  Creature main=find(task);boolean done=task.id()>0&&(main==null&&(s.seen||known.contains(task))||main!=null&&(main.isDead()||main instanceof Door d&&d.isOpen()));
  if(task.id()>0&&main!=null)s.seen=true;
  final Task prior=task;
  if(task.id()==0)done=lead.calculateDistance2D(task.x(),task.y(),task.z())<400&&defenders.stream().noneMatch(c->c instanceof Npc&&!(c instanceof Tower)&&SiegeSquadBrain.allowed(c,lead)&&c.calculateDistance2D(prior.x(),prior.y(),prior.z())<prior.radius());
  if(done&&s.step<PLANS.get(s.id).size()-1){s.step++;s.seen=false;s.goal=null;task=PLANS.get(s.id).get(s.step);main=find(task);LOG.info("GIRAN_AGENDA "+GiranRoster.CLANS[s.id]+" -> "+task.name());}
  s.objective=task.name();
  if(task.id()==-1){s.goal=human;s.focus=threat(s,human,1200);return;}
  Creature threat=threat(s,lead,800);
  s.focus=main instanceof Door&&SiegeSquadBrain.allowed(main,lead)?main:threat!=null?threat:main!=null&&SiegeSquadBrain.allowed(main,lead)?main:null;
  final Task current=task;
  if(task.id()==0&&s.focus==null)s.focus=defenders.stream().filter(c->c instanceof Npc&&!(c instanceof Tower)&&SiegeSquadBrain.allowed(c,lead)&&c.calculateDistance2D(current.x(),current.y(),current.z())<current.radius()).min(Comparator.comparingDouble(c->lead.calculateDistance2D(c))).orElse(null);
  s.goal=route(s,lead,task);
 }
 void competitive(Squad s,Player human,String mode){
  Player lead=s.leader;var castle=GiranRules.castle();boolean defending=GiranRules.defender(lead);SiegeTactics.update(s);
  Creature rival=enemy(s,lead);
  if(mode.equals("seguir")){s.goal=human;s.objective=defending?"Escoltar al propietario":"Asistir al lider aliado";s.focus=human.getTarget() instanceof Creature t&&SiegeSquadBrain.allowed(t,lead)?t:rival;return;}
  if(defending){s.objective="Defender acceso al artefacto";s.goal=safe(PASSAGE.x(),PASSAGE.y(),PASSAGE.z());s.focus=rival;return;}
  List<Task> plan=ASSAULT_PLANS.get(s.id);
  Task task=plan.get(Math.min(s.step,plan.size()-1));Creature main=find(task);
  if(task.id()>0&&main!=null)s.seen=true;
  boolean done=task.id()>0&&(main==null&&(s.seen||known.contains(task))||main!=null&&(main.isDead()||main instanceof Door d&&d.isOpen()));
  final Task prior=task;
  if(task.id()==0)done=lead.calculateDistance2D(task.x(),task.y(),task.z())<task.radius()&&Math.abs(lead.getZ()-task.z())<80;
  if(done&&s.step<plan.size()-1){s.step++;s.seen=false;task=plan.get(s.step);main=find(task);LOG.info("GIRAN_STAGE "+GiranRoster.CLANS[s.id]+" step="+s.step+" -> "+task.name());}
  s.objective=task.name();
  if(task.id()==-1){Creature artifact=castle.getArtefacts().iterator().next();s.goal=captureApproach(s,lead,artifact);s.objective=engraving(lead)?"Proteger casteo del lider":"Lider al artefacto; escolta despeja";s.conquest=true;main=null;}
  else s.goal=route(s,lead,task);
  Task blocked=unbreached(s,lead);if(blocked!=null){main=find(blocked);s.goal=route(s,lead,blocked);s.conquest=false;s.objective=blocked.name()+" / retomar avance";}
  Creature guard=threat(s,lead,800);Door shared=GiranRules.sharedDoor(lead);
  Door breach=main instanceof Door d&&SiegeSquadBrain.allowed(d,lead)?d:shared;
  if(rival!=null&&!GiranRules.defender(rival.isSummon()?rival.asSummon().getOwner():rival.asPlayer())&&!engraving(rival)&&!breachSkirmish(s,System.currentTimeMillis()))rival=null;
  s.focus=rival!=null?rival:breach!=null?breach:guard!=null?guard:main!=null&&SiegeSquadBrain.allowed(main,lead)?main:null;
 }
 // Rival attackers may retaliate at the entrance, then return to the breach instead of camping each other forever.
 static boolean breachSkirmish(Squad s,long now){if(now<s.nextRivalSkirmish)return false;if(s.rivalUntil==0){s.rivalUntil=now+10000;return true;}if(now<s.rivalUntil)return true;s.rivalUntil=0;s.nextRivalSkirmish=now+20000;return false;}
 Creature enemy(Squad s,Player center){
  List<Creature> choices=new ArrayList<>();World.forEachVisibleObjectInRange(center,Creature.class,1500,t->{if(SiegeSquadBrain.allowed(t,center)&&t.isPlayable())choices.add(t);});
  return choices.stream().filter(t->!t.isInvul()&&!t.isInvisible()&&!SiegeTactics.truce(center,t)&&GeoEngine.getInstance().canSeeTarget(center,t)).filter(t->engraving(t)||attackingParty(t,s)&&center.calculateDistance2D(t)<1200||GiranRules.defender(owner(t))&&center.calculateDistance2D(t)<1300||center.getX()>115450&&center.calculateDistance2D(t)<500)
   .max(Comparator.comparingDouble(t->(engraving(t)?3000:0)+(attackingParty(t,s)?1600:0)+(GiranRules.defender(owner(t))?1200:0)+150*(1-t.getCurrentHp()/Math.max(1,t.getMaxHp()))-center.calculateDistance2D(t)*.2)).orElse(null);
 }
 static Player owner(Creature t){return t.isSummon()?t.asSummon().getOwner():t.asPlayer();}
 static Creature escortTarget(Pilot a){
  return SiegeTactics.localTarget(a);
 }
 static boolean attackingLeader(Creature t,Squad s){return s.leader!=null&&t.hasAI()&&(t.getAI().getAttackTarget()==s.leader||t.getAI().getCastTarget()==s.leader);}
 static boolean engageAttacker(Squad s,Creature t,long now){return !SiegeTactics.truce(s.leader,t)&&(GiranRules.defender(owner(t))||engraving(t)||s.conquest&&attackingLeader(t,s)||now>=s.nextRivalSkirmish);}
 static boolean allowedPursuit(Pilot a,long now){return a.pursuit!=null&&now<a.pursuitUntil&&engageAttacker(a.squad,a.pursuit,now)&&SiegeSquadBrain.allowed(a.pursuit,a.p)&&a.p.calculateDistance2D(a.pursuit)<1500&&a.pursuitOrigin!=null&&a.pursuit.calculateDistance2D(a.pursuitOrigin)<1600&&GeoEngine.getInstance().canSeeTarget(a.p,a.pursuit);}
 static boolean attackingParty(Creature t,Squad s){return t.hasAI()&&s.members.stream().anyMatch(a->t.getAI().getAttackTarget()==a.p||t.getAI().getCastTarget()==a.p);}
 static boolean engraving(Creature t){Player p=t.asPlayer();return p!=null&&p.isCastingNow()&&p.getCurrentSkill()!=null&&p.getCurrentSkill().getSkill().getId()==246;}
 Task unbreached(Squad s,Player p){Task t=p.getX()<112880?(north(s)?OUTER_N:OUTER_S):p.getX()<115430?(north(s)?INNER_N:INNER_S):null;Creature c=t==null?null:find(t);return c instanceof Door d&&SiegeSquadBrain.allowed(d,p)?t:null;}
 static Location captureApproach(Squad s,Player p,Creature artifact){
  if(p.getX()<117500)return route(s,p,PASSAGE);
  if(p.getX()<117560)return safe(117608,145064,-2592);
  if(p.getX()<117650)return safe(117704,145064,-2528);
  if(p.getX()<117850)return safe(117880,145064,-2528);
  return sealPosition(artifact);
 }
 static Location sealPosition(Creature artifact){
  for(int radius:new int[]{32,48,64,0})for(int i:new int[]{6,4,2,0,5,7,3,1}){int x=artifact.getX()+(int)(Math.cos(i*Math.PI/4)*radius),y=artifact.getY()+(int)(Math.sin(i*Math.PI/4)*radius);int z=GeoEngine.getInstance().getHeight(x,y,artifact.getZ());if(z>=artifact.getZ()&&z-artifact.getZ()<=45&&open(x,y,z))return new Location(x,y,z);}
  return safe(artifact.getX(),artifact.getY(),artifact.getZ());
 }
 Creature find(Task t){if(t.id()<=0)return null;return defenders.stream().filter(c->c instanceof Door d?d.getId()==t.id():c instanceof Npc n&&n.getId()==t.id()&&c.calculateDistance2D(t.x(),t.y(),t.z())<220).min(Comparator.comparingDouble(c->c.calculateDistance2D(t.x(),t.y(),t.z()))).orElse(null);}
 Creature threat(Squad s,Creature center,int range){return defenders.stream().filter(c->c instanceof Npc&&!(c instanceof Tower)&&SiegeSquadBrain.allowed(c,s.leader)&&c.calculateDistance2D(center)<range&&GeoEngine.getInstance().canSeeTarget(s.leader,c)).max(Comparator.comparingDouble(c->(s.members.stream().anyMatch(a->c.getTarget()==a.p)?2000:0)+1000/(1+s.leader.calculateDistance2D(c)/100))).orElse(null);}
 static Location route(Squad s,Player p,Task task){
  if(p.getX()<112250&&task.x()>112250){int approachY=north(s)?144400:145350;
   if(Math.abs(p.getY()-approachY)>400)return safe(111400,approachY,-2832);
   return safe(112400,north(s)?144790:144940,-2832);
  }
  // Shared chokepoints have to be breached. Once inside, parties split toward their assigned objectives.
  int lane=north(s)?144790:144940;
  if(task.id()>20000000&&p.getX()<task.x())return safe(task.x()-200,task.y(),task.z());
  if(p.getX()<112950&&task.x()>113000)return safe(113250,lane,-2832);
  if(p.getX()<114450&&task.x()>115450)return safe(114650,145095,-2752);
  if(p.getX()<115250&&task.x()>115450)return safe(115700,north(s)?145035:145160,-2560);
  if(p.getX()<116500&&task.x()>117000)return safe(116650,145095,-2560);
  return safe(task.x(),task.y(),task.z());
 }
 static boolean north(Squad s){return s.routeLane<0?s.id%2==1:s.routeLane==1;}
 static Location safe(int x,int y,int hint){GeoEngine geo=GeoEngine.getInstance();int z=geo.getHeight(x,y,hint);
  if(open(x,y,z))return new Location(x,y,z);
  for(int r:new int[]{32,64,128,192,256})for(int i=0;i<8;i++){int nx=x+(int)(Math.cos(i*Math.PI/4)*r),ny=y+(int)(Math.sin(i*Math.PI/4)*r),nz=geo.getHeight(nx,ny,hint);if(Math.abs(nz-hint)<220&&open(nx,ny,nz))return new Location(nx,ny,nz);}
  return new Location(x,y,z);
 }
 static boolean open(int x,int y,int z){return GeoEngine.getInstance().checkNearestNswe(GeoEngine.getGeoX(x),GeoEngine.getGeoY(y),z,15);}
}
