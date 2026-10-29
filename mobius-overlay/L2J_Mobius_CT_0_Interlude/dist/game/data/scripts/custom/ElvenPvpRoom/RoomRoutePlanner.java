package custom.ElvenPvpRoom;
import java.util.*;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.geoengine.pathfinding.PathFinding;

/** Room-scoped, layered geodata routes. Every segment must be traversable in the native engine. */
public final class RoomRoutePlanner {
 private record Cell(int x,int y,int z){}
 private record Open(Cell cell,double cost,double score){}
 private RoomRoutePlanner(){}
 public static List<Location> plan(Location start,Location goal,PvpRoomConfig.ArenaMap map,int instance){
  var geo=GeoEngine.getInstance();Location a=new Location(start.getX(),start.getY(),geo.getHeight(start.getX(),start.getY(),start.getZ()));Location b=new Location(goal.getX(),goal.getY(),geo.getHeight(goal.getX(),goal.getY(),goal.getZ()));
  if(!map.inside(a)||!map.inside(b))return List.of();
  if(walk(a,b,instance))return List.of(b);
  var nativePath=PathFinding.getInstance().findPath(a.getX(),a.getY(),a.getZ(),b.getX(),b.getY(),b.getZ(),instance,true);
  if(nativePath!=null){List<Location> points=new ArrayList<>();Location previous=a;boolean valid=true;
   for(var node:nativePath){Location point=new Location(node.getX(),node.getY(),node.getZ());if(!map.inside(point)||!walk(previous,point,instance)){valid=false;break;}points.add(point);previous=point;}
   if(valid&&!points.isEmpty()&&walk(previous,b,instance)){points.add(b);return compact(a,points,instance);}
  }
  // Unlike the core's obstructed-node filter, use the same directional checks as actual movement.
  long deadline=System.nanoTime()+400_000_000L;int expanded=0;
  Cell first=new Cell(a.getX(),a.getY(),a.getZ());PriorityQueue<Open> open=new PriorityQueue<>(Comparator.comparingDouble(Open::score));
  Map<Cell,Double> costs=new HashMap<>();Map<Cell,Cell> parents=new HashMap<>();costs.put(first,0d);open.add(new Open(first,0,heuristic(first,b)));
  while(!open.isEmpty()&&expanded++<45000){
   if((expanded&255)==0&&System.nanoTime()>deadline)break;
   Open current=open.poll();Cell c=current.cell();if(current.cost()>costs.getOrDefault(c,Double.MAX_VALUE)+.01)continue;
   Location here=new Location(c.x(),c.y(),c.z());
   if(Math.hypot(c.x()-b.getX(),c.y()-b.getY())<48&&Math.abs(c.z()-b.getZ())<=64&&walk(here,b,instance)){
    LinkedList<Location> route=new LinkedList<>();route.add(b);Cell node=c;
    while(!node.equals(first)){route.addFirst(new Location(node.x(),node.y(),node.z()));node=parents.get(node);if(node==null)return List.of();}
    return compact(a,route,instance);
   }
   for(int dx=-16;dx<=16;dx+=16)for(int dy=-16;dy<=16;dy+=16){
    if(dx==0&&dy==0)continue;int x=c.x()+dx,y=c.y()+dy,z=geo.getHeight(x,y,c.z());Location dest=new Location(x,y,z);
    if(!map.inside(dest)||Math.abs(z-c.z())>64||!walk(here,dest,instance))continue;
    Cell next=new Cell(x,y,z);double cost=current.cost()+Math.hypot(dx,dy)+Math.abs(z-c.z())*.25;
    if(cost>=costs.getOrDefault(next,Double.MAX_VALUE))continue;costs.put(next,cost);parents.put(next,c);open.add(new Open(next,cost,cost+heuristic(next,b)));
   }
  }
  return List.of();
 }
 private static double heuristic(Cell cell,Location goal){return Math.hypot(cell.x()-goal.getX(),cell.y()-goal.getY())+Math.abs(cell.z()-goal.getZ())*.5;}
 public static boolean walk(Location a,Location b,int instance){return GeoEngine.getInstance().canMoveToTarget(a.getX(),a.getY(),a.getZ(),b.getX(),b.getY(),b.getZ(),instance);}
 private static List<Location> compact(Location start,List<Location> points,int instance){
  List<Location> result=new ArrayList<>();Location previous=start;int index=0;
  while(index<points.size()){
   int best=index;for(int j=index+1;j<Math.min(points.size(),index+80);j++)if(walk(previous,points.get(j),instance))best=j;
   Location next=points.get(best);if(Math.hypot(next.getX()-previous.getX(),next.getY()-previous.getY())>4||Math.abs(next.getZ()-previous.getZ())>8){result.add(next);previous=next;}index=best+1;
  }
  return List.copyOf(result);
 }
}
