package custom.RacialProfileVerification;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Arrays;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Race;
import org.l2jmobius.gameserver.mechanics.script.Script;

/** Isolated real-player persistence test; never modifies a user's character. */
public class RacialProfileVerification extends Script
{
    private static final Logger LOGGER = Logger.getLogger(RacialProfileVerification.class.getName());
    private RacialProfileVerification() { ThreadPool.schedule(this::verify, 45000); }
    private static int[] attributes(Player p) { return new int[]{p.getSTR(),p.getDEX(),p.getCON(),p.getINT(),p.getWIT(),p.getMEN()}; }
    private static void check(Player p, Race race, boolean mage, int[] expected, String step)
    {
        if (p.getRace()!=race || p.isRacialMage()!=mage || !Arrays.equals(attributes(p),expected))
            throw new IllegalStateException(step+": race="+p.getRace()+" mage="+p.isRacialMage()+" observed="+Arrays.toString(attributes(p))+" expected="+Arrays.toString(expected));
        LOGGER.info("RacialProfile PASS " + step + " class=" + p.getPlayerClass().getId() + " attrs=" + Arrays.toString(attributes(p)));
    }
    private void verify()
    {
        Player p = null;
        try
        {
            int id=0;
            try(Connection con=DatabaseFactory.getConnection(); PreparedStatement ps=con.prepareStatement("SELECT charId,account_name,online FROM characters WHERE char_name='RacialProbe'"))
            {
                try(ResultSet rs=ps.executeQuery())
                {
                    if(rs.next())
                    {
                        if(!"racialtest".equals(rs.getString("account_name")) || rs.getInt("online")!=0 || World.getPlayer(rs.getInt("charId"))!=null)
                            throw new IllegalStateException("Probe name occupied or online; no modification permitted");
                        id=rs.getInt("charId");
                    }
                }
            }
            p=id==0 ? Player.create(PlayerTemplateData.getInstance().getTemplate(0),"racialtest","RacialProbe",new PlayerAppearance((byte)0,(byte)0,(byte)0,false)) : Player.load(id);
            if(p==null) throw new IllegalStateException("Probe load/create failed");
            p.setOnlineStatus(true,false);
            p.setRacialOrigin(Race.HUMAN,false);
            p.setActiveClass(0);
            p.setBaseClass(0);p.setPlayerClass(0);
            int[] human=attributes(p);
            check(p,Race.HUMAN,false,new int[]{40,30,43,21,11,25},"human fighter origin");
            p.setPlayerClass(92);p.setBaseClass(92);
            check(p,Race.HUMAN,false,human,"main Sagittarius evolution");
            if(!p.getSubClasses().containsKey(1) && !p.addSubClass(48,1)) throw new IllegalStateException("Tyrant subclass failed");
            if(!p.getSubClasses().containsKey(2) && !p.addSubClass(27,2)) throw new IllegalStateException("Spellsinger subclass failed");
            p.setActiveClass(1);
            check(p,Race.HUMAN,false,human,"Tyrant second profession");
            p.setActiveClass(2);
            check(p,Race.HUMAN,false,human,"Spellsinger second profession");
            p.storeMe();id=p.getObjectId();p.deleteMe();p.setOnlineStatus(false,true);p=null;
            p=Player.load(id);
            check(p,Race.HUMAN,false,human,"reload with mage subclass active");
            p.setOnlineStatus(true,false);
            final int main=p.getBaseClass(),active=p.getPlayerClass().getId(),subs=p.getTotalSubClasses();
            p.setRace(Race.ORC);
            check(p,Race.ORC,false,new int[]{40,26,47,18,12,27},"explicit race change to orc");
            if(p.getBaseClass()!=main || p.getPlayerClass().getId()!=active || p.getTotalSubClasses()!=subs) throw new IllegalStateException("Race change altered build");
            p.storeMe();p.deleteMe();p.setOnlineStatus(false,true);p=null;
            p=Player.load(id);
            check(p,Race.ORC,false,new int[]{40,26,47,18,12,27},"reload explicit race change");
            p.setOnlineStatus(true,false);p.setRace(Race.HUMAN);p.setActiveClass(0);
            check(p,Race.HUMAN,false,human,"restore original race and main");
            p.setTitle("Prueba racial OK");
            p.setXYZ(147450,46350,-3400);
            LOGGER.info("RacialProfileVerification SUCCESS: 8 real Player checks, main third + second-profession subs, persisted independently of active class.");
        }
        catch(Exception e) { LOGGER.log(Level.SEVERE,"RacialProfileVerification FAILED",e); }
        finally
        {
            if(p!=null) { p.storeMe();p.deleteMe();p.setOnlineStatus(false,true); }
        }
    }
    public static void main(String[] args) { new RacialProfileVerification(); }
}
