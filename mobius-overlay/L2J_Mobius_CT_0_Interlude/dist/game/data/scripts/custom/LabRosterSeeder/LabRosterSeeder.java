/* Creates the persistent physical player anchors used by the telemetry lab. */
package custom.LabRosterSeeder;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.data.xml.SkillTreeData;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.entity.actor.templates.PlayerTemplate;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.skill.holders.SkillLearn;

/**
 * Creates real, playable level-one characters for the first telemetry phase.
 * Existing names are left untouched, making this safe to run on every startup.
 */
public class LabRosterSeeder extends Script
{
	private static final Logger LOGGER = Logger.getLogger(LabRosterSeeder.class.getName());
	private static final Anchor[] ANCHORS =
	{
		new Anchor("telemetryf", "Arden", 0, 0, 0, 0, false),
		new Anchor("telemetryf", "Eryndor", 18, 1, 1, 1, true),
		new Anchor("telemetryf", "Vaelkor", 31, 2, 2, 2, false),
		new Anchor("telemetryf", "Gorvak", 44, 0, 1, 3, false),
		new Anchor("telemetryf", "Brunna", 53, 1, 0, 1, true),
		new Anchor("telemetrym", "Selene", 10, 1, 2, 2, true),
		new Anchor("telemetrym", "Lethiel", 25, 0, 1, 4, false),
		new Anchor("telemetrym", "Myrentha", 38, 2, 0, 5, true),
		new Anchor("telemetrym", "Zhurak", 49, 1, 2, 1, false)
	};

	public LabRosterSeeder()
	{
		int created = 0;
		for (Anchor anchor : ANCHORS)
		{
			try
			{
				if (!characterExists(anchor.name) && createAnchor(anchor))
				{
					created++;
				}
			}
			catch (Exception e)
			{
				LOGGER.log(Level.WARNING, "No se pudo crear el ancla " + anchor.name + ".", e);
			}
		}
		LOGGER.info("Laboratorio L2: anclas fisicas disponibles=" + ANCHORS.length + ", creadas ahora=" + created + ".");
	}

	private static boolean characterExists(String name) throws Exception
	{
		try (Connection con = DatabaseFactory.getConnection();
			PreparedStatement ps = con.prepareStatement("SELECT charId FROM characters WHERE char_name=?"))
		{
			ps.setString(1, name);
			try (ResultSet rs = ps.executeQuery())
			{
				return rs.next();
			}
		}
	}

	private static boolean createAnchor(Anchor anchor)
	{
		final PlayerTemplate template = PlayerTemplateData.getInstance().getTemplate(anchor.classId);
		if (template == null)
		{
			throw new IllegalStateException("No existe la plantilla inicial " + anchor.classId);
		}
		final Player player = Player.create(template, anchor.account, anchor.name,
			new PlayerAppearance((byte) anchor.face, (byte) anchor.hairColor, (byte) anchor.hairStyle, anchor.female));
		if (player == null)
		{
			return false;
		}

		final Location creationPoint = template.getCreationPoint();
		player.setXYZInvisible(creationPoint.getX(), creationPoint.getY(), creationPoint.getZ());
		player.setTitle("Ancla Telemetrica");
		player.setCurrentHp(player.getMaxHp());
		player.setCurrentMp(player.getMaxMp());
		player.setCurrentCp(player.getMaxCp());
		for (SkillLearn skill : SkillTreeData.getInstance().getAvailableSkills(player, player.getPlayerClass(), false, true))
		{
			player.addSkill(SkillData.getInstance().getSkill(skill.getSkillId(), skill.getSkillLevel()), true);
		}
		player.storeMe();
		return true;
	}

	private static final class Anchor
	{
		private final String account;
		private final String name;
		private final int classId;
		private final int face;
		private final int hairColor;
		private final int hairStyle;
		private final boolean female;

		private Anchor(String account, String name, int classId, int face, int hairColor, int hairStyle, boolean female)
		{
			this.account = account;
			this.name = name;
			this.classId = classId;
			this.face = face;
			this.hairColor = hairColor;
			this.hairStyle = hairStyle;
			this.female = female;
		}
	}

	public static void main(String[] args)
	{
		new LabRosterSeeder();
	}
}
