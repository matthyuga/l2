package org.l2jmobius.gameserver.managers;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.l2jmobius.gameserver.entity.actor.Player;

/** Reject queued pre-teleport coordinates without despawning or protecting the actor. */
public final class RoomTeleportSync
{
    private record Guard(int instance, long until) { }
    private static final Map<Integer, Guard> GUARDS = new ConcurrentHashMap<>();
    private static final long WINDOW = 6_000_000_000L;
    private RoomTeleportSync() { }

    public static void arm(Player player, int instance)
    {
        long now = System.nanoTime();
        GUARDS.entrySet().removeIf(e -> now - e.getValue().until() >= 0);
        GUARDS.put(player.getObjectId(), new Guard(instance, now + WINDOW));
    }

    public static boolean reject(Player player, int x, int y, int z)
    {
        Guard guard = GUARDS.get(player.getObjectId());
        if (guard == null) return false;
        if (System.nanoTime() - guard.until() >= 0)
        {
            GUARDS.remove(player.getObjectId(), guard);
            return false;
        }
        if (player.getInstanceId() != guard.instance()) return false;
        // Compare with the authoritative CURRENT position, allowing legitimate continued movement.
        double dx = (double)x - player.getX(), dy = (double)y - player.getY();
        return dx*dx + dy*dy > 360000 || Math.abs((long)z - player.getZ()) > 1000;
    }
}
