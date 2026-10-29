package custom.ElvenPvpRoom;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.geoengine.pathfinding.PathFinding;
import org.l2jmobius.gameserver.managers.RoomCombatRules;

/** Ground-checked spawn dispersion and local movement. Never teleports combatants. */
public final class RoomSpatialTactics {
 private RoomSpatialTactics(){}
 public static Location spawn(PvpRoomConfig.ArenaMap map,RoundState.Mode mode,int team,Player actor,List<Player> members){
  var geo=GeoEngine.getInstance();List<Location> candidates=new ArrayList<>();
  List<Location> bases=mode.teams==0?map.spawns():List.of(map.spawns().get(team));
  for(Location base:bases){
   candidates.add(map.safe(base));
   for(int radius:new int[]{96,192,288,384,512,640,768})for(int i=0;i<24;i++){
    double a=i*Math.PI/12;int x=base.getX()+(int)(Math.cos(a)*radius),y=base.getY()+(int)(Math.sin(a)*radius);
    int z=geo.getHeight(x,y,base.getZ());Location point=new Location(x,y,z);
    if(map.inside(point)&&geo.hasGeo(x,y)&&Math.abs(z-base.getZ())<=64&&(geo.canMoveToTarget(x,y,z,x+32,y,z,actor.getInstanceId())&&geo.canMoveToTarget(x,y,z,x-32,y,z,actor.getInstanceId())||geo.canMoveToTarget(x,y,z,x,y+32,z,actor.getInstanceId())&&geo.canMoveToTarget(x,y,z,x,y-32,z,actor.getInstanceId())))candidates.add(point);
   }
  }
  Collections.shuffle(candidates);Location best=candidates.get(0);double scoreBest=-Double.MAX_VALUE;
  for(Location point:candidates){
   double clearance=1400;
   for(Player other:members)if(other!=actor&&other.isOnline()&&!other.isDead()&&map.inside(new Location(other))){
    double distance=Math.hypot(point.getX()-(double)other.getX(),point.getY()-(double)other.getY());
    clearance=Math.min(clearance,distance);
   }
   // Prefer somewhere different from the death point, without overriding enemy clearance.
   double score=clearance+Math.min(300,Math.hypot(point.getX()-(double)actor.getX(),point.getY()-(double)actor.getY()))*.10;
   if(score>scoreBest){scoreBest=score;best=point;}
  }
  return new Location(best.getX(),best.getY(),best.getZ(),ThreadLocalRandom.current().nextInt(65536));
 }
 public static Location step(Player p,int x,int y,PvpRoomConfig.ArenaMap map){
  var geo=GeoEngine.getInstance();double dx=x-(double)p.getX(),dy=y-(double)p.getY(),distance=Math.hypot(dx,dy);
  if(distance<8)return null;double angle=Math.atan2(dy,dx);
  for(double length:new double[]{Math.min(distance,350),Math.min(distance,140),Math.min(distance,70)})
   for(int offset:new int[]{0,30,-30,60,-60}){
    double a=angle+Math.toRadians(offset);int xx=p.getX()+(int)(Math.cos(a)*length),yy=p.getY()+(int)(Math.sin(a)*length);
    int z=geo.getHeight(xx,yy,p.getZ());Location dest=new Location(xx,yy,z);
    if(map.inside(dest)&&geo.hasGeo(xx,yy)&&Math.abs(z-p.getZ())<=96&&geo.canMoveToTarget(p.getX(),p.getY(),p.getZ(),xx,yy,z,p.getInstanceId()))return dest;
   }
  int targetZ=geo.getHeight(x,y,p.getZ());
  if(map.inside(new Location(x,y,targetZ))&&Math.abs(targetZ-p.getZ())<=96){
   var path=PathFinding.getInstance().findPath(p.getX(),p.getY(),p.getZ(),x,y,targetZ,p.getInstanceId(),true);
   if(path!=null)for(var node:path){
    double length=Math.hypot(node.getX()-(double)p.getX(),node.getY()-(double)p.getY());Location waypoint=new Location(node.getX(),node.getY(),node.getZ());
    if(length>8&&length<700&&map.inside(waypoint)&&Math.abs(node.getZ()-p.getZ())<=96&&geo.canMoveToTarget(p.getX(),p.getY(),p.getZ(),node.getX(),node.getY(),node.getZ(),p.getInstanceId()))return waypoint;
   }
  }
  return null;
 }
 public static Location spacing(Player p,Player enemy,List<Player> members,PvpRoomConfig.ArenaMap map,RoomTacticalPolicy.Role role){
  boolean ranged=role==RoomTacticalPolicy.Role.MAGE||role==RoomTacticalPolicy.Role.ARCHER||role==RoomTacticalPolicy.Role.HEALER||role==RoomTacticalPolicy.Role.BUFFER||role==RoomTacticalPolicy.Role.SUMMONER;
  double dx=0,dy=0;int threats=0;
  if(ranged){
   for(Player q:members)if(q!=p&&!q.isDead()&&q.getInstanceId()==p.getInstanceId()&&RoomCombatRules.decision(p,q)==1){
    double d=p.calculateDistance2D(q);if(d<430&&Math.abs(p.getZ()-q.getZ())<120){
     double weight=(430-d)/Math.max(1,d);dx+=(p.getX()-q.getX())*weight;dy+=(p.getY()-q.getY())*weight;threats++;
    }
   }
  }
  if(threats>0){
   if(Math.hypot(dx,dy)<1){dx=p.getX()-enemy.getX();dy=p.getY()-enemy.getY();if(Math.hypot(dx,dy)<1)dx=(p.getObjectId()%2==0?1:-1);}
   double len=Math.max(1,Math.hypot(dx,dy));return step(p,p.getX()+(int)(dx/len*280),p.getY()+(int)(dy/len*280),map);
  }
  // Daggers seek a flank; other melee only separate when bodies overlap.
  boolean crowded=false;for(Player q:members)if(q!=p&&!q.isDead()&&q.getInstanceId()==p.getInstanceId()&&p.calculateDistance2D(q)<55){crowded=true;break;}
  if(!ranged&&enemy!=null&&p.calculateDistance2D(enemy)<200&&(crowded||role==RoomTacticalPolicy.Role.DAGGER)){
   double angle=enemy.getHeading()*Math.PI/32768+Math.PI;
   if(role!=RoomTacticalPolicy.Role.DAGGER)angle=Math.atan2(p.getY()-enemy.getY(),p.getX()-enemy.getX())+(p.getObjectId()%2==0?.9:-.9);
   int x=enemy.getX()+(int)(Math.cos(angle)*90),y=enemy.getY()+(int)(Math.sin(angle)*90);
   if(Math.hypot(x-p.getX(),y-p.getY())>65)return step(p,x,y,map);
  }
  return null;
 }
}
