/*
 * This file is part of the L2J Mobius project.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
package custom.ElvenPvpRoom;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;

import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.data.xml.SkillData;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.instancezone.Instance;
import org.l2jmobius.gameserver.entity.instancezone.InstanceWorld;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import org.l2jmobius.gameserver.managers.InstanceManager;
import org.l2jmobius.gameserver.mechanics.skill.Skill;

/**
 * Persistent, shared PvP room using an isolated copy of Elven Village.
 * @author Codex
 */
public class ElvenPvpRoom implements IVoicedCommandHandler
{
	private static final int TEMPLATE_ID = 3051;
	private static final int FIRST_FIGHTER_ID = 901100;
	private static final int LAST_FIGHTER_ID = 901108;
	private static final int NOBLESSE_BLESSING_ID = 1323;
	private static final int ARENA_BUFF_DURATION = 7200;
	private static final int ENTRY_X = 45150;
	private static final int ENTRY_Y = 52100;
	private static final int ENTRY_Z = -2792;
	private static final int EXIT_X = 46890;
	private static final int EXIT_Y = 51531;
	private static final int EXIT_Z = -2976;
	private static final Object ROOM_LOCK = new Object();
	private final Set<Integer> _deadPlayers = new HashSet<>();
	private static final String[] COMMANDS =
	{
		"elvenpvp"
	};

	private ElvenPvpRoom()
	{
		VoicedCommandHandler.getInstance().registerHandler(this);
		ThreadPool.scheduleAtFixedRate(this::tickArena, 250, 1000);
	}

	@Override
	public boolean onCommand(String command, Player player, String params)
	{
		final String action = normalize(params);
		switch (action)
		{
			case "":
			case "join":
			case "entrar":
			{
				enterRoom(player);
				break;
			}
			case "leave":
			case "salir":
			{
				leaveRoom(player);
				break;
			}
			case "status":
			case "estado":
			{
				showStatus(player);
				break;
			}
			case "reset":
			case "reiniciar":
			{
				resetRoom(player);
				break;
			}
			default:
			{
				showHelp(player);
				break;
			}
		}
		return true;
	}

	private static void enterRoom(Player player)
	{
		if (player.isDead())
		{
			player.sendMessage("No puedes entrar a la sala PvP mientras estas muerto.");
			return;
		}
		if (player.isInCombat())
		{
			player.sendMessage("Sal del combate antes de entrar a la sala PvP.");
			return;
		}

		final InstanceWorld room = getOrCreateRoom();
		if (room == null)
		{
			player.sendMessage("La sala Elven Village PvP aun no esta disponible. Revisa la plantilla 3051.");
			return;
		}
		if ((player.getInstanceId() > 0) && (player.getInstanceId() != room.getInstanceId()))
		{
			player.sendMessage("Primero debes salir de la instancia en la que te encuentras.");
			return;
		}
		if (player.getInstanceId() == room.getInstanceId())
		{
			player.sendMessage("Ya estas dentro de Elven Village PvP.");
			return;
		}

		room.addAllowed(player);
		player.teleToLocation(ENTRY_X, ENTRY_Y, ENTRY_Z, 49152, room.getInstanceId(), false);
		prepareArenaPlayer(player);
		player.sendMessage("Entraste a Elven Village PvP. Usa .elvenpvp salir para volver al pueblo normal.");
	}

	private static void leaveRoom(Player player)
	{
		final Instance room = findRoom();
		if ((room == null) || (player.getInstanceId() != room.getId()))
		{
			player.sendMessage("No estas dentro de Elven Village PvP.");
			return;
		}

		final InstanceWorld world = InstanceManager.getInstance().getWorld(room.getId());
		if (world != null)
		{
			world.removeAllowed(player);
		}
		player.teleToLocation(EXIT_X, EXIT_Y, EXIT_Z, 0, 0, false);
		player.sendMessage("Saliste de Elven Village PvP.");
	}

	private static void showStatus(Player player)
	{
		final Instance room = findRoom();
		if (room == null)
		{
			player.sendMessage("Elven Village PvP: sala aun no creada; 0 jugadores.");
			return;
		}

		final long alive = room.getNpcs().stream().filter(npc -> !npc.isDead()).count();
		player.sendMessage("Elven Village PvP: " + room.getPlayers().size() + " jugador(es), " + alive + "/9 combatientes activos, instancia " + room.getId() + ".");
	}

	private static void resetRoom(Player player)
	{
		if (!player.isGM())
		{
			player.sendMessage("Solo un GM puede reiniciar la sala PvP.");
			return;
		}

		synchronized (ROOM_LOCK)
		{
			final Instance room = findRoom();
			if (room != null)
			{
				InstanceManager.getInstance().destroyInstance(room.getId());
			}
		}
		player.sendMessage("Elven Village PvP fue reiniciada. Se creara de nuevo al proximo ingreso.");
	}

