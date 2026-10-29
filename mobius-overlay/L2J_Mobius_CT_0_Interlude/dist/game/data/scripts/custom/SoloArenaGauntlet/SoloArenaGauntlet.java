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
import org.l2jmobius.gameserver.entity.spawns.Spawn;
import org.l2jmobius.gameserver.data.xml.PlayerTemplateData;
import org.l2jmobius.gameserver.entity.actor.appearance.PlayerAppearance;
import org.l2jmobius.gameserver.handler.IVoicedCommandHandler;
import org.l2jmobius.gameserver.handler.VoicedCommandHandler;
import custom.NormalNpcRoster.NormalNpcRoster;

/**
 * Runs thirty-nine rivals in sequential or individually selected Coliseum duels.
 * @author Codex
 */
public class SoloArenaGauntlet implements IVoicedCommandHandler
{
	private static final Logger LOGGER = Logger.getLogger(SoloArenaGauntlet.class.getName());
	private static final Object STATE_LOCK = new Object();
	private static SoloArenaGauntlet INSTANCE;
	private static boolean PILOT_ACTIVE;
	private static final String[] COMMANDS =
	{
		"arena"
	};
	private static final int[] FIGHTER_IDS =
	{
		901100, 901101, 901102, 901103, 901104, 901105, 901106, 901107, 901108, 901109, 901110, 901111,
		901112, 901113, 901114, 901115, 901116, 901117, 901118,
		901119, 901120, 901121, 901122, 901123, 901124, 901125, 901126, 901127, 901128, 901129, 901130, 901131, 901132, 901133, 901134, 901135, 901136, 901137, 901138
	};
	private static final String[] FIGHTER_NAMES =
	{
		"Arden", "Selene", "Eryndor", "Lethiel", "Vaelkor", "Myrentha", "Gorvak", "Zhurak", "Brunna", "Kaelis", "Riven", "Noctis",
		"Caelan", "Ignara", "Aelira", "Korvash", "Morvain", "Sylira", "Velith",
		"Darion", "Valerian", "Malrik", "Lucien", "Seraphine", "Darius", "Thalion", "Elowen", "Faelith", "Nerys", "Draven", "Nysera", "Veyron", "Zareth", "Saevra", "Rhogar", "Mazhura", "Urkan", "Dagna", "Borin"
	};
	private static final Location ARENA_CENTER = new Location(148900, 46100, -3400);
	private static final Location SAFE_DUEL_ENTRY = new Location(148900, 45800, -3400, 16384);
	private static final int ARENA_RADIUS = 3200;
	private static final int CENTER_ARRIVAL_DISTANCE = 140;
	private static final long PREPARATION_MILLIS = 10000;
	private static final long MAX_ENTRANCE_RUN_MILLIS = 6000;

	private Phase _phase = Phase.IDLE;
	private int _controllerObjectId;
	private int _roundIndex;
	private int _activeNpcObjectId;
	private Spawn _activeSpawn;
	private long _phaseStartedMs;
	private long _nextLaunchMs;
	private int _lastCountdown = -1;
	private long _runId;
	private long _duelStartedMs;
	private boolean _singleDuel;
	private int _defeatedCount;

	private SoloArenaGauntlet()
	{
		INSTANCE=this;
		createTables();
		VoicedCommandHandler.getInstance().registerHandler(this);
		ThreadPool.scheduleAtFixedRate(this::tick, 1500, 500);
		LOGGER.info("Coliseo secuencial activo: comando .arena, " + FIGHTER_IDS.length + " rivales y telemetria por duelo.");
		if (Boolean.getBoolean("lab.arena.spawn.verify")) ThreadPool.schedule(this::verifyOnDemandSpawns, 60000);
	}

