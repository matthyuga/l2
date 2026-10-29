package custom.EquipmentShowcase;

import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.script.Script;

/** Passive display only. No accounts, inventories, combat AI or rewards. */
public class EquipmentShowcase extends Script implements IVoicedCommandHandler {
    public static final int FIRST=62000, LAST=62156;
    private static final Logger LOG=Logger.getLogger(EquipmentShowcase.class.getName());
    private EquipmentShowcase(){
        int[] ids=new int[LAST-FIRST+1];for(int i=0;i<ids.length;i++)ids[i]=FIRST+i;
        addSpawnId(ids);
        VoicedCommandHandler.getInstance().registerHandler(this);
        // Startup order may put XML spawns before script registration.
        ThreadPool.schedule(()->{
            int count=0;
            for(var object:World.getVisibleObjects())if(object instanceof Npc npc && owns(npc)){protect(npc);count++;}
            LOG.info("EQUIPMENT_SHOWCASE: "+count+" passive mannequins protected in Giran; no player profiles created.");
        },2000);
    }
    public static boolean owns(Npc npc){return npc.getId()>=FIRST && npc.getId()<=LAST;}
    public static void protect(Npc npc){
        if(!owns(npc))return;
        npc.setInvul(true);npc.setImmobilized(true);npc.setAutoAttackable(false);
        npc.setRandomWalking(false);npc.setRandomAnimationEnabled(false);
    }
    @Override public void onSpawn(Npc npc){protect(npc);}
    @Override public String[] getCommandList(){return new String[]{"galeria"};}
    @Override public boolean onCommand(String command,Player player,String params){
        if(!player.isGM()){player.sendMessage("Galeria: acceso de laboratorio GM.");return true;}
        if(player.isInCombat()){player.sendMessage("Espera a salir de combate para ir a la galeria.");return true;}
        if(player.getInstanceId()!=0){player.sendMessage("Sal de la instancia antes de ir a la galeria de Giran.");return true;}
        player.teleToLocation(81920,147950,-3400);
        player.sendMessage("Giran: 157 maniquies; anillos interiores de sets, exteriores de armas y accesorios.");return true;
    }
    public static void main(String[] args){new EquipmentShowcase();}
}
