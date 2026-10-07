/*
 * This file is part of the L2J Mobius project.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
package handlers.chat.commands.voiced;

import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;

/**
 * GM-only tactical controls for the Solo Arena fake players.
 * @author Codex
 */
public class SquadCommand implements IVoicedCommandHandler
{
	private static final int ARES_ID = 900200;
	private static final int NYX_ID = 900201;
	private static final int ARRIVAL_DISTANCE = 70;
	private static final int FORMATION_DISTANCE = 65;

	private static final String[] VOICED_COMMANDS =
	{
		"ares",
		"nyx",
		"squad"
	};

	private static final Map<Integer, ControlState> STATES = new ConcurrentHashMap<>();

	static
	{
		ThreadPool.scheduleAtFixedRate(SquadCommand::updateOrders, 1000, 750);
	}

	@Override
	public boolean onCommand(String command, Player player, String params)
	{
		if (!player.isGM())
		{
			player.sendMessage("Solo un GM puede controlar el peloton de la arena.");
			return true;
		}

		final String action = normalizeAction(params);
		if (action.isEmpty() || action.equals("help"))
		{
			showHelp(player, command);
			return true;
		}

		final int[] npcIds = getNpcIds(command);
		if (action.equals("status"))
		{
			showStatus(player, npcIds);
			return true;
		}

		final WorldObject selectedTarget = player.getTarget();
		if (action.equals("attack") && !isValidTarget(player, selectedTarget))
		{
			player.sendMessage("Selecciona primero un personaje o criatura viva y vuelve a ejecutar el macro.");
			return true;
		}

		int ordered = 0;
		for (int index = 0; index < npcIds.length; index++)
		{
			final int npcId = npcIds[index];
			final Npc npc = World.getNpc(npcId);
			if ((npc == null) || npc.isDead())
			{
				player.sendMessage(getNpcName(npcId) + " no esta disponible (muerto o sin aparecer).");
				continue;
			}
			if (npc.getInstanceId() != player.getInstanceId())
			{
				player.sendMessage(getNpcName(npcId) + " esta en otra instancia.");
				continue;
			}
			if (action.equals("attack") && (selectedTarget == npc))
			{
				player.sendMessage(getNpcName(npcId) + " no puede atacarse a si mismo.");
				continue;
			}

			final ControlState state = STATES.computeIfAbsent(npcId, key -> new ControlState());
			state.controllerObjectId = player.getObjectId();
			final int formationOffset = (npcIds.length > 1) ? ((index == 0) ? -FORMATION_DISTANCE : FORMATION_DISTANCE) : 0;
			switch (action)
			{
				case "attack":
				{
					state.targetObjectId = selectedTarget.getObjectId();
					state.order = Order.ATTACK;
					applyAttack(npc, selectedTarget);
					break;
				}
				case "move":
				{
					state.destination = locationAtPlayer(player, formationOffset);
					state.order = Order.MOVE;
					applyMove(npc, state.destination);
					break;
				}
				case "follow":
				{
					state.order = Order.FOLLOW;
					applyFollow(npc, player);
					break;
				}
				case "hold":
				{
					applyHold(npc, state);
					break;
				}
				case "free":
				{
					STATES.remove(npcId);
					applyFree(npc);
					break;
				}
				case "patrol1":
				{
					state.patrolA = locationAtPlayer(player, formationOffset);
					break;
				}
				case "patrol2":
				{
					if (state.patrolA == null)
					{
						player.sendMessage("Primero guarda el punto A con ." + command + " patrol1.");
						continue;
					}
					state.patrolB = locationAtPlayer(player, formationOffset);
					state.patrolIndex = 0;
					state.order = Order.PATROL;
					applyMove(npc, state.patrolA);
					break;
				}
				default:
				{
					player.sendMessage("Orden desconocida: " + action);
					showHelp(player, command);
					return true;
				}
			}
			ordered++;
		}

		if (ordered > 0)
		{
			sendConfirmation(player, command, action, selectedTarget);
		}
		return true;
	}