	@Override
	public boolean onCommand(String command, Player player, String params)
	{
		final String action = normalize(params);
		switch (action)
		{
			case "lista":
			case "list":
			{
				for (int index=0;index<FIGHTER_NAMES.length;index++) player.sendMessage((index+1)+". "+FIGHTER_NAMES[index]);
				player.sendMessage("Elige un rival: .arena probar nombre o numero");
				break;
			}
			case "probar":
			case "test":
			{
				String[] parts=params.trim().split("\\s+",2);
				int index=parts.length==2?resolveFighter(parts[1]):-1;
				if(index<0) player.sendMessage("Rival desconocido. Usa .arena lista y luego .arena probar nombre o numero.");
				else startExperiment(player,index,true);
				break;
			}
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
		startExperiment(player,0,false);
	}

	private void startExperiment(Player player,int firstIndex,boolean singleDuel)
	{
		if (!NormalNpcRoster.isReady())
		{
			player.sendMessage("Los perfiles normales aun se estan preparando o fallaron. Espera y revisa el laboratorio.");
			return;
		}
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
			if(PILOT_ACTIVE)
			{
				player.sendMessage("Hay una prueba de IA Player activa. Termina o cancela con .ia cancelar.");
				return;
			}
			if (isActivePhase(_phase))
			{
				final Player controller = World.getPlayer(_controllerObjectId);
				player.sendMessage("Ya hay un experimento activo" + ((controller != null) ? " para " + controller.getName() : "") + ".");
				return;
			}

			_controllerObjectId = player.getObjectId();
			_roundIndex = firstIndex;
			_singleDuel = singleDuel;
			_defeatedCount = 0;
			_activeNpcObjectId = 0;
			_runId = createRun(player);
			_duelStartedMs = 0;
			updateRunProgress(_roundIndex+1,0);
			player.sendMessage(singleDuel?"Prueba individual contra "+FIGHTER_NAMES[_roundIndex]+". No saldra otro rival al finalizar.":"Experimento iniciado: " + FIGHTER_IDS.length + " duelos 1 contra 1. Entre victorias tendras 10 segundos de preparacion.");
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
			finishRun("CANCELLED", _defeatedCount);
			resetState(Phase.CANCELLED);
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
			player.sendMessage("Arena secuencial: " + _phase.label + ", rival " + (_roundIndex + 1) + "/" + FIGHTER_IDS.length + " " + FIGHTER_NAMES[_roundIndex] + ".");
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
					return;
				}

				if ((player == null) || !player.isOnline() || !isInsideColiseum(player))
				{
					finishRun("CANCELLED", _defeatedCount);
					resetState(Phase.CANCELLED);
					return;
				}
				if (player.isDead())
				{
					onPlayerDefeated(player);
					return;
				}

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
		if (npc.calculateDistance2D(ARENA_CENTER) <= CENTER_ARRIVAL_DISTANCE)
		{
			beginFight(player, npc);
			return;
		}
		if ((System.currentTimeMillis() - _phaseStartedMs) >= MAX_ENTRANCE_RUN_MILLIS)
		{
			// Never start a duel from behind a wall. If movement stalls, relocate to
			// the already proven Ares/Nyx floor and begin from the visible center.
			npc.teleToLocation(ARENA_CENTER.getX(), ARENA_CENTER.getY(), ARENA_CENTER.getZ(), 16384, 0, false);
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
		Npc npc = null;
		try
		{
			_activeSpawn = new Spawn(FIGHTER_IDS[_roundIndex]);
			_activeSpawn.setLocation(SAFE_DUEL_ENTRY);
			npc = _activeSpawn.doSpawn();
			_activeSpawn.stopRespawn();
			if (npc == null) throw new IllegalStateException("No se pudo crear el rival");
			_activeNpcObjectId = npc.getObjectId();
			npc.setInvul(true);
			npc.disableCoreAI(true);
			npc.setRandomWalking(false);
			NormalNpcRoster.applyPreparedStats(npc);
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "No se pudo preparar el rival bajo demanda.", e);
			abortRun(player, "No se pudo preparar a " + FIGHTER_NAMES[_roundIndex] + ".");
			return;
		}
		npc.getAI().setIntentionMoveTo(ARENA_CENTER);
		_phase = Phase.RUNNING_TO_CENTER;
		_phaseStartedMs = System.currentTimeMillis();
		_lastCountdown = -1;
		updateRunProgress(_roundIndex + 1, _roundIndex);
		player.sendMessage("Rival " + (_roundIndex + 1) + "/" + FIGHTER_IDS.length + ": " + FIGHTER_NAMES[_roundIndex] + " entra desde el sector sur interior y corre al centro.");
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
		player.sendMessage("Duelo " + (_roundIndex + 1) + "/" + FIGHTER_IDS.length + ": " + FIGHTER_NAMES[_roundIndex] + " te ha encontrado. Combate.");
	}

