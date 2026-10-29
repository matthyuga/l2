package handlers.chat.commands.voiced;

import java.util.List;
import java.util.Map;

import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.enums.player.MacroType;
import org.l2jmobius.gameserver.entity.actor.holders.player.Macro;
import org.l2jmobius.gameserver.entity.actor.holders.player.MacroCmd;
import org.l2jmobius.gameserver.geoengine.GeoEngine;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.mechanics.DirectThreat;

/** On-demand selection, without starting an attack or changing the action queue. */
public class ThreatCommand implements IVoicedCommandHandler
{
	@Override
	public boolean onCommand(String command, Player player, String params)
	{
		if ((params != null) && params.trim().equalsIgnoreCase("macro"))
		{
			createMacro(player);
			return true;
		}
		if (player.isAlikeDead() || player.isOutOfControl())
		{
			player.sendMessage("No puedes seleccionar una amenaza en tu estado actual.");
			return true;
		}
		final Creature target = DirectThreat.last(player);
		if (target == null)
		{
			player.sendMessage("No hay una amenaza directa reciente (ultimos 30 segundos).");
			return true;
		}
		if ((target == player) || target.isAlikeDead() || !target.isSpawned() || !target.isTargetable() ||
			(target.getInstanceId() != player.getInstanceId()) || !player.isInSurroundingRegion(target) ||
			!player.isInsideRadius3D(target, 2000) || !GeoEngine.getInstance().canSeeTarget(player, target) ||
			!target.isVisibleFor(player) || target.isInvisible())
		{
			player.sendMessage("La amenaza ya no es un objetivo visible y disponible.");
			return true;
		}
		if (player.isLockedTarget() && (player.getLockedTarget() != target))
		{
			player.sendMessage("No puedes cambiar de objetivo mientras esta bloqueado.");
			return true;
		}
		player.setTarget(target);
		return true;
	}

	private static void createMacro(Player player)
	{
		final Map<Integer, Macro> macros = player.getMacros().getAllMacroses();
		synchronized (macros)
		{
			for (Macro macro : macros.values())
			{
				if (macro.getCommands().stream().anyMatch(line -> (".amenaza".equalsIgnoreCase(line.getCmd().trim()) || "//amenaza".equalsIgnoreCase(line.getCmd().trim()))))
				{
					player.getMacros().sendUpdate();
					player.sendMessage("Ya tienes el macro de amenaza: " + macro.getName() + ". Abre Alt+R y arrastralo a la barra.");
					return;
				}
			}
			if (macros.size() >= 24)
			{
				player.sendMessage("Tienes 24 macros. Libera uno y repite .amenaza macro.");
				return;
			}
			String name = "Amenaza";
			for (int suffix = 2; containsName(macros, name); suffix++)
			{
				name = "Amenaza" + suffix;
			}
			player.registerMacro(new Macro(0, 0, name, "Selecciona al agresor directo", "AMNZ",
				List.of(new MacroCmd(0, MacroType.TEXT, 0, 0, player.isGM() ? "//amenaza" : ".amenaza"))));
			player.sendMessage("Macro Amenaza creado. Abre Alt+R y arrastralo a la barra.");
		}
	}

	private static boolean containsName(Map<Integer, Macro> macros, String name)
	{
		return macros.values().stream().anyMatch(macro -> macro.getName().equalsIgnoreCase(name));
	}

	@Override
	public String[] getCommandList()
	{
		return new String[] {"amenaza", "agresor"};
	}
}
