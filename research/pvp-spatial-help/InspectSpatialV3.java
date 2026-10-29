import java.lang.instrument.*;
import java.nio.file.*;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.geoengine.pathfinding.PathFinding;
public class InspectSpatialV3 {
 public static void agentmain(String directory,Instrumentation inst)throws Exception{
  StringBuilder b=new StringBuilder();var geo=GeoEngine.getInstance();
  for(String name:new String[]{"ArenaThalion","ArenaDraven"}){var p=World.getPlayer(name);if(p==null)continue;
   b.append(name).append(" xyz=").append(p.getLocation()).append(" movementDisabled=").append(p.isMovementDisabled()).append(" overloaded=").append(p.isOverloaded()).append(" root=").append(p.isRooted()).append(" immobilized=").append(p.isImmobilized()).append(" weightPenalty=").append(p.getWeightPenalty()).append(" casting=").append(p.isCastingNow()).append(" intention=").append(p.getAI().getIntention()).append(" HP=").append(p.getCurrentHp()).append('\n');
   b.append("load=").append(p.getCurrentLoad()).append(" max=").append(p.getMaxLoad()).append("\n");for(var item:p.getInventory().getItems())if((long)item.getCount()*item.getTemplate().getWeight()>2000)b.append("ITEM ").append(item.getId()).append(" ").append(item.getName()).append(" count=").append(item.getCount()).append(" weight=").append((long)item.getCount()*item.getTemplate().getWeight()).append("\n");
   for(int i=0;i<8;i++){double a=i*Math.PI/4;int x=p.getX()+(int)(Math.cos(a)*32),y=p.getY()+(int)(Math.sin(a)*32),z=geo.getHeight(x,y,p.getZ());b.append("neighbor ").append(x).append(',').append(y).append(',').append(z).append(" canmove=").append(geo.canMoveToTarget(p.getX(),p.getY(),p.getZ(),x,y,z,p.getInstanceId())).append('\n');}
   var path=PathFinding.getInstance().findPath(p.getX(),p.getY(),p.getZ(),p.getX()+300,p.getY(),geo.getHeight(p.getX()+300,p.getY(),p.getZ()),p.getInstanceId(),true);b.append("path sample=").append(path==null?"null":path.size()).append('\n');
  }
  Files.writeString(Path.of(directory,"geometry-diagnostic.txt"),b);
 }
}
