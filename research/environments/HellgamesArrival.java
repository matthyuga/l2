package custom.HellgamesArrival;

import java.util.logging.Logger;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

/** Public arrival travel only. Does not load the Lab airship/resort/crew scripts. */
public final class HellgamesArrival implements IVoicedCommandHandler
{
    private HellgamesArrival()
    {
        VoicedCommandHandler.getInstance().registerHandler(this);
        Logger.getLogger(HellgamesArrival.class.getName()).info("HELLGAMES_ARRIVAL_READY: shared dock and Giran exit; no experimental scripts or spawns.");
    }
    public String[] getCommandList() { return new String[]{"muelle"}; }
    public boolean onCommand(String command, Player p, String params)
    {
        if (p.isDead() || p.isInCombat() || p.isTeleporting() || p.isFlying() || p.isInOlympiadMode()
            || p.getInstanceId()!=0 || p.getPvpFlag()>0 || p.getKarma()>0 || p.isInStoreMode() || p.isProcessingTransaction())
        { p.sendMessage("Para viajar debes estar vivo y fuera de combate, comercio y eventos."); return true; }
        String action = params == null ? "" : params.trim();
        if (action.equalsIgnoreCase("giran"))
        {
            if (p.getX()<145000 || p.getX()>151000 || p.getY()<44000 || p.getY()>50000 || p.getZ()<9500)
            { p.sendMessage("La salida a Giran parte del muelle."); return true; }
            p.teleToLocation(82698,148638,-3473,0,0,false);
        }
        else if (action.isEmpty())
        {
            int floor = GeoEngine.getInstance().getHeight(149000,46700,12040);
            if (Math.abs(floor-12040)>100) { p.sendMessage("La llegada no esta disponible. Avisa al administrador."); return true; }
            p.teleToLocation(149000,46700,floor+24,0,0,false);
            p.sendMessage("Bienvenido al muelle de Hellgames. Salida: .muelle giran");
        }
        else p.sendMessage(".muelle | .muelle giran");
        return true;
    }
    public static void main(String[] args) { new HellgamesArrival(); }
}