	private static void updateOrders()
	{
		for (Map.Entry<Integer, ControlState> entry : STATES.entrySet())
		{
			final Npc npc = World.getNpc(entry.getKey());
			if ((npc == null) || npc.isDead())
			{
				continue;
			}

			final ControlState state = entry.getValue();
			switch (state.order)
			{
				case MOVE:
				{
					if (state.destination == null)
					{
						applyHold(npc, state);
					}
					else if (npc.calculateDistance2D(state.destination) <= ARRIVAL_DISTANCE)
					{
						applyHold(npc, state);
					}
					else if (npc.getAI().getIntention() != Intention.MOVE_TO)
					{
						applyMove(npc, state.destination);
					}
					break;
				}
				case PATROL:
				{
					if ((state.patrolA == null) || (state.patrolB == null))
					{
						applyHold(npc, state);
						break;
					}

					Location destination = (state.patrolIndex == 0) ? state.patrolA : state.patrolB;
					if (npc.calculateDistance2D(destination) <= ARRIVAL_DISTANCE)
					{
						state.patrolIndex = (state.patrolIndex == 0) ? 1 : 0;
						destination = (state.patrolIndex == 0) ? state.patrolA : state.patrolB;
						applyMove(npc, destination);
					}
					else if (npc.getAI().getIntention() != Intention.MOVE_TO)
					{
						applyMove(npc, destination);
					}
					break;
				}
				case FOLLOW:
				{
					final Player controller = World.getPlayer(state.controllerObjectId);
					if ((controller == null) || (controller.getInstanceId() != npc.getInstanceId()))
					{
						applyHold(npc, state);
					}
					else if (npc.getAI().getIntention() != Intention.FOLLOW)
					{
						applyFollow(npc, controller);
					}
					break;
				}
				case ATTACK:
				{
					final WorldObject target = World.findObject(state.targetObjectId);
					if (!isValidTarget(npc, target))
					{
						applyHold(npc, state);
					}
					else if ((npc.getAI().getIntention() != Intention.ATTACK) || (npc.getTarget() != target))
					{
						applyAttack(npc, target);
					}
					break;
				}
				case HOLD:
				default:
				{
					break;
				}
			}
		}
	}

	private static void applyAttack(Npc npc, WorldObject target)
	{
		npc.disableCoreAI(false);
		npc.setRandomWalking(false);
		npc.abortAttack();
		npc.abortCast();
		if (npc.isAttackable())
		{
			npc.asAttackable().clearAggroList();
			npc.asAttackable().addDamageHate(target.asCreature(), 0, 999999);
		}
		npc.setTarget(target);
		npc.getAI().setIntentionAttack(target);
	}

	private static void applyMove(Npc npc, Location destination)
	{
		prepareForTacticalOrder(npc);
		npc.getAI().setIntentionMoveTo(destination);
	}

	private static void applyFollow(Npc npc, Player controller)
	{
		prepareForTacticalOrder(npc);
		npc.getAI().setIntentionFollow(controller);
	}

	private static void applyHold(Npc npc, ControlState state)
	{
		state.order = Order.HOLD;
		prepareForTacticalOrder(npc);
		npc.stopMove(null);
	}

	private static void applyFree(Npc npc)
	{
		npc.abortAttack();
		npc.abortCast();
		if (npc.isAttackable())
		{
			npc.asAttackable().clearAggroList();
		}
		npc.setTarget(null);
		npc.disableCoreAI(false);
		npc.getAI().setIntentionActive();
	}

	private static void prepareForTacticalOrder(Npc npc)
	{
		npc.disableCoreAI(true);
		npc.setRandomWalking(false);
		npc.abortAttack();
		npc.abortCast();
		if (npc.isAttackable())
		{
			npc.asAttackable().clearAggroList();
		}
		npc.setTarget(null);
	}

	private static boolean isValidTarget(WorldObject commander, WorldObject target)
	{
		return (target != null) && (target != commander) && target.isCreature() && !target.asCreature().isDead() && (target.getInstanceId() == commander.getInstanceId());
	}

