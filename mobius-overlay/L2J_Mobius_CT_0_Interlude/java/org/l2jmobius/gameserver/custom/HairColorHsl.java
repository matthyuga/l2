package org.l2jmobius.gameserver.custom;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Collections;
import java.util.Map;
import java.util.WeakHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.entity.actor.Player;

/** Separate custom RGB state; the existing haircolor column remains A-D. */
public final class HairColorHsl
{
    private static final Logger LOGGER = Logger.getLogger(HairColorHsl.class.getName());
    public static final String VARIABLE = "NEXUS_HAIR_RGB_V1";
    public static final int TAG = 0x40000000;
    private static final Map<Object, Integer> PENDING = Collections.synchronizedMap(new WeakHashMap<>());
    private HairColorHsl() { }
    public static boolean isCustom(int value) { return (value & 0xfc000000) == TAG; }
    public static int encode(int rgb, int legacy) { return TAG | ((legacy & 3) << 24) | (rgb & 0xffffff); }
    public static byte read(Object packet, int value)
    {
        PENDING.remove(packet);
        if (isCustom(value))
        {
            PENDING.put(packet, value & 0xffffff);
            return (byte) ((value >>> 24) & 3);
        }
        return (byte) ((value >= 0 && value <= 3) ? value : -1);
    }
    public static void finish(Object packet, Player player)
    {
        final Integer rgb = PENDING.remove(packet);
        if (player != null && rgb != null)
        {
            player.getVariables().set(VARIABLE, rgb);
            player.getVariables().saveNow();
        }
    }
    public static int wire(Player player, int legacy)
    {
        if (player == null) return legacy;
        final int rgb = player.getVariables().getInt(VARIABLE, -1);
        return rgb >= 0 && rgb <= 0xffffff ? encode(rgb, legacy) : legacy;
    }
    public static int selection(int charId, int legacy)
    {
        try (Connection con = DatabaseFactory.getConnection();
             PreparedStatement st = con.prepareStatement("SELECT val FROM character_variables WHERE charId=? AND var=?"))
        {
            st.setInt(1, charId);
            st.setString(2, VARIABLE);
            try (ResultSet rs = st.executeQuery())
            {
                if (rs.next())
                {
                    final int rgb = Integer.parseInt(rs.getString(1));
                    if (rgb >= 0 && rgb <= 0xffffff) return encode(rgb, legacy);
                }
            }
        }
        catch (Exception e) { LOGGER.log(Level.WARNING, "Cannot read custom hair color for " + charId + "; using classic color", e); }
        return legacy;
    }
}
