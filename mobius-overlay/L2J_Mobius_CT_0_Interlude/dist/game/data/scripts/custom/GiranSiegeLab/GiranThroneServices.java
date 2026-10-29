package custom.GiranSiegeLab;

import java.util.*;
import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.NpcData;
import org.l2jmobius.gameserver.entity.*;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.spawns.Spawn;
import org.l2jmobius.gameserver.mechanics.script.Script;

/** Additional instances of the existing Coliseum shop/buffer; their native service handlers and originals remain. */
public class GiranThroneServices extends Script {
 private static final Logger LOG=Logger.getLogger(GiranThroneServices.class.getName());
 static GiranThroneServices instance;final List<Npc> actors=new ArrayList<>();
 public GiranThroneServices(){instance=this;ThreadPool.scheduleAtFixedRate(this::ensure,12000,30000);}
 synchronized void ensure(){try{for(int[] d:new int[][]{{50010,116650,144720,-2560},{50008,116650,145470,-2560}}){
   Location loc=SiegeAgenda.safe(d[1],d[2],d[3]);Npc existing=World.getVisibleObjects().stream().filter(o->o instanceof Npc n&&n.getId()==d[0]&&!n.isDead()&&n.calculateDistance3D(loc)<100).map(o->(Npc)o).findFirst().orElse(null);
   if(existing==null){Spawn spawn=new Spawn(NpcData.getInstance().getTemplate(d[0]));spawn.setLocation(loc);spawn.setHeading(d[0]==50010?16384:49152);spawn.setRespawnDelay(60);existing=spawn.doSpawn(false);existing.setInvul(true);existing.setImmobilized(true);LOG.info("GIRAN_V8_SERVICE "+existing.getName()+" id="+d[0]+" xyz="+existing.getX()+","+existing.getY()+","+existing.getZ());}
   if(!actors.contains(existing))actors.add(existing);
  }}catch(Exception e){LOG.log(java.util.logging.Level.SEVERE,"Giran throne services",e);}}
 public static void main(String[] args){new GiranThroneServices();}
}
