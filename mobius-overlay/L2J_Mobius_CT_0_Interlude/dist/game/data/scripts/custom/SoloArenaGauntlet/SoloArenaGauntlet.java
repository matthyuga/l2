/*
 * This file is part of the L2J Mobius project.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */
package custom.SoloArenaGauntlet;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Locale;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.ai.Intention;
import org.l2jmobius.gameserver.entity.Location;
import org.l2jmobius.gameserver.entity.World;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;

/**
 * Runs the nine anchor fighters as a sequential one-versus-one Coliseum gauntlet.
 * @author Codex
 */
public class SoloArenaGauntlet implements IVoicedCommandHandler
{
	private static final Logger LOGGER = Logger.getLogger(SoloArenaGauntlet.class.getName());
	private static final Object STATE_LOCK = new Object();
	private static final String[] COMMANDS =
	{
		"arena"
	};
	private static final int[] FIGHTER_IDS =
	{
		901100, 901101, 901102, 901103, 901104, 901105, 901106, 901107, 901108
	};
	private static final String[] FIGHTER_NAMES =
	{
		"Arden", "Selene", "Eryndor", "Lethiel", "Vaelkor", "Myrentha", "Gorvak", "Zhurak", "Brunna"
	};
	private static final Location[] WAIT_POSITIONS =
	{
		new Location(148500, 44350, -3400, 16384),
		new Location(148600, 44270, -3400, 16384),
		new Location(148700, 44350, -3400, 16384),
		new Location(148800, 44270, -3400, 16384),
		new Location(148900, 44350, -3400, 16384),
		new Location(149000, 44270, -3400, 16384),
		new Location(149100, 44350, -3400, 16384),
		new Location(149200, 44270, -3400, 16384),
		new Location(149300, 44350, -3400, 16384)
	};
	private static final Location ARENA_CENTER = new Location(148900, 45500, -3400);
	private static final int ARENA_RADIUS = 3200;
	private static final int CENTER_ARRIVAL_DISTANCE = 140;
	private static final int WAIT_POSITION_TOLERANCE = 120;
	private static final long PREPARATION_MILLIS = 10000;
	private static final long MAX_ENTRANCE_RUN_MILLIS = 10000;

	private Phase _phase = Phase.IDLE;
	private int _controllerObjectId;
	private int _roundIndex;
	private int _activeNpcObjectId;
	private long _phaseStartedMs;
	private long _nextLaunchMs;
	private int _lastCountdown = -1;
	private long _runId;
	private long _duelStartedMs;

	private SoloArenaGauntlet()
	{
		createTables();
		VoicedCommandHandler.getInstance().registerHandler(this);
		ThreadPool.scheduleAtFixedRate(this::tick, 1500, 500);
		LOGGER.info("Coliseo secuencial activo: comando .arena, nueve rivales y telemetria por duelo.");
	}

