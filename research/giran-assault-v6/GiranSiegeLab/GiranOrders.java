package custom.GiranSiegeLab;

import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import custom.GiranSiegeLab.GiranSiegeLab.*;

/** Commands belong to the operator's current friendly side, never to every registered clan. */
final class GiranOrders {
 static boolean allied(Player pilot,Player commander){
  if(pilot==null||commander==null||pilot.getClan()==null||commander.getClan()==null)return false;
  return pilot.getClanId()==commander.getClanId()||pilot.getAllyId()!=0&&pilot.getAllyId()==commander.getAllyId()||GiranRules.defender(pilot)&&GiranRules.defender(commander);
 }
 static String effective(Squad s,Player commander,String requested){return s.members.stream().anyMatch(a->allied(a.p,commander))?requested:"asalto";}
 static boolean summonHere(Pilot a,Player commander){
  if(!a.bot||a.p.isDead()||!allied(a.p,commander))return false;
  var geo=GeoEngine.getInstance();Location spot=null;
  search: for(int radius:new int[]{64,96,128})for(int i=0;i<8;i++){double angle=(i+a.slot*2)*Math.PI/4;int x=commander.getX()+(int)(Math.cos(angle)*radius),y=commander.getY()+(int)(Math.sin(angle)*radius),z=geo.getHeight(x,y,commander.getZ());
   if(Math.abs(z-commander.getZ())<=40&&SiegeAgenda.open(x,y,z)&&geo.canMoveToTarget(commander.getX(),commander.getY(),commander.getZ(),x,y,z,commander.getInstanceId())){spot=new Location(x,y,z);break search;}
  }
  if(spot==null)return false;
  a.p.abortAttack();a.p.abortCast();a.p.getAI().setIntentionIdle();GiranSiegeLab.move(a.p,spot);a.lastDestination=null;a.lastProgress=System.currentTimeMillis();a.progressX=a.p.getX();a.progressY=a.p.getY();a.nextThink=0;
  return true;
 }
}
