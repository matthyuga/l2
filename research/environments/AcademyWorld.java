package custom.AcademyWorld;

import java.util.logging.Logger;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerLogin;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;

/** Local Academy profile only. Does not register travel to other maps. */
public final class AcademyWorld extends Script
{
    private static final Logger LOG = Logger.getLogger(AcademyWorld.class.getName());
    public static boolean inside(int x, int y, int z, int instance)
    {
        return instance == 0 && x >= 145500 && x <= 153000 && y >= 43000 && y <= 49500 && z >= -5000 && z <= -1500;
    }
    private static void contain(Player p)
    {
        if (p == null || p.isTeleporting() || p.isLabControlled() || inside(p.getX(), p.getY(), p.getZ(), p.getInstanceId())) return;
        p.teleToLocation(148900, 46100, -3400, 0, 0, false);
        p.sendMessage("L2 Academy: el area habilitada es el Coliseo.");
    }
    private AcademyWorld()
    {
        Containers.Players().addListener(new ConsumerEventListener(Containers.Players(), EventType.ON_PLAYER_LOGIN,
            (OnPlayerLogin e) -> ThreadPool.schedule(() -> contain(e.getPlayer()), 1500), this));
        ThreadPool.scheduleAtFixedRate(() -> { for (Player p : World.getPlayers()) contain(p); }, 2000, 500);
        if (!inside(148900, 46100, -3400, 0) || inside(82698, 148638, -3473, 0)
            || inside(149000, 46700, 12040, 0) || inside(148900, 46100, -3400, 1))
            throw new IllegalStateException("Academy boundary verification failed");
        LOG.info("ACADEMY_WORLD_READY: local single-player; Coliseum boundary, Giran/dock/instance exclusion checks PASS.");
        if (Boolean.getBoolean("academy.verify")) ThreadPool.schedule(AcademyWorld::verifyReturn, 15000);
    }
    private static void verifyReturn()
    {
        Player probe = null;
        try
        {
            var template = PlayerTemplateData.getInstance().getTemplate(0);
            var ctor = Player.class.getDeclaredConstructor(template.getClass(), String.class, PlayerAppearance.class);
            ctor.setAccessible(true);
            probe = ctor.newInstance(template, "academy-transient-probe", new PlayerAppearance((byte)0,(byte)0,(byte)0,false));
            probe.setName("AcademyBoundaryProbe");
            probe.setAccessLevel(0);
            probe.setDead(false);
            probe.setOnlineStatus(true, false);
            probe.setEnteredWorld();
            probe.spawnMe(82698,148638,-3473);
            contain(probe);
            probe.onTeleported();
            if (!inside(probe.getX(),probe.getY(),probe.getZ(),probe.getInstanceId())) throw new IllegalStateException("Giran return failed");
            probe.setXYZInvisible(149000,46700,12040);
            contain(probe);
            probe.onTeleported();
            if (!inside(probe.getX(),probe.getY(),probe.getZ(),probe.getInstanceId())) throw new IllegalStateException("Sky dock return failed");
            LOG.info("ACADEMY_RETURN_TEST PASS: actual Player returned from Giran and sky dock; transient actor only, no account or character inserted.");
        }
        catch (Exception e) { LOG.log(java.util.logging.Level.SEVERE,"ACADEMY_RETURN_TEST FAIL",e); }
        finally { if (probe != null) { probe.deleteMe(); probe.setOnlineStatus(false,false); } }
    }
    public static void main(String[] args) { new AcademyWorld(); }
}
