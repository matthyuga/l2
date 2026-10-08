package custom.RealHumanPilots;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.ExperienceData;
import org.l2jmobius.gameserver.data.xml.HennaData;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.enums.creature.Race;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import custom.LabTelemetry.LabTelemetry;

/** Persistent, real Player pilots of explicit races. This is not a combat AI. */
public class RealHumanPilots extends Script
{
    private static final Logger LOGGER = Logger.getLogger(RealHumanPilots.class.getName());
    private static final String VERSION = "human-pilots-v1-main-only";
    private static final int[][] COMMON_BUFFS = {{1204,2},{1040,3},{1036,2},{1045,6},{1048,6},{1035,4},{1062,2}};
    private static final int[][] ARCHER_BUFFS = {{1068,3},{1086,2},{1240,3},{1242,3},{1077,3},{1087,3},{1357,1},
        {271,1},{272,1},{274,1},{275,1},{269,1},{266,1},{264,1},{267,1},{268,1},{304,1}};
    private static final int[][] MAGE_BUFFS = {{1085,3},{1059,3},{1078,6},{1303,2},{1355,1},
        {273,1},{276,1},{365,1},{264,1},{267,1},{268,1},{304,1},{349,1}};

    private RealHumanPilots()
    {
        ThreadPool.schedule(this::prepare, 15000);
    }