	@Override
	public boolean onCommand(String command, Player player, String params)
	{
		final String action = normalize(params);
		switch (action)
		{
			case "start":
			case "iniciar":
			case "comenzar":
			case "repeat":
			case "repetir":
			{
				startExperiment(player);
				break;
			}
			case "status":
			case "estado":
			{
				showStatus(player);
				break;
			}
			case "cancel":
			case "cancelar":
			{
				cancelExperiment(player);
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

	private void startExperiment(Player player)
	{
		if (!isInsideColiseum(player))
		{
			player.sendMessage("Debes estar dentro del Coliseo para iniciar el experimento.");
			return;
		}
		if (player.isDead())
		{
			player.sendMessage("Revive antes de iniciar el experimento.");
			return;
		}
		if (player.isInCombat())
		{
			player.sendMessage("Sal del combate antes de iniciar el experimento.");
			return;
		}

		synchronized (STATE_LOCK)
		{
			if (isActivePhase(_phase))
			{
				final Player controller = World.getPlayer(_controllerObjectId);
				player.sendMessage("Ya hay un experimento activo" + ((controller != null) ? " para " + controller.getName() : "") + ".");
				return;
			}

			if (!prepareAllFighters())
			{
				player.sendMessage("Aun no estan disponibles los nueve rivales. Espera unos segundos y vuelve a usar .arena iniciar.");
				return;
			}

			_controllerObjectId = player.getObjectId();
			_roundIndex = 0;
			_activeNpcObjectId = 0;
			_runId = createRun(player);
			_duelStartedMs = 0;
			player.sendMessage("Experimento iniciado: nueve duelos 1 contra 1. Entre victorias tendras 10 segundos de preparacion.");
			launchCurrentFighter(player);
		}
	}

	private void cancelExperiment(Player player)
	{
		synchronized (STATE_LOCK)
		{
			if (!isActivePhase(_phase))
			{
				player.sendMessage("No hay un experimento activo.");
				return;
			}
			if ((_controllerObjectId != player.getObjectId()) && !player.isGM())
			{
				player.sendMessage("Solo el participante o un GM puede cancelar el experimento.");
				return;
			}
			finishRun("CANCELLED", _roundIndex);
			resetState(Phase.CANCELLED);
			prepareAllFighters();
			player.sendMessage("Experimento cancelado. Usa .arena repetir cuando quieras comenzar de nuevo.");
		}
	}

	private void showStatus(Player player)
	{
		synchronized (STATE_LOCK)
		{
			if (!isActivePhase(_phase))
			{
				player.sendMessage("Arena secuencial: " + _phase.label + ". Usa .arena iniciar.");
				return;
			}
			player.sendMessage("Arena secuencial: " + _phase.label + ", rival " + (_roundIndex + 1) + "/9 " + FIGHTER_NAMES[_roundIndex] + ".");
		}
	}

	private void tick()
	{
		try
		{
			synchronized (STATE_LOCK)
			{
				final Player player = World.getPlayer(_controllerObjectId);
				if (!isActivePhase(_phase))
				{
					holdWaitingFighters(0);
					return;
				}

				if ((player == null) || !player.isOnline() || !isInsideColiseum(player))
				{
					finishRun("CANCELLED", _roundIndex);
					resetState(Phase.CANCELLED);
					prepareAllFighters();
					return;
				}
				if (player.isDead())
				{
					onPlayerDefeated(player);
					return;
				}

				holdWaitingFighters(_activeNpcObjectId);
				switch (_phase)
				{
					case PREPARATION:
					{
						tickPreparation(player);
						break;
					}
					case RUNNING_TO_CENTER:
					{
						tickEntrance(player);
						break;
					}
					case FIGHTING:
					{
						tickFight(player);
						break;
					}
					default:
					{
						break;
					}
				}
			}
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "No se pudo actualizar el experimento secuencial del Coliseo.", e);
		}
	}

	private void tickPreparation(Player player)
	{
		final long remainingMs = _nextLaunchMs - System.currentTimeMillis();
		if (remainingMs <= 0)
		{
			launchCurrentFighter(player);
			return;
		}
		final int seconds = (int) Math.ceil(remainingMs / 1000.0);
		if ((seconds != _lastCountdown) && ((seconds == 10) || (seconds == 5) || (seconds <= 3)))
		{
			_lastCountdown = seconds;
			player.sendMessage("Siguiente rival en " + seconds + " segundo" + ((seconds == 1) ? "" : "s") + ": " + FIGHTER_NAMES[_roundIndex] + ".");
		}
	}

	private void tickEntrance(Player player)
	{
		final Npc npc = findByObjectId(_activeNpcObjectId);
		if ((npc == null) || npc.isDead())
		{
			abortRun(player, "El rival activo dejo de estar disponible antes del duelo.");
			return;
		}
		if ((npc.calculateDistance2D(ARENA_CENTER) <= CENTER_ARRIVAL_DISTANCE) || ((System.currentTimeMillis() - _phaseStartedMs) >= MAX_ENTRANCE_RUN_MILLIS))
		{
			beginFight(player, npc);
			return;
		}
		if (npc.getAI().getIntention() != Intention.MOVE_TO)
		{
			npc.getAI().setIntentionMoveTo(ARENA_CENTER);
		}
	}

	private void tickFight(Player player)
	{
		final Npc npc = findByObjectId(_activeNpcObjectId);
		if ((npc == null) || npc.isDead())
		{
			onFighterDefeated(player, npc);
			return;
		}

		if ((npc.getAI().getIntention() != Intention.ATTACK) || (npc.getTarget() != player))
		{
			attackPlayer(npc, player);
		}
	}

	private void launchCurrentFighter(Player player)
	{
		final Npc npc = findArenaFighter(FIGHTER_IDS[_roundIndex]);
		if (npc == null)
		{
			abortRun(player, "No se encontro a " + FIGHTER_NAMES[_roundIndex] + " en la entrada sur.");
			return;
		}
		prepareWaitingFighter(npc, _roundIndex, true);
		npc.setInvul(true);
		npc.disableCoreAI(true);
		npc.getAI().setIntentionMoveTo(ARENA_CENTER);
		_activeNpcObjectId = npc.getObjectId();
		_phase = Phase.RUNNING_TO_CENTER;
		_phaseStartedMs = System.currentTimeMillis();
		_lastCountdown = -1;
		updateRunProgress(_roundIndex + 1, _roundIndex);
		player.sendMessage("Rival " + (_roundIndex + 1) + "/9: " + FIGHTER_NAMES[_roundIndex] + " sale de la entrada sur y corre al centro.");
	}

	private void beginFight(Player player, Npc npc)
	{
		npc.fullRestore();
		npc.setInvul(false);
		npc.disableCoreAI(false);
		attackPlayer(npc, player);
		_phase = Phase.FIGHTING;
		_phaseStartedMs = System.currentTimeMillis();
		_duelStartedMs = _phaseStartedMs;
		player.sendMessage("Duelo " + (_roundIndex + 1) + "/9: " + FIGHTER_NAMES[_roundIndex] + " te ha encontrado. Combate.");
	}

	private void onFighterDefeated(Player player, Npc npc)
	{
		storeDuel("WIN", player, npc);
		final String defeatedName = FIGHTER_NAMES[_roundIndex];
		_roundIndex++;
		_activeNpcObjectId = 0;
		_duelStartedMs = 0;
		if (_roundIndex >= FIGHTER_IDS.length)
		{
			finishRun("COMPLETED", FIGHTER_IDS.length);
			_phase = Phase.COMPLETED;
			player.sendMessage("Experimento terminado. Felicitaciones: derrotaste a los 9 rivales.");
			player.sendMessage("Para repetirlo usa el macro .arena repetir.");
			return;
		}

		_phase = Phase.PREPARATION;
		_phaseStartedMs = System.currentTimeMillis();
		_nextLaunchMs = _phaseStartedMs + PREPARATION_MILLIS;
		_lastCountdown = -1;
		updateRunProgress(_roundIndex + 1, _roundIndex);
		player.sendMessage(defeatedName + " derrotado. Tienes 10 segundos de preparacion.");
	}

	private void onPlayerDefeated(Player player)
	{
		final Npc npc = findByObjectId(_activeNpcObjectId);
		if ((_phase == Phase.FIGHTING) && (_duelStartedMs > 0))
		{
			storeDuel("LOSS", player, npc);
		}
		finishRun("FAILED", _roundIndex);
		final String rival = (_roundIndex < FIGHTER_NAMES.length) ? FIGHTER_NAMES[_roundIndex] : "el rival";
		resetState(Phase.FAILED);
		prepareAllFighters();
		player.sendMessage("Experimento interrumpido: " + rival + " te derroto. Revive y usa .arena repetir.");
	}

	private void abortRun(Player player, String reason)
	{
		finishRun("CANCELLED", _roundIndex);
		resetState(Phase.CANCELLED);
		prepareAllFighters();
		player.sendMessage(reason + " El experimento fue cancelado; usa .arena repetir.");
	}

	private boolean prepareAllFighters()
	{
		boolean allReady = true;
		for (int index = 0; index < FIGHTER_IDS.length; index++)
		{
			final Npc npc = findArenaFighter(FIGHTER_IDS[index]);
			if (npc == null)
			{
				allReady = false;
				continue;
			}
			prepareWaitingFighter(npc, index, true);
		}
		return allReady;
	}

	private void holdWaitingFighters(int excludedObjectId)
	{
		for (int index = 0; index < FIGHTER_IDS.length; index++)
		{
			final Npc npc = findArenaFighter(FIGHTER_IDS[index]);
			if ((npc != null) && (npc.getObjectId() != excludedObjectId) && !npc.isDead())
			{
				prepareWaitingFighter(npc, index, false);
			}
		}
	}

	private static void prepareWaitingFighter(Npc npc, int index, boolean restore)
	{
		if (npc.isDead())
		{
			npc.doRevive();
		}
		if (restore)
		{
			npc.fullRestore();
		}
		npc.setInvul(true);
		npc.disableCoreAI(true);
		npc.setRandomWalking(false);
		npc.abortAttack();
		npc.abortCast();
		if (npc.isAttackable())
		{
			npc.asAttackable().clearAggroList();
		}
		npc.setTarget(null);
		npc.getAI().setIntentionActive();
		final Location wait = WAIT_POSITIONS[index];
		if (npc.calculateDistance2D(wait) > WAIT_POSITION_TOLERANCE)
		{
			npc.teleToLocation(wait.getX(), wait.getY(), wait.getZ(), wait.getHeading(), 0, false);
		}
	}

	private static void attackPlayer(Npc npc, Player player)
	{
		npc.disableCoreAI(false);
		npc.setRandomWalking(false);
		if (npc.isAttackable())
		{
			npc.asAttackable().clearAggroList();
			npc.asAttackable().addDamageHate(player, 0, 999999);
		}
		npc.setTarget(player);
		npc.getAI().setIntentionAttack(player);
	}

	private static Npc findArenaFighter(int npcId)
	{
		Npc closest = null;
		double closestDistance = Double.MAX_VALUE;
		for (WorldObject object : World.getVisibleObjects())
		{
			if (!object.isNpc() || (object.getId() != npcId) || (object.getInstanceId() != 0))
			{
				continue;
			}
			final Npc npc = object.asNpc();
			final double distance = npc.calculateDistance2D(ARENA_CENTER);
			if ((distance <= ARENA_RADIUS) && (distance < closestDistance))
			{
				closest = npc;
				closestDistance = distance;
			}
		}
		return closest;
	}

	private static Npc findByObjectId(int objectId)
	{
		final WorldObject object = World.findObject(objectId);
		return ((object != null) && object.isNpc()) ? object.asNpc() : null;
	}

	private static boolean isInsideColiseum(Player player)
	{
		return (player != null) && player.isOnline() && (player.getInstanceId() == 0) && (player.calculateDistance2D(ARENA_CENTER) <= ARENA_RADIUS);
	}

	private void resetState(Phase finalPhase)
	{
		_phase = finalPhase;
		_controllerObjectId = 0;
		_activeNpcObjectId = 0;
		_roundIndex = 0;
		_phaseStartedMs = 0;
		_nextLaunchMs = 0;
		_lastCountdown = -1;
		_duelStartedMs = 0;
		_runId = 0;
	}

	private static boolean isActivePhase(Phase phase)
	{
		return (phase == Phase.PREPARATION) || (phase == Phase.RUNNING_TO_CENTER) || (phase == Phase.FIGHTING);
	}

	private static String normalize(String params)
	{
		if ((params == null) || params.trim().isEmpty())
		{
			return "";
		}
		return params.trim().split("\\s+", 2)[0].toLowerCase(Locale.ROOT);
	}

	private static void showHelp(Player player)
	{
		player.sendMessage("Arena secuencial: .arena iniciar | estado | cancelar | repetir");
		player.sendMessage("Macro recomendado: .arena iniciar");
	}

	private void createTables()
	{
		try (Connection con = DatabaseFactory.getConnection(); Statement st = con.createStatement())
		{
			st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_arena_gauntlet_runs (run_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, player_object_id INT NOT NULL, player_name VARCHAR(45) NOT NULL, player_class_id INT NOT NULL, player_level SMALLINT NOT NULL, started_ms BIGINT UNSIGNED NOT NULL, ended_ms BIGINT UNSIGNED NOT NULL DEFAULT 0, status VARCHAR(16) NOT NULL, current_round SMALLINT NOT NULL DEFAULT 0, defeated_count SMALLINT NOT NULL DEFAULT 0, PRIMARY KEY (run_id), KEY idx_gauntlet_player_time (player_object_id, started_ms)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
			st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_arena_gauntlet_duels (duel_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, run_id BIGINT UNSIGNED NOT NULL, round_number SMALLINT NOT NULL, npc_template_id INT NOT NULL, npc_name VARCHAR(45) NOT NULL, started_ms BIGINT UNSIGNED NOT NULL, ended_ms BIGINT UNSIGNED NOT NULL, outcome VARCHAR(12) NOT NULL, player_hp DOUBLE NOT NULL, player_cp DOUBLE NOT NULL, player_mp DOUBLE NOT NULL, npc_hp DOUBLE NOT NULL, npc_cp DOUBLE NOT NULL, npc_mp DOUBLE NOT NULL, PRIMARY KEY (duel_id), KEY idx_gauntlet_run_round (run_id, round_number)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
		}
		catch (SQLException e)
		{
			LOGGER.log(Level.WARNING, "No se pudieron crear las tablas de la arena secuencial.", e);
		}
	}

	private long createRun(Player player)
	{
		final String sql = "INSERT INTO lab_arena_gauntlet_runs (player_object_id,player_name,player_class_id,player_level,started_ms,status,current_round,defeated_count) VALUES (?,?,?,?,?,'RUNNING',1,0)";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS))
		{
			ps.setInt(1, player.getObjectId());
			ps.setString(2, player.getName());
			ps.setInt(3, player.getActiveClass());
			ps.setInt(4, player.getLevel());
			ps.setLong(5, System.currentTimeMillis());
			ps.executeUpdate();
			try (ResultSet rs = ps.getGeneratedKeys())
			{
				return rs.next() ? rs.getLong(1) : 0;
			}
		}
		catch (SQLException e)
		{
			LOGGER.log(Level.WARNING, "No se pudo abrir la sesion telemetrica de la arena secuencial.", e);
			return 0;
		}
	}

	private void updateRunProgress(int currentRound, int defeatedCount)
	{
		if (_runId <= 0)
		{
			return;
		}
		final long runId = _runId;
		ThreadPool.execute(() ->
		{
			try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("UPDATE lab_arena_gauntlet_runs SET current_round=?, defeated_count=? WHERE run_id=?"))
			{
				ps.setInt(1, currentRound);
				ps.setInt(2, defeatedCount);
				ps.setLong(3, runId);
				ps.executeUpdate();
			}
			catch (SQLException e)
			{
				LOGGER.log(Level.WARNING, "No se pudo actualizar el progreso de la arena secuencial.", e);
			}
		});
	}

	private void storeDuel(String outcome, Player player, Npc npc)
	{
		if ((_runId <= 0) || (_duelStartedMs <= 0))
		{
			return;
		}
		final long runId = _runId;
		final int round = _roundIndex + 1;
		final int npcId = FIGHTER_IDS[_roundIndex];
		final String npcName = FIGHTER_NAMES[_roundIndex];
		final long started = _duelStartedMs;
		final long ended = System.currentTimeMillis();
		final double playerHp = player.getCurrentHp();
		final double playerCp = player.getCurrentCp();
		final double playerMp = player.getCurrentMp();
		final double npcHp = (npc != null) ? npc.getCurrentHp() : 0;
		final double npcCp = (npc != null) ? npc.getCurrentCp() : 0;
		final double npcMp = (npc != null) ? npc.getCurrentMp() : 0;
		ThreadPool.execute(() ->
		{
			final String sql = "INSERT INTO lab_arena_gauntlet_duels (run_id,round_number,npc_template_id,npc_name,started_ms,ended_ms,outcome,player_hp,player_cp,player_mp,npc_hp,npc_cp,npc_mp) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)";
			try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql))
			{
				ps.setLong(1, runId);
				ps.setInt(2, round);
				ps.setInt(3, npcId);
				ps.setString(4, npcName);
				ps.setLong(5, started);
				ps.setLong(6, ended);
				ps.setString(7, outcome);
				ps.setDouble(8, playerHp);
				ps.setDouble(9, playerCp);
				ps.setDouble(10, playerMp);
				ps.setDouble(11, npcHp);
				ps.setDouble(12, npcCp);
				ps.setDouble(13, npcMp);
				ps.executeUpdate();
			}
			catch (SQLException e)
			{
				LOGGER.log(Level.WARNING, "No se pudo guardar el duelo de la arena secuencial.", e);
			}
		});
	}

	private void finishRun(String status, int defeatedCount)
	{
		if (_runId <= 0)
		{
			return;
		}
		final long runId = _runId;
		ThreadPool.execute(() ->
		{
			try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("UPDATE lab_arena_gauntlet_runs SET ended_ms=?, status=?, defeated_count=? WHERE run_id=?"))
			{
				ps.setLong(1, System.currentTimeMillis());
				ps.setString(2, status);
				ps.setInt(3, defeatedCount);
				ps.setLong(4, runId);
				ps.executeUpdate();
			}
			catch (SQLException e)
			{
				LOGGER.log(Level.WARNING, "No se pudo cerrar la sesion telemetrica de la arena secuencial.", e);
			}
		});
	}

	@Override
	public String[] getCommandList()
	{
		return COMMANDS;
	}

	public static void main(String[] args)
	{
		new SoloArenaGauntlet();
	}

	private enum Phase
	{
		IDLE("en espera"),
		PREPARATION("preparacion"),
		RUNNING_TO_CENTER("entrada del rival"),
		FIGHTING("combate"),
		COMPLETED("completada"),
		FAILED("fallida"),
		CANCELLED("cancelada");

		private final String label;

		Phase(String label)
		{
			this.label = label;
		}
	}
}
