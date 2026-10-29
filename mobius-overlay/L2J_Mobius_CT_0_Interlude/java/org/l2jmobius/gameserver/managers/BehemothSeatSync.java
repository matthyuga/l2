package org.l2jmobius.gameserver.managers;

import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.network.serverpackets.ActionFailed;
import org.l2jmobius.gameserver.network.serverpackets.ValidateLocation;

/** Opt-in seat protection. An empty registry has no effect on ordinary players. */
public final class BehemothSeatSync
{
    private record Seat(Player player, Consumer<Location> control) { }
    private static final ConcurrentHashMap<Integer,Seat> SEATS=new ConcurrentHashMap<>();
    private BehemothSeatSync() { }
    public static boolean bind(Player player, Consumer<Location> control)
    {
        if(player==null || control==null)throw new IllegalArgumentException("Seat requires player and controller");
        return SEATS.putIfAbsent(player.getObjectId(),new Seat(player,control))==null;
    }
    public static void unbind(Player player)
    {
        SEATS.computeIfPresent(player.getObjectId(),(id,seat)->seat.player()==player?null:seat);
    }
    public static boolean isSeated(Creature actor)
    {
        if(!(actor instanceof Player player))return false;
        Seat seat=SEATS.get(player.getObjectId());return seat!=null && seat.player()==player;
    }
    public static boolean onMove(Player player,int x,int y,int z)
    {
        Seat seat=SEATS.get(player.getObjectId());if(seat==null || seat.player()!=player)return false;
        // Never let a malformed destination release a seated player into ordinary movement.
        if(Math.abs((long)x)<1_000_000 && Math.abs((long)y)<1_000_000 && Math.abs((long)z)<100_000)
            seat.control().accept(new Location(x,y,z));
        player.sendPacket(ActionFailed.STATIC_PACKET);return true;
    }
    public static boolean onValidate(Player player)
    {
        if(!isSeated(player))return false;
        player.sendPacket(new ValidateLocation(player));return true;
    }
}
