/* Local solo laboratory: three cumulative subclasses; main class is immutable. */
package handlers.chat.commands.admin;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.util.StringTokenizer;

import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.gameserver.data.xml.ExperienceData;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import org.l2jmobius.gameserver.entity.actor.holders.player.SubClassHolder;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.handler.IAdminCommandHandler;
import org.l2jmobius.gameserver.network.serverpackets.NpcHtmlMessage;

public class AdminBuildLab implements IAdminCommandHandler
{
	private static final int ADENA = 57;
	private static final int ADENA_PACK = 1_000_000_000;
	private static final String[] ADMIN_COMMANDS =
	{
		"admin_buildlab", "admin_buildlab_main_roots", "admin_buildlab_main_set", "admin_buildlab_main_evolve",
		"admin_buildlab_main_reset", "admin_buildlab_reset_all", "admin_buildlab_choose", "admin_buildlab_set", "admin_buildlab_third",
		"admin_buildlab_switch", "admin_buildlab_clear", "admin_buildlab_clear_all",
		"admin_buildlab_stage", "admin_buildlab_adena"
	};

	@Override
	public boolean onCommand(String command, Player activeChar)
	{
		final Player player = getEditedPlayer(activeChar);
		try
		{
			final StringTokenizer tokens = new StringTokenizer(command);
			final String action = tokens.nextToken();
			if (action.equals("admin_buildlab_main_roots"))
			{
				showMainOriginChooser(activeChar, player);
			}
			else if (action.equals("admin_buildlab_main_set"))
			{
				setMainOrigin(activeChar, player, Integer.parseInt(tokens.nextToken()));
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_main_evolve"))
			{
				if (tokens.hasMoreTokens())
				{
					evolveMainClass(activeChar, player, Integer.parseInt(tokens.nextToken()));
					showMain(activeChar, player);
				}
				else
				{
					showMainEvolutionChooser(activeChar, player);
				}
			}
			else if (action.equals("admin_buildlab_main_reset"))
			{
				resetMainClass(activeChar, player);
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_reset_all"))
			{
				resetAllClasses(activeChar, player);
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_choose"))
			{
				final int slot = Integer.parseInt(tokens.nextToken());
				final int page = tokens.hasMoreTokens() ? Integer.parseInt(tokens.nextToken()) : 0;
				showSecondClassChooser(activeChar, player, slot, page);
			}
			else if (action.equals("admin_buildlab_set"))
			{
				setSecondClass(activeChar, player, Integer.parseInt(tokens.nextToken()), Integer.parseInt(tokens.nextToken()));
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_third"))
			{
				upgradeToThird(activeChar, player, Integer.parseInt(tokens.nextToken()));
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_switch"))
			{
				final int slot = Integer.parseInt(tokens.nextToken());
				if ((slot == 0) || player.getSubClasses().containsKey(slot))
				{
					player.setActiveClass(slot);
					heal(player);
				}
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_clear"))
			{
				final int slot = Integer.parseInt(tokens.nextToken());
				clearSubClass(player, slot);
				activeChar.sendSysMessage("Build Lab: Sub " + slot + " vaciada.");
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_clear_all"))
			{
				clearAllSubClasses(player);
				activeChar.sendSysMessage("Build Lab: las tres subclases fueron reiniciadas.");
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_stage"))
			{
				maximizeStage(player);
				player.sendSysMessage("Build Lab: nivel maximo y skills de la profesion activa.");
				showMain(activeChar, player);
			}
			else if (action.equals("admin_buildlab_adena"))
			{
				player.getInventory().addItem(ItemProcessType.REWARD, ADENA, ADENA_PACK, player, activeChar);
				player.sendSysMessage("Build Lab: recibiste 1.000.000.000 Adena para el GM Shop.");
				showMain(activeChar, player);
			}
			else
			{
				showMain(activeChar, player);
			}
		}
		catch (Exception e)
		{
			activeChar.sendSysMessage("Build Lab: " + e.getMessage());
			showMain(activeChar, player);
		}
		return true;
	}

	private static Player getEditedPlayer(Player activeChar)
	{
		final WorldObject target = activeChar.getTarget();
		return ((target != null) && target.isPlayer()) ? target.asPlayer() : activeChar;
	}

	private static void setMainOrigin(Player admin, Player player, int classId) throws Exception
	{
		final PlayerClass root = PlayerClass.getPlayerClass(classId);
		if ((root == null) || (root.getParent() != null))
		{
			throw new IllegalArgumentException("elige una raza y clase inicial validas");
		}
		replaceMainClass(player, root, true);
		admin.sendSysMessage("Build Lab: principal reiniciada como " + originName(root) + ".");
	}

	private static void evolveMainClass(Player admin, Player player, int classId) throws Exception
	{
		final PlayerClass current = PlayerClass.getPlayerClass(player.getBaseClass());
		final PlayerClass next = PlayerClass.getPlayerClass(classId);
		if ((current == null) || (next == null) || !current.getNextClasses().contains(next))
		{
			throw new IllegalArgumentException("esa profesion no es una evolucion directa de la principal");
		}
		replaceMainClass(player, next, false);
		admin.sendSysMessage("Build Lab: principal evolucionada a " + nameOf(next) + ".");
	}

	private static void resetMainClass(Player admin, Player player) throws Exception
	{
		final PlayerClass root = rootOf(PlayerClass.getPlayerClass(player.getBaseClass()));
		if (root == null)
		{
			throw new IllegalStateException("no se pudo determinar la raza de la principal");
		}
		replaceMainClass(player, root, true);
		admin.sendSysMessage("Build Lab: principal reiniciada a " + originName(root) + ".");
	}

	private static void resetAllClasses(Player admin, Player player) throws Exception
	{
		final PlayerClass root = rootOf(PlayerClass.getPlayerClass(player.getBaseClass()));
		if (root == null)
		{
			throw new IllegalStateException("no se pudo determinar la raza de la principal");
		}
		clearAllSubClasses(player);
		replaceMainClass(player, root, true);
		admin.sendSysMessage("Build Lab: principal y las tres Sub fueron reiniciadas.");
	}

	private static void replaceMainClass(Player player, PlayerClass playerClass, boolean clearSkills) throws Exception
	{
		player.setActiveClass(0);
		if (clearSkills)
		{
			deleteMainClassData(player);
		}
		player.setBaseClass(playerClass);
		player.setPlayerClass(playerClass.getId());
		player.setActiveClass(0);
		maximizeStage(player);
		player.storeMe();
		player.sendSkillList();
		player.broadcastUserInfo();
	}

	private static void deleteMainClassData(Player player) throws Exception
	{
		try (Connection con = DatabaseFactory.getConnection())
		{
			deleteSubClassRows(con, "character_hennas", player.getObjectId(), 0);
			deleteSubClassRows(con, "character_shortcuts", player.getObjectId(), 0);
			deleteSubClassRows(con, "character_skills_save", player.getObjectId(), 0);
			deleteSubClassRows(con, "character_skills", player.getObjectId(), 0);
		}
	}

	private static void setSecondClass(Player admin, Player player, int slot, int classId) throws Exception
	{
		validateSubSlot(slot);
		final PlayerClass playerClass = PlayerClass.getPlayerClass(classId);
		if ((playerClass == null) || (playerClass.level() != 2))
		{
			throw new IllegalArgumentException("elige una profesion de segunda clase");
		}
		if (isBranchUsedInOtherSlot(player, slot, playerClass))
		{
			throw new IllegalArgumentException("esa rama ya esta usada por otra Sub");
		}
		replaceSubClass(player, slot, playerClass);
		admin.sendSysMessage("Build Lab: Sub " + slot + " configurada como " + nameOf(playerClass) + ".");
	}

	private static void upgradeToThird(Player admin, Player player, int slot) throws Exception
	{
		validateSubSlot(slot);
		final SubClassHolder sub = player.getSubClasses().get(slot);
		if (sub == null)
		{
			throw new IllegalStateException("la ranura esta vacia");
		}
		final PlayerClass current = PlayerClass.getPlayerClass(sub.getId());
		if ((current == null) || (current.level() != 2))
		{
			throw new IllegalStateException("esta Sub no esta en una segunda profesion valida");
		}
		PlayerClass third = null;
		for (PlayerClass next : current.getNextClasses())
		{
			if (next.level() == 3)
			{
				third = next;
				break;
			}
		}
		if (third == null)
		{
			throw new IllegalStateException(nameOf(current) + " no tiene tercera profesion");
		}
		replaceSubClass(player, slot, third);
		admin.sendSysMessage("Build Lab: Sub " + slot + " evoluciono a " + nameOf(third) + ".");
	}

	private static void replaceSubClass(Player player, int slot, PlayerClass playerClass) throws Exception
	{
		if (player.getClassIndex() != 0)
		{
			player.setActiveClass(0);
		}
		final boolean changed = player.getSubClasses().containsKey(slot) ? player.modifySubClass(slot, playerClass.getId()) : player.addSubClass(playerClass.getId(), slot);
		if (!changed)
		{
			throw new IllegalStateException("no se pudo guardar la Sub " + slot + "; revisa que la clase no este repetida");
		}
		player.setActiveClass(slot);
		maximizeStage(player);
		player.storeMe();
		player.sendSkillList();
		player.broadcastUserInfo();
	}

	private static void clearSubClass(Player player, int slot) throws Exception
	{
		validateSubSlot(slot);
		if (!player.getSubClasses().containsKey(slot))
		{
			return;
		}
		player.setActiveClass(0);
		deleteSubClassData(player, slot);
		player.getSubClasses().remove(slot);
		refreshMainClass(player);
	}

	private static void clearAllSubClasses(Player player) throws Exception
	{
		player.setActiveClass(0);
		try (Connection con = DatabaseFactory.getConnection())
		{
			deleteAllSubClassRows(con, "character_hennas", player.getObjectId());
			deleteAllSubClassRows(con, "character_shortcuts", player.getObjectId());
			deleteAllSubClassRows(con, "character_skills_save", player.getObjectId());
			deleteAllSubClassRows(con, "character_skills", player.getObjectId());
			deleteAllSubClassRows(con, "character_subclasses", player.getObjectId());
		}
		player.getSubClasses().clear();
		refreshMainClass(player);
	}

	private static void deleteSubClassData(Player player, int slot) throws Exception
	{
		try (Connection con = DatabaseFactory.getConnection())
		{
			deleteSubClassRows(con, "character_hennas", player.getObjectId(), slot);
			deleteSubClassRows(con, "character_shortcuts", player.getObjectId(), slot);
			deleteSubClassRows(con, "character_skills_save", player.getObjectId(), slot);
			deleteSubClassRows(con, "character_skills", player.getObjectId(), slot);
			deleteSubClassRows(con, "character_subclasses", player.getObjectId(), slot);
		}
	}

	private static void deleteSubClassRows(Connection con, String table, int objectId, int slot) throws Exception
	{
		try (PreparedStatement ps = con.prepareStatement("DELETE FROM " + table + " WHERE charId=? AND class_index=?"))
		{
			ps.setInt(1, objectId);
			ps.setInt(2, slot);
			ps.executeUpdate();
		}
	}

	private static void deleteAllSubClassRows(Connection con, String table, int objectId) throws Exception
	{
		try (PreparedStatement ps = con.prepareStatement("DELETE FROM " + table + " WHERE charId=? AND class_index>0"))
		{
			ps.setInt(1, objectId);
			ps.executeUpdate();
		}
	}

	private static void refreshMainClass(Player player)
	{
		player.setActiveClass(0);
		player.storeMe();
		player.sendSkillList();
		player.broadcastUserInfo();
		heal(player);
	}

	private static void validateSubSlot(int slot)
	{
		if ((slot < 1) || (slot > 3))
		{
			throw new IllegalArgumentException("solo se pueden editar Sub 1, Sub 2 y Sub 3");
		}
	}

	private static boolean isBranchUsedInOtherSlot(Player player, int editedSlot, PlayerClass candidate)
	{
		final PlayerClass candidateSecond = secondOf(candidate);
		for (int slot = 1; slot <= 3; slot++)
		{
			if (slot == editedSlot)
			{
				continue;
			}
			final SubClassHolder sub = player.getSubClasses().get(slot);
			if ((sub != null) && (secondOf(PlayerClass.getPlayerClass(sub.getId())) == candidateSecond))
			{
				return true;
			}
		}
		return false;
	}

	private static PlayerClass secondOf(PlayerClass playerClass)
	{
		while ((playerClass != null) && (playerClass.level() > 2))
		{
			playerClass = playerClass.getParent();
		}
		return ((playerClass != null) && (playerClass.level() == 2)) ? playerClass : null;
	}

	private static PlayerClass rootOf(PlayerClass playerClass)
	{
		while ((playerClass != null) && (playerClass.getParent() != null))
		{
			playerClass = playerClass.getParent();
		}
		return playerClass;
	}

	private static void maximizeStage(Player player)
	{
		final int stage = player.getPlayerClass().level();
		final int targetLevel;
		switch (stage)
		{
			case 0:
				targetLevel = 20;
				break;
			case 1:
				targetLevel = 40;
				break;
			case 2:
				targetLevel = 76;
				break;
			default:
				targetLevel = 80;
		}
		final long targetExp = ExperienceData.getInstance().getExpForLevel(targetLevel);
		final long currentExp = player.getExp();
		if (currentExp < targetExp)
		{
			player.addExpAndSp(targetExp - currentExp, 0);
		}
		else if (currentExp > targetExp)
		{
			player.getStat().setLevel((byte) targetLevel);
			player.removeExpAndSp(currentExp - targetExp, 0);
		}
		player.rewardSkills();
		heal(player);
		player.sendSkillList();
		player.broadcastUserInfo();
	}

	private static void heal(Player player)
	{
		player.setCurrentHpMp(player.getMaxHp(), player.getMaxMp());
		player.setCurrentCp(player.getMaxCp());
	}

	private static void showMain(Player admin, Player player)
	{
		final StringBuilder html = new StringBuilder(6000);
		html.append("<html><body><center><font color=LEVEL>Build Lab - 4 clases acumulativas</font><br>");
		html.append("Editando: <font color=FFFFFF>").append(player.getName()).append("</font><br>");
		html.append("Solo la principal define raza y apariencia. Las Sub son profesiones.<br><br>");
		addMainSection(html, player);
		for (int slot = 1; slot <= 3; slot++)
		{
			addSubSection(html, player, slot);
		}
		html.append("Activa: <font color=FFFFFF>").append(pathOf(player.getPlayerClass())).append("</font><br>");
		html.append(button("Nivel maximo + skills", "admin_buildlab_stage", 250)).append("<br>");
		html.append(button("Recibir 1.000M Adena", "admin_buildlab_adena", 250)).append("<br>");
		html.append(button("VACIAR LAS 3 SUB", "admin_buildlab_clear_all", 250)).append("<br>");
		html.append(button("REINICIAR TODAS LAS CLASES", "admin_buildlab_reset_all", 250)).append("<br>");
		html.append("<font color=AAAAAA>Principal: 20 / 40 / 76 / 80. Sub: 2da 76, 3ra 80.</font><br>");
		html.append("<font color=AAAAAA>Los skills de las cuatro clases se acumulan.</font>");
		html.append("</center></body></html>");
		sendHtml(admin, html.toString());
	}

	private static void addMainSection(StringBuilder html, Player player)
	{
		final PlayerClass main = PlayerClass.getPlayerClass(player.getBaseClass());
		html.append("<table width=280 bgcolor=111111><tr><td width=280>");
		html.append(player.getClassIndex() == 0 ? "<font color=00FF00>PRINCIPAL</font>" : "<font color=LEVEL>PRINCIPAL</font>");
		html.append("</td></tr><tr><td><font color=FFFFFF>Raza: ").append(raceName(main)).append("</font></td></tr>");
		html.append("<tr><td><font color=FFFFFF>Clase: ").append(nameOf(main)).append("</font></td></tr>");
		html.append("<tr><td><font color=AAAAAA>").append(pathOf(main)).append("</font></td></tr>");
		html.append("<tr><td>");
		if ((main != null) && !main.getNextClasses().isEmpty())
		{
			html.append(button("Evolucionar", "admin_buildlab_main_evolve", 105));
		}
		html.append(button("Cambiar raza", "admin_buildlab_main_roots", 120));
		html.append("</td></tr><tr><td>");
		html.append(button("Reiniciar", "admin_buildlab_main_reset", 95));
		html.append(button("Usar", "admin_buildlab_switch 0", 75)).append("</td></tr></table><br>");
	}

	private static void addSubSection(StringBuilder html, Player player, int slot)
	{
		final SubClassHolder sub = player.getSubClasses().get(slot);
		final PlayerClass playerClass = sub == null ? null : PlayerClass.getPlayerClass(sub.getId());
		html.append("<table width=280 bgcolor=222222><tr><td width=280>");
		html.append(player.getClassIndex() == slot ? "<font color=00FF00>Sub " + slot + " ACTIVA</font>" : "<font color=LEVEL>Sub " + slot + "</font>");
		html.append("</td></tr><tr><td>");
		if (playerClass == null)
		{
			html.append("<font color=AAAAAA>Ranura vacia</font></td></tr><tr><td>")
				.append(button("Elegir 2da profesion", "admin_buildlab_choose " + slot, 180)).append("</td></tr>");
		}
		else
		{
			final PlayerClass second = secondOf(playerClass);
			html.append("<font color=FFFFFF>").append(nameOf(playerClass)).append("</font> - ")
				.append(second == null ? "<font color=FF7777>ruta incompleta</font>" : stageName(playerClass.level())).append("</td></tr>");
			html.append("<tr><td><font color=AAAAAA>Profesion: ").append(subPathOf(playerClass)).append("</font></td></tr>");
			html.append("<tr><td>").append(button("Cambiar", "admin_buildlab_choose " + slot, 95));
			if ((playerClass.level() == 2) && hasThirdClass(playerClass))
			{
				html.append(button("Subir a 3ra", "admin_buildlab_third " + slot, 105));
			}
			html.append("</td></tr><tr><td>");
			html.append(button("Usar", "admin_buildlab_switch " + slot, 75));
			html.append(button("Vaciar", "admin_buildlab_clear " + slot, 80)).append("</td></tr>");
		}
		html.append("</table><br>");
	}

	private static void showMainOriginChooser(Player admin, Player player)
	{
		final StringBuilder html = new StringBuilder(3500);
		html.append("<html><body><center><font color=LEVEL>Principal: elegir raza y clase inicial</font><br>");
		html.append("La raza y apariencia pertenecen unicamente a la principal.<br>");
		html.append("Cambiarla reinicia los skills de la principal; las Sub se conservan.<br><br><table width=280>");
		for (PlayerClass playerClass : PlayerClass.values())
		{
			if (playerClass.getParent() != null)
			{
				continue;
			}
			html.append("<tr><td width=280>").append(button(originName(playerClass), "admin_buildlab_main_set " + playerClass.getId(), 260)).append("</td></tr>");
		}
		html.append("</table><br>").append(button("Volver", "admin_buildlab", 100));
		html.append("</center></body></html>");
		sendHtml(admin, html.toString());
	}

	private static void showMainEvolutionChooser(Player admin, Player player)
	{
		final PlayerClass current = PlayerClass.getPlayerClass(player.getBaseClass());
		final StringBuilder html = new StringBuilder(2500);
		html.append("<html><body><center><font color=LEVEL>Principal: evolucion de clase</font><br>");
		html.append("Raza: <font color=FFFFFF>").append(raceName(current)).append("</font><br>");
		html.append("Ruta actual: <font color=FFFFFF>").append(pathOf(current)).append("</font><br><br>");
		if ((current == null) || current.getNextClasses().isEmpty())
		{
			html.append("La principal ya alcanzo su profesion final.<br>");
		}
		else
		{
			html.append("Elige la siguiente profesion directa:<br><br>");
			for (PlayerClass next : current.getNextClasses())
			{
				html.append(button(nameOf(next), "admin_buildlab_main_evolve " + next.getId(), 220));
				html.append("<font color=AAAAAA>").append(pathOf(next)).append("</font><br>");
			}
		}
		html.append("<br>").append(button("Cambiar raza", "admin_buildlab_main_roots", 120));
		html.append(button("Volver", "admin_buildlab", 100));
		html.append("</center></body></html>");
		sendHtml(admin, html.toString());
	}

	private static void showSecondClassChooser(Player admin, Player player, int slot, int page)
	{
		validateSubSlot(slot);
		final int pageSize = 8;
		int total = 0;
		for (PlayerClass playerClass : PlayerClass.values())
		{
			if (playerClass.level() == 2)
			{
				total++;
			}
		}
		final int pageCount = Math.max(1, (total + pageSize - 1) / pageSize);
		page = Math.max(0, Math.min(pageCount - 1, page));
		final StringBuilder html = new StringBuilder(5000);
		html.append("<html><body><center><font color=LEVEL>Sub ").append(slot).append(": elegir profesion</font><br>");
		html.append("Las Sub no tienen raza propia: solo guardan una profesion.<br>");
		html.append("Pagina ").append(page + 1).append(" de ").append(pageCount).append(" - elige una profesion de 2da.<br><br>");
		html.append("<table width=280>");
		int classIndex = 0;
		for (PlayerClass playerClass : PlayerClass.values())
		{
			if (playerClass.level() != 2)
			{
				continue;
			}
			if ((classIndex < (page * pageSize)) || (classIndex >= ((page + 1) * pageSize)))
			{
				classIndex++;
				continue;
			}
			final boolean used = isBranchUsedInOtherSlot(player, slot, playerClass);
			html.append("<tr><td width=280>");
			if (used)
			{
				html.append("<font color=777777>").append(nameOf(playerClass)).append(" (usada)</font>");
			}
			else
			{
				html.append(button(nameOf(playerClass), "admin_buildlab_set " + slot + " " + playerClass.getId(), 260));
			}
			html.append("</td></tr>");
			classIndex++;
		}
		html.append("</table><br>");
		if (page > 0)
		{
			html.append(button("Pagina anterior", "admin_buildlab_choose " + slot + " " + (page - 1), 130));
		}
		if (page < (pageCount - 1))
		{
			html.append(button("Pagina siguiente", "admin_buildlab_choose " + slot + " " + (page + 1), 130));
		}
		html.append("<br>").append(button("Volver", "admin_buildlab", 100));
		html.append("</center></body></html>");
		sendHtml(admin, html.toString());
	}

	private static boolean hasThirdClass(PlayerClass playerClass)
	{
		for (PlayerClass next : playerClass.getNextClasses())
		{
			if (next.level() == 3)
			{
				return true;
			}
		}
		return false;
	}

	private static String subPathOf(PlayerClass playerClass)
	{
		final PlayerClass second = secondOf(playerClass);
		if (second == null)
		{
			return nameOf(playerClass);
		}
		return (playerClass.level() >= 3) ? nameOf(second) + " &gt; " + nameOf(playerClass) : nameOf(second);
	}

	private static String raceName(PlayerClass playerClass)
	{
		if (playerClass == null)
		{
			return "desconocida";
		}
		return prettyName(playerClass.getRace().name());
	}

	private static String originName(PlayerClass playerClass)
	{
		return raceName(playerClass) + " - " + (playerClass.isMage() ? "Mage" : "Fighter");
	}

	private static String pathOf(PlayerClass playerClass)
	{
		if (playerClass == null)
		{
			return "desconocida";
		}
		return playerClass.getParent() == null ? nameOf(playerClass) : pathOf(playerClass.getParent()) + " &gt; " + nameOf(playerClass);
	}

	private static String stageName(int stage)
	{
		return stage >= 3 ? "<font color=FFCC66>3ra profesion</font>" : "<font color=99CCFF>2da profesion</font>";
	}

	private static String button(String value, String action, int width)
	{
		return "<button value=\"" + value + "\" action=\"bypass -h " + action + "\" width=" + width + " height=21 back=\"L2UI_ch3.bigbutton2_down\" fore=\"L2UI_ch3.bigbutton2\">";
	}

	private static String nameOf(PlayerClass playerClass)
	{
		if (playerClass == null)
		{
			return "desconocida";
		}
		return prettyName(playerClass.name());
	}

	private static String prettyName(String rawName)
	{
		final String[] words = rawName.toLowerCase().split("_");
		final StringBuilder name = new StringBuilder();
		for (String word : words)
		{
			if (name.length() > 0)
			{
				name.append(' ');
			}
			name.append(Character.toUpperCase(word.charAt(0))).append(word.substring(1));
		}
		return name.toString();
	}

	private static void sendHtml(Player player, String text)
	{
		final NpcHtmlMessage html = new NpcHtmlMessage();
		html.setHtml(text);
		player.sendPacket(html);
	}

	@Override
	public String[] getCommandList()
	{
		return ADMIN_COMMANDS;
	}
}