    private void prepare()
    {
        try
        {
            try (Connection con = DatabaseFactory.getConnection(); Statement st = con.createStatement())
            {
                st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_real_human_pilots (char_id INT UNSIGNED NOT NULL PRIMARY KEY, char_name VARCHAR(35) NOT NULL UNIQUE, recipe_version VARCHAR(40) NOT NULL, prepared_ms BIGINT UNSIGNED NOT NULL, verified_ms BIGINT UNSIGNED NOT NULL DEFAULT 0, role_name VARCHAR(20) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
            }
            prepareOne("Caelan", "telemetryf", false, 92, Race.HUMAN, "ARCHER", 343,
                new int[]{6379,6380,6381,6382,858,858,889,889,920,7577}, new int[]{169,174}, ARCHER_BUFFS);
            prepareOne("Ignara", "telemetrym", true, 94, Race.HUMAN, "FIRE_MAGE", 1230,
                new int[]{6383,6384,6385,6386,858,858,889,889,920,6608,6377}, new int[]{175,180}, MAGE_BUFFS);
            prepareOne("Korvash", "telemetrym", false, 115, Race.ORC, "DOMINATOR", 1245,
                new int[]{6383,6384,6385,6386,858,858,889,889,920,6608,6377}, new int[]{180}, MAGE_BUFFS);
            prepareOne("Aelira", "telemetrym", true, 103, Race.ELF, "MYSTIC_MUSE", 1235,
                new int[]{6383,6384,6385,6386,858,858,889,889,920,6608,6377}, new int[]{175,180}, MAGE_BUFFS);
            prepareOne("Morvain", "telemetryf", false, 95, Race.HUMAN, "SOULTAKER", 1234,
                new int[]{6383,6384,6385,6386,858,858,889,889,920,6608,6377}, new int[]{175,180}, MAGE_BUFFS);
            // Existing telemetry accounts already have seven characters each.
            prepareOne("Velith", "telemetryx", true, 110, Race.DARK_ELF, "STORM_DARK_ELF", 1239,
                new int[]{6383,6384,6385,6386,858,858,889,889,920,6608,6377}, new int[]{175,180}, MAGE_BUFFS);
            prepareOne("Sylira", "telemetryx", true, 110, Race.ELF, "STORM_ELF", 1239,
                new int[]{6383,6384,6385,6386,858,858,889,889,920,6608,6377}, new int[]{175,180}, MAGE_BUFFS);
        }
        catch (Exception e)
        {
            LOGGER.log(Level.SEVERE, "Pilotos humanos reales: preparacion incompleta; no se tocaron los nueve NPC.", e);
        }
    }

    private void prepareOne(String name, String account, boolean female, int mainClass, Race race, String role, int primarySkill, int[] gear, int[] dyes, int[][] buffs) throws Exception
    {
        int id = 0;
        boolean prepared = false;
        try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(
            "SELECT c.charId,c.account_name,c.online,p.recipe_version FROM characters c LEFT JOIN lab_real_human_pilots p ON p.char_id=c.charId WHERE c.char_name=?"))
        {
            ps.setString(1,name);
            try (ResultSet rs = ps.executeQuery())
            {
                if (rs.next())
                {
                    if (!account.equals(rs.getString("account_name"))) throw new IllegalStateException("Nombre ocupado: " + name);
                    id = rs.getInt("charId");
                    prepared = VERSION.equals(rs.getString("recipe_version"));
                    if (!prepared) throw new IllegalStateException("Existe un personaje sin receta verificada: " + name + "; no se sobrescribe.");
                    if ((rs.getInt("online") != 0) || (World.getPlayer(id) != null))
                    {
                        LOGGER.info("Piloto conectado; no se modifica: " + name);
                        return;
                    }
                }
            }
        }
        Player player = prepared ? Player.load(id) : Player.create(PlayerTemplateData.getInstance().getTemplate(mainClass),
            account, name, new PlayerAppearance((byte)0,(byte)0,(byte)0,female));
        if (player == null) throw new IllegalStateException("No se pudo cargar/crear " + name);
        // Player.load uses this lifecycle state too; no client is attached or marked online in SQL.
        player.setOnlineStatus(true,false);
        double[] expectedStats = null;
        int expectedSkills = 0;
        try
        {
            player.setDead(false);
            if (!prepared)
            {
                player.setRace(race);
                player.setTitle("Piloto real +4");
                maximize(player);
                for (int itemId : gear)
                {
                    Item item = player.getInventory().addItem(ItemProcessType.NONE,itemId,1,player,null);
                    if (item == null) throw new IllegalStateException("Objeto inexistente: " + itemId);
                    item.setEnchantLevel(4);
                    player.getInventory().equipItem(item);
                    item.updateDatabase(true);
                }
                for (int dyeId : dyes)
                {
                    if (!player.addHenna(HennaData.getInstance().getHenna(dyeId))) throw new IllegalStateException("No se pudo aplicar dye " + dyeId);
                }
                // Supplies do not grant stats. Reserved for manual tests / a later combat controller.
                supply(player,57,1000000);
                supply(player,5592,200);
                supply(player,mainClass == 92 ? 1467 : 3952,2000);
                if (mainClass == 92) supply(player,1345,2000);
                player.setXYZ(147450,female ? 46550 : 46350,-3400);
                player.storeMe();
            }
            validate(player,mainClass,race,primarySkill,gear,dyes);
            applyBuffs(player,buffs);
            player.setCurrentHpMp(player.getMaxHp(),player.getMaxMp());
            player.setCurrentCp(player.getMaxCp());
            player.storeMe();
            expectedStats = stats(player);
            expectedSkills = player.getAllSkills().size();
            if (!LabTelemetry.capturePilotStatsNow(player)) throw new IllegalStateException("No se pudieron capturar stats reales de " + name);
            if (!prepared)
            {
                try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(
                    "INSERT INTO lab_real_human_pilots (char_id,char_name,recipe_version,prepared_ms,role_name) VALUES (?,?,?,?,?)"))
                {
                    ps.setInt(1,player.getObjectId());ps.setString(2,name);ps.setString(3,VERSION);
                    ps.setLong(4,System.currentTimeMillis());ps.setString(5,role);ps.executeUpdate();
                }
            }
            LOGGER.info("Piloto real preparado: " + name + " " + race + " nivel " + player.getLevel() + " PAtk=" + player.getPAtk(null) + " MAtk=" + player.getMAtk(null,null));
        }
        finally
        {
            player.storeMe();
            player.deleteMe();
            player.setOnlineStatus(false,true);
        }
        // A fresh Player.load verifies persistence, equipment functions, main-only skills and racial stability.
        Player restored = Player.load(player.getObjectId());
        if (restored == null) throw new IllegalStateException("No se pudo verificar persistencia de " + name);
        try
        {
            validate(restored,mainClass,race,primarySkill,gear,dyes);
            applyBuffs(restored,buffs);
            restored.setCurrentHpMp(restored.getMaxHp(),restored.getMaxMp());
            restored.setCurrentCp(restored.getMaxCp());
            double[] reloadedStats = stats(restored);
            if (expectedSkills != restored.getAllSkills().size()) throw new IllegalStateException("Las skills cambiaron tras recarga de " + name);
            for (int i=0;i<expectedStats.length;i++)
                if (Math.abs(expectedStats[i]-reloadedStats[i]) > 0.00001)
                    throw new IllegalStateException("Los stats cambiaron tras recarga de " + name + " indice=" + i + ": " + expectedStats[i] + " != " + reloadedStats[i]);
            restored.storeMe();
            if (!LabTelemetry.capturePilotStatsNow(restored)) throw new IllegalStateException("Fallo captura tras recarga de " + name);
            try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(
                "UPDATE lab_real_human_pilots SET verified_ms=? WHERE char_id=?"))
            {
                ps.setLong(1,System.currentTimeMillis());ps.setInt(2,restored.getObjectId());ps.executeUpdate();
            }
            LOGGER.info("Piloto real verificado tras recarga: " + name + " skills=" + restored.getAllSkills().size() + " efectos=" + restored.getEffectList().getEffects().size());
        }
        finally
        {
            restored.storeMe();
            restored.deleteMe();
            restored.setOnlineStatus(false,true);
        }
    }

    private static void maximize(Player player)
    {
        int level = ExperienceData.getInstance().getMaxLevel() - 1;
        player.getStat().setExp(ExperienceData.getInstance().getExpForLevel(level));
        player.getStat().setLevel((byte)level);
        player.rewardSkills();
        player.storeMe();
    }

    private static double[] stats(Player player)
    {
        return new double[]{player.getPAtk(null),player.getMAtk(null,null),player.getPDef(null),player.getMDef(null,null),
            player.getPAtkSpd(),player.getMAtkSpd(),player.getMaxHp(),player.getMaxMp(),player.getMaxCp(),
            player.getSTR(),player.getDEX(),player.getCON(),player.getINT(),player.getWIT(),player.getMEN()};
    }

    private static void supply(Player player, int itemId, int count)
    {
        if (player.getInventory().addItem(ItemProcessType.NONE,itemId,count,player,null) == null)
            throw new IllegalStateException("Consumible inexistente: " + itemId);
    }

    private static void applyBuffs(Player player, int[][] buffs)
    {
        player.stopAllEffects();
        for (int[][] group : new int[][][]{COMMON_BUFFS,buffs})
        {
            for (int[] entry : group)
            {
                Skill skill = SkillData.getInstance().getSkill(entry[0],entry[1]);
                if (skill == null) throw new IllegalStateException("Buff inexistente: " + entry[0]);
                skill.applyEffects(player,player);
            }
        }
    }

    private static void validate(Player player, int mainClass, Race race, int primarySkill, int[] gear, int[] dyes)
    {
        if (player.getRace() != race || player.getClassIndex() != 0 || player.getPlayerClass().getId() != mainClass
            || player.getLevel() != ExperienceData.getInstance().getMaxLevel()-1) throw new IllegalStateException("Identidad/nivel incorrectos: " + player.getName());
        if (!player.getSubClasses().isEmpty()) throw new IllegalStateException("El piloto debe estar sin subclases: " + player.getName());
        for (int itemId : gear)
        {
            boolean found=false;
            for (Item item : player.getInventory().getItems())
                if (item.getId()==itemId && item.isEquipped() && item.getEnchantLevel()==4) found=true;
            if (!found) throw new IllegalStateException("Falta equipo real +4: " + itemId);
        }
        for (int dyeId : dyes)
        {
            boolean found=false;
            for (int slot=1;slot<=3;slot++) if (player.getHenna(slot)!=null && player.getHenna(slot).getDyeId()==dyeId) found=true;
            if (!found) throw new IllegalStateException("Falta dye real: " + dyeId);
        }
        if (player.getKnownSkill(primarySkill)==null) throw new IllegalStateException("Falta habilidad principal: " + player.getName());
    }

    public static void main(String[] args)
    {
        new RealHumanPilots();
    }
}