	private void onFighterDefeated(Player player, Npc npc)
	{
		storeDuel("WIN", player, npc);
		despawnCurrentFighter();
		final String defeatedName = FIGHTER_NAMES[_roundIndex];
		_defeatedCount++;
		if(_singleDuel)
		{
			finishRun("COMPLETED",_defeatedCount);
			resetState(Phase.COMPLETED);
			player.sendMessage("Prueba individual terminada: derrotaste a "+defeatedName+". Recuperate y elige el siguiente con .arena probar nombre.");
			return;
		}
		_roundIndex++;
		_activeNpcObjectId = 0;
		_duelStartedMs = 0;
		if (_roundIndex >= FIGHTER_IDS.length)
		{
			finishRun("COMPLETED", FIGHTER_IDS.length);
			_phase = Phase.COMPLETED;
			player.sendMessage("Experimento terminado. Felicitaciones: derrotaste a los " + FIGHTER_IDS.length + " rivales.");
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
		finishRun("FAILED", _defeatedCount);
		final boolean singleDuel = _singleDuel;
		final String rival = (_roundIndex < FIGHTER_NAMES.length) ? FIGHTER_NAMES[_roundIndex] : "el rival";
		resetState(Phase.FAILED);
		player.sendMessage("Experimento interrumpido: " + rival + " te derroto. Revive y usa " + (singleDuel ? ".arena probar " + rival : ".arena repetir") + ".");
	}

	private void abortRun(Player player, String reason)
	{
		finishRun("CANCELLED", _defeatedCount);
		resetState(Phase.CANCELLED);
		player.sendMessage(reason + " El experimento fue cancelado; usa .arena repetir.");
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
		despawnCurrentFighter();
		_phase = finalPhase;
		_controllerObjectId = 0;
		_activeNpcObjectId = 0;
		_roundIndex = 0;
		_phaseStartedMs = 0;
		_nextLaunchMs = 0;
		_lastCountdown = -1;
		_duelStartedMs = 0;
		_runId = 0;
		_singleDuel = false;
		_defeatedCount = 0;
	}

	private void despawnCurrentFighter()
	{
		if (_activeSpawn != null) _activeSpawn.stopRespawn();
		final Npc npc = findByObjectId(_activeNpcObjectId);
		if (npc != null)
		{
			npc.abortAttack();
			npc.abortCast();
			npc.deleteMe();
		}
		_activeSpawn = null;
		_activeNpcObjectId = 0;
	}

	/** Explicit, headless lifecycle verification; never enabled by the normal launcher. */
	private void verifyOnDemandSpawns()
	{
		if (!NormalNpcRoster.isReady())
		{
			ThreadPool.schedule(this::verifyOnDemandSpawns, 5000);
			return;
		}
		Player probe = null;
		try
		{
			synchronized (STATE_LOCK)
			{
				for (WorldObject obj : World.getVisibleObjects())
					if (obj.isPlayer() && obj.asPlayer().getClient() != null) throw new IllegalStateException("Verification needs no connected clients");
				if (PILOT_ACTIVE || isActivePhase(_phase)) throw new IllegalStateException("Arena already occupied");
				int probeId = 0;
				try (Connection c = DatabaseFactory.getConnection(); PreparedStatement q = c.prepareStatement("SELECT charId,account_name,online FROM characters WHERE char_name='ArenaSpawnProbe'"))
				{
					try (ResultSet r = q.executeQuery())
					{
						if (r.next())
						{
							if (!"arenaspawntest".equals(r.getString(2)) || r.getInt(3) != 0 || World.getPlayer(r.getInt(1)) != null) throw new IllegalStateException("Reserved spawn probe unavailable");
							probeId = r.getInt(1);
						}
					}
				}
				probe = probeId == 0 ? Player.create(PlayerTemplateData.getInstance().getTemplate(0), "arenaspawntest", "ArenaSpawnProbe", new PlayerAppearance((byte)0,(byte)0,(byte)0,false)) : Player.load(probeId);
				if (probe == null) throw new IllegalStateException("Could not load spawn probe");
				probe.setLabControlled(true); probe.setDead(false); probe.setOnlineStatus(true,true); probe.setEnteredWorld();
				probe.spawnMe(148900,46100,-3408); probe.revalidateZone(true); probe.setInvul(true);
				int checks = 0;
				verifyRivalCount(0); checks++;
				for (int i=0; i<FIGHTER_IDS.length; i++)
				{
					onCommand("arena",probe,"probar " + (i+1));
					verifyRivalCount(1); checks++;
					Npc npc = findByObjectId(_activeNpcObjectId);
					if (npc == null || npc.getId() != FIGHTER_IDS[i] || npc.getMaxCp() <= 0 || npc.getMaxHp() <= 0 || _activeSpawn.isRespawnEnabled()) throw new IllegalStateException("Wrong opponent, stats or respawn policy");
					checks++;
					onCommand("arena",probe,"cancelar");
					verifyRivalCount(0); checks++;
				}
				startExperiment(probe,0,false);
				Npc first = findByObjectId(_activeNpcObjectId); beginFight(probe,first);
				first.doDie(probe); tick(); verifyRivalCount(0); checks++;
				if (_phase != Phase.PREPARATION || _roundIndex != 1) throw new IllegalStateException("Next round not queued"); checks++;
				_nextLaunchMs = 0; tick(); verifyRivalCount(1); checks++;
				probe.setDead(true); tick(); verifyRivalCount(0); checks++; probe.setDead(false);
				startExperiment(probe,0,true);
				probe.setOnlineStatus(false,true); tick(); verifyRivalCount(0); checks++;
				probe.setOnlineStatus(true,false); // deleteMe expects a world-resident probe to remain online until cleanup.
				LOGGER.info("ArenaSpawnVerification SUCCESS: " + checks + " checks; 39 on-demand opponents, cancellation, victory, next round, defeat and disconnect cleanup.");
			}
		}
		catch (Exception e) { LOGGER.log(Level.SEVERE,"ArenaSpawnVerification FAILED",e); }
		finally
		{
			synchronized (STATE_LOCK)
			{
				if (probe != null)
				{
					if (_controllerObjectId == probe.getObjectId()) { finishRun("VERIFY_CLEANUP",_defeatedCount); resetState(Phase.CANCELLED); }
					probe.setDead(false); probe.storeMe(); probe.deleteMe(); probe.setLabControlled(false); probe.setOnlineStatus(false,true);
				}
			}
		}
	}

	private static void verifyRivalCount(int expected)
	{
		int count=0;
		for (WorldObject obj : World.getVisibleObjects())
			if (obj.isNpc() && obj.getId()>=901100 && obj.getId()<=901138 && obj.getInstanceId()==0) count++;
		if (count != expected) throw new IllegalStateException("Expected " + expected + " public rivals, got " + count);
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
		player.sendMessage("Pruebas individuales: .arena lista | .arena probar nombre o numero");
	}

	public static int resolveFighter(String value)
	{
		if(value==null) return -1;
		String selected=value.trim();
		for(int index=0;index<FIGHTER_NAMES.length;index++)
			if(selected.equalsIgnoreCase(FIGHTER_NAMES[index]) || selected.equals(String.valueOf(index+1))) return index;
		return -1;
	}

	public static boolean tryClaimPilot()
	{
		synchronized(STATE_LOCK)
		{
			if(INSTANCE==null || PILOT_ACTIVE || isActivePhase(INSTANCE._phase)) return false;
			PILOT_ACTIVE=true;
			return true;
		}
	}

	public static void releasePilot()
	{
		synchronized(STATE_LOCK) {PILOT_ACTIVE=false;}
	}

	private void createTables()
	{
		try (Connection con = DatabaseFactory.getConnection(); Statement st = con.createStatement())
		{
			st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_arena_gauntlet_runs (run_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, player_object_id INT NOT NULL, player_name VARCHAR(45) NOT NULL, player_class_id INT NOT NULL, player_level SMALLINT NOT NULL, started_ms BIGINT UNSIGNED NOT NULL, ended_ms BIGINT UNSIGNED NOT NULL DEFAULT 0, status VARCHAR(16) NOT NULL, current_round SMALLINT NOT NULL DEFAULT 0, defeated_count SMALLINT NOT NULL DEFAULT 0, PRIMARY KEY (run_id), KEY idx_gauntlet_player_time (player_object_id, started_ms)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
			st.executeUpdate("ALTER TABLE lab_arena_gauntlet_runs ADD COLUMN IF NOT EXISTS test_mode VARCHAR(16) NOT NULL DEFAULT 'SEQUENCE', ADD COLUMN IF NOT EXISTS selected_npc_id INT NOT NULL DEFAULT 0");
			st.executeUpdate("CREATE TABLE IF NOT EXISTS lab_arena_gauntlet_duels (duel_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT, run_id BIGINT UNSIGNED NOT NULL, round_number SMALLINT NOT NULL, npc_template_id INT NOT NULL, npc_name VARCHAR(45) NOT NULL, started_ms BIGINT UNSIGNED NOT NULL, ended_ms BIGINT UNSIGNED NOT NULL, outcome VARCHAR(12) NOT NULL, player_hp DOUBLE NOT NULL, player_cp DOUBLE NOT NULL, player_mp DOUBLE NOT NULL, npc_hp DOUBLE NOT NULL, npc_cp DOUBLE NOT NULL, npc_mp DOUBLE NOT NULL, PRIMARY KEY (duel_id), KEY idx_gauntlet_run_round (run_id, round_number)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
		}
		catch (SQLException e)
		{
			LOGGER.log(Level.WARNING, "No se pudieron crear las tablas de la arena secuencial.", e);
		}
	}

	private long createRun(Player player)
	{
		final String sql = "INSERT INTO lab_arena_gauntlet_runs (player_object_id,player_name,player_class_id,player_level,started_ms,test_mode,selected_npc_id,status,current_round,defeated_count) VALUES (?,?,?,?,?,?,?,'RUNNING',1,0)";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS))
		{
			ps.setInt(1, player.getObjectId());
			ps.setString(2, player.getName());
			ps.setInt(3, player.getActiveClass());
			ps.setInt(4, player.getLevel());
			ps.setLong(5, System.currentTimeMillis());
			ps.setString(6,Boolean.getBoolean("lab.arena.spawn.verify") && "ArenaSpawnProbe".equals(player.getName()) ? "SPAWN_VERIFY" : (_singleDuel ? "INDIVIDUAL" : "SEQUENCE"));
			ps.setInt(7,_singleDuel ? FIGHTER_IDS[_roundIndex] : 0);
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