	private static Location locationAtPlayer(Player player, int xOffset)
	{
		return new Location(player.getX() + xOffset, player.getY(), player.getZ(), player.getHeading(), player.getInstanceId());
	}

	private static int[] getNpcIds(String command)
	{
		if (command.equalsIgnoreCase("ares"))
		{
			return new int[]
			{
				ARES_ID
			};
		}
		if (command.equalsIgnoreCase("nyx"))
		{
			return new int[]
			{
				NYX_ID
			};
		}
		return new int[]
		{
			ARES_ID,
			NYX_ID
		};
	}

	private static String normalizeAction(String params)
	{
		if ((params == null) || params.trim().isEmpty())
		{
			return "";
		}

		final String action = params.trim().split("\\s+", 2)[0].toLowerCase(Locale.ROOT);
		switch (action)
		{
			case "atacar":
			{
				return "attack";
			}
			case "mover":
			case "moverse":
			{
				return "move";
			}
			case "seguir":
			{
				return "follow";
			}
			case "mantener":
			case "parar":
			case "stop":
			{
				return "hold";
			}
			case "libre":
			{
				return "free";
			}
			case "patrulla1":
			{
				return "patrol1";
			}
			case "patrulla2":
			case "patrol":
			{
				return "patrol2";
			}
			case "estado":
			{
				return "status";
			}
			case "ayuda":
			{
				return "help";
			}
			default:
			{
				return action;
			}
		}
	}

	private static void sendConfirmation(Player player, String command, String action, WorldObject target)
	{
		final String unit = command.equalsIgnoreCase("squad") ? "Peloton" : getNpcName(command.equalsIgnoreCase("ares") ? ARES_ID : NYX_ID);
		switch (action)
		{
			case "attack":
			{
				player.sendMessage(unit + ": atacar a " + target.getName() + ".");
				break;
			}
			case "move":
			{
				player.sendMessage(unit + ": moverse a tu posicion actual.");
				break;
			}
			case "follow":
			{
				player.sendMessage(unit + ": seguirte.");
				break;
			}
			case "hold":
			{
				player.sendMessage(unit + ": mantener posicion.");
				break;
			}
			case "free":
			{
				player.sendMessage(unit + ": IA autonoma restaurada.");
				break;
			}
			case "patrol1":
			{
				player.sendMessage(unit + ": punto A de patrulla guardado aqui.");
				break;
			}
			case "patrol2":
			{
				player.sendMessage(unit + ": punto B guardado; patrulla iniciada.");
				break;
			}
			default:
			{
				break;
			}
		}
	}

	private static void showHelp(Player player, String command)
	{
		player.sendMessage("Control: ." + command + " attack | move | follow | hold | patrol1 | patrol2 | free | status");
		player.sendMessage("attack usa tu objetivo seleccionado; move usa el lugar donde estas parado.");
		player.sendMessage("Patrulla: parate en A y usa patrol1; parate en B y usa patrol2.");
	}

	private static void showStatus(Player player, int[] npcIds)
	{
		for (int npcId : npcIds)
		{
			final Npc npc = World.getNpc(npcId);
			final ControlState state = STATES.get(npcId);
			final String availability = ((npc != null) && !npc.isDead()) ? "presente" : "no disponible";
			player.sendMessage(getNpcName(npcId) + ": " + ((state == null) ? "LIBRE" : state.order.name()) + " (" + availability + ").");
		}
	}

	private static String getNpcName(int npcId)
	{
		return (npcId == ARES_ID) ? "Ares" : "Nyx";
	}

	@Override
	public String[] getCommandList()
	{
		return VOICED_COMMANDS;
	}

	private enum Order
	{
		HOLD,
		MOVE,
		FOLLOW,
		ATTACK,
		PATROL
	}

	private static final class ControlState
	{
		private volatile Order order = Order.HOLD;
		private volatile int controllerObjectId;
		private volatile int targetObjectId;
		private volatile Location destination;
		private volatile Location patrolA;
		private volatile Location patrolB;
		private volatile int patrolIndex;
	}
}