	/**
	 * Keeps the room alive even when no player is close enough to wake the normal
	 * aggressive AI. Fighters receive a valid arena target and run to engage it.
	 * It also detects player revival so every arena respawn starts fully restored
	 * and protected by a fresh Noblesse Blessing.
	 */
	private void tickArena()
	{
		final Instance room = findRoom();
		if (room == null)
		{
			_deadPlayers.clear();
			return;
		}

		final List<Npc> fighters = new ArrayList<>();
		for (Npc npc : room.getNpcs())
		{
			if (isArenaFighter(npc) && !npc.isAlikeDead())
			{
				fighters.add(npc);
			}
		}

		final List<Creature> combatants = new ArrayList<>(fighters);
		for (Integer objectId : room.getPlayers())
		{
			final Player player = World.getPlayer(objectId);
			if ((player == null) || (player.getInstanceId() != room.getId()))
			{
				_deadPlayers.remove(objectId);
				continue;
			}

			if (player.isDead())
			{
				_deadPlayers.add(objectId);
			}
			else
			{
				combatants.add(player);
				if (_deadPlayers.remove(objectId))
				{
					prepareArenaPlayer(player);
					player.sendMessage("Reapareciste con HP, MP y CP completos; tus buffs fueron conservados.");
				}
			}
		}

		if (combatants.size() < 2)
		{
			return;
		}

		for (Npc fighter : fighters)
		{
			final Creature currentTarget = fighter.getAI().getAttackTarget();
			if (isValidTarget(fighter, currentTarget, room.getId()))
			{
				continue;
			}

			final Creature target = pickTarget(fighter, combatants);
			if (target != null)
			{
				fighter.asAttackable().clearAggroList();
				fighter.asAttackable().addDamageHate(target, 0, 50000);
				fighter.setTarget(target);
				fighter.getAI().setIntentionAttack(target);
			}
		}
	}

	private static Creature pickTarget(Npc fighter, List<Creature> combatants)
	{
		final int start = ThreadLocalRandom.current().nextInt(combatants.size());
		for (int offset = 0; offset < combatants.size(); offset++)
		{
			final Creature target = combatants.get((start + offset) % combatants.size());
			if (target != fighter)
			{
				return target;
			}
		}
		return null;
	}

	private static boolean isValidTarget(Npc fighter, Creature target, int instanceId)
	{
		if ((target == null) || (target == fighter) || target.isAlikeDead() || (target.getInstanceId() != instanceId))
		{
			return false;
		}
		return target.isPlayer() || (target.isNpc() && isArenaFighter(target.asNpc()));
	}

	private static boolean isArenaFighter(Npc npc)
	{
		return (npc != null) && (npc.getId() >= FIRST_FIGHTER_ID) && (npc.getId() <= LAST_FIGHTER_ID);
	}

	private static void prepareArenaPlayer(Player player)
	{
		player.fullRestore();
		final Skill noblesse = SkillData.getInstance().getSkill(NOBLESSE_BLESSING_ID, 1);
		if (noblesse != null)
		{
			noblesse.applyEffects(player, player, true, ARENA_BUFF_DURATION);
		}
	}

	private static InstanceWorld getOrCreateRoom()
	{
		final InstanceManager manager = InstanceManager.getInstance();
		Instance room = findRoom();
		if (room != null)
		{
			InstanceWorld world = manager.getWorld(room.getId());
			if (world == null)
			{
				world = new InstanceWorld();
				world.setInstance(room);
				manager.addWorld(world);
			}
			return world;
		}

		synchronized (ROOM_LOCK)
		{
			room = findRoom();
			if (room == null)
			{
				if (manager.getInstanceTemplateFileName(TEMPLATE_ID) == null)
				{
					return null;
				}
				room = manager.createDynamicInstance(TEMPLATE_ID);
			}

			InstanceWorld world = manager.getWorld(room.getId());
			if (world == null)
			{
				world = new InstanceWorld();
				world.setInstance(room);
				manager.addWorld(world);
			}
			return world;
		}
	}

	private static Instance findRoom()
	{
		for (Instance instance : InstanceManager.getInstance().getInstances().values())
		{
			if ((instance != null) && (instance.getTemplateId() == TEMPLATE_ID))
			{
				return instance;
			}
		}
		return null;
	}

	private static String normalize(String params)
	{
		if (params == null)
		{
			return "";
		}
		final String value = params.trim();
		if (value.isEmpty())
		{
			return "";
		}
		return value.split("\\s+", 2)[0].toLowerCase(Locale.ROOT);
	}

	private static void showHelp(Player player)
	{
		player.sendMessage("Elven Village PvP: .elvenpvp entrar | salir | estado");
		if (player.isGM())
		{
			player.sendMessage("GM: .elvenpvp reiniciar");
		}
	}

	@Override
	public String[] getCommandList()
	{
		return COMMANDS;
	}

	public static void main(String[] args)
	{
		new ElvenPvpRoom();
	}
}
