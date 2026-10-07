/*
 * Local Lineage II laboratory combat telemetry.
 * Records combat facts only; it never changes combat calculations.
 */
package custom.LabTelemetry;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.l2jmobius.commons.database.DatabaseFactory;
import org.l2jmobius.commons.threads.ThreadPool;
import org.l2jmobius.gameserver.config.custom.ClassBalanceConfig;
import org.l2jmobius.gameserver.data.SpawnTable;
import org.l2jmobius.gameserver.data.xml.ExperienceData;
import org.l2jmobius.gameserver.entity.WorldObject;
import org.l2jmobius.gameserver.entity.actor.Creature;
import org.l2jmobius.gameserver.entity.actor.Npc;
import org.l2jmobius.gameserver.entity.actor.Player;
import org.l2jmobius.gameserver.entity.actor.Summon;
import org.l2jmobius.gameserver.entity.actor.enums.player.PlayerClass;
import org.l2jmobius.gameserver.entity.actor.holders.player.SubClassHolder;
import org.l2jmobius.gameserver.entity.item.enums.ItemProcessType;
import org.l2jmobius.gameserver.entity.item.enums.ShotType;
import org.l2jmobius.gameserver.entity.itemcontainer.Inventory;
import org.l2jmobius.gameserver.entity.item.instance.Item;
import org.l2jmobius.gameserver.mechanics.events.Containers;
import org.l2jmobius.gameserver.mechanics.events.EventType;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureAttackAvoid;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDamageDealt;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureDeath;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.creature.OnCreatureSkillUse;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerLogin;
import org.l2jmobius.gameserver.mechanics.events.holders.actor.player.OnPlayerProfessionChange;
import org.l2jmobius.gameserver.mechanics.events.listeners.ConsumerEventListener;
import org.l2jmobius.gameserver.mechanics.script.Script;
import org.l2jmobius.gameserver.mechanics.effects.AbstractEffect;
import org.l2jmobius.gameserver.mechanics.effects.EffectType;
import org.l2jmobius.gameserver.mechanics.skill.BuffInfo;
import org.l2jmobius.gameserver.mechanics.skill.EffectScope;
import org.l2jmobius.gameserver.mechanics.skill.Skill;
import org.l2jmobius.gameserver.mechanics.stats.Formulas;
import org.l2jmobius.gameserver.mechanics.stats.Stat;
import org.l2jmobius.gameserver.network.Disconnection;

/**
 * Captures damage, skill use, misses and deaths involving a real player or one
 * of the laboratory opponents. Inserts are asynchronous so combat is never
 * held up by the telemetry database.
 */
public class LabTelemetry extends Script
{
	private static final Logger LOGGER = Logger.getLogger(LabTelemetry.class.getName());
	private static LabTelemetry INSTANCE;
	private static final int LAB_NPC_ID_MIN = 900200;
	private static final int LAB_NPC_ID_MAX = 900299;
	private static final int CLEAN_PROFILE_LEVEL = 80;
	private static final Set<Integer> CONTROLLED_CAPTURE_IDS = ConcurrentHashMap.newKeySet();
	private static final int EXPECTED_PAIR_COUNT = 465;
	private static final int EXPECTED_BUILD_COUNT = 155;
	private static final int EXPECTED_BUILD_STATE_COUNT = EXPECTED_BUILD_COUNT * 4;
	private static final int EXPECTED_BENCHMARK_CASE_COUNT = 95;
	private static final int EXPECTED_BENCHMARK_RUN_COUNT = 285;
	private static final int EXPECTED_NYX_CALIBRATION_CASE_COUNT = 30;
	private static final int[] NYX_CALIBRATION_SCALES = {100, 75, 60, 50};
	private static final int EXPECTED_NYX_CALIBRATION_RUN_COUNT = EXPECTED_NYX_CALIBRATION_CASE_COUNT * 3 * NYX_CALIBRATION_SCALES.length;
	private static final int[] MAGIC_PROGRESSION_CLASS_IDS = {110, 103, 94, 95};
	private static final String[] MAGIC_PROGRESSION_LABELS = {"Storm Screamer", "+ Mystic Muse", "+ Archmage", "+ Soultaker"};
	private static final int MAGIC_PROGRESSION_WEAPON_ID = 6579;
	private static final int MAGIC_PROGRESSION_DURATION_SECONDS = 60;
	private static final int MAGIC_PROGRESSION_REPETITIONS = 3;
	private static final int EXPECTED_MAGIC_PROGRESSION_RUN_COUNT = MAGIC_PROGRESSION_CLASS_IDS.length * MAGIC_PROGRESSION_REPETITIONS;
	private static final String[] MAGIC_COMPARISON_PROTOCOLS = {"FIXED_HURRICANE", "BEST_AVAILABLE"};
	private static final int MAGIC_COMPARISON_FIXED_SKILL_ID = 1239;
	private static final int MAGIC_COMPARISON_REPETITIONS = 30;
	private static final int EXPECTED_MAGIC_COMPARISON_RUN_COUNT = MAGIC_PROGRESSION_CLASS_IDS.length * MAGIC_COMPARISON_PROTOCOLS.length * MAGIC_COMPARISON_REPETITIONS;
	private static final int[] PHYSICAL_RACE_ROOT_CLASS_IDS = {0}; // Human Fighter first; extend for cross-race replication.
	private static final int[] PHYSICAL_RACE_CLASS_IDS = {89, 113, 117, 118}; // Dreadnought + Titan + Fortune Seeker + Maestro.
	private static final String[] PHYSICAL_RACE_STAGE_LABELS = {"Dreadnought", "+ Titan", "+ Fortune Seeker", "+ Maestro"};
	private static final String[] PHYSICAL_RACE_PROTOCOLS = {"FIXED_AUTOATTACK", "BEST_COMPATIBLE"};
	private static final int PHYSICAL_RACE_WEAPON_ID = 6370; // Saint Spear.
	private static final int PHYSICAL_RACE_REPETITIONS = 30;
	private static final int EXPECTED_PHYSICAL_RACE_RUN_COUNT = PHYSICAL_RACE_ROOT_CLASS_IDS.length * PHYSICAL_RACE_CLASS_IDS.length * PHYSICAL_RACE_PROTOCOLS.length * PHYSICAL_RACE_REPETITIONS;
	private static final int BENCHMARK_ATLAS_ID = 900202;
	private static final int BENCHMARK_ARES_ID = 900200;
	private static final int BENCHMARK_NYX_ID = 900201;
	private static final Set<Integer> BENCHMARK_CAPTURE_IDS = ConcurrentHashMap.newKeySet();
	private static final int[] COMMON_JEWELRY_IDS = {858, 858, 889, 889, 920};
	private static final int[] HEAVY_ARMOR_IDS = {6373, 6374, 6375, 6376, 6378};
	private static final int[] LIGHT_ARMOR_IDS = {6379, 6380, 6381, 6382};
	private static final int[] ROBE_ARMOR_IDS = {6383, 6384, 6385, 6386};
	private static final Set<Integer> SHIELD_CLASS_IDS = Set.of(90, 91, 99, 106);
	private static final int PAIR_WORKER_COUNT = 8;
	private static final String[] PAIR_WORKER_NAMES =
	{
		"Arden", "Eryndor", "Gorvak", "Selene", "Vaelkor", "Brunna", "Lethiel", "Myrentha"
	};
	private static final int[] PAIR_WORKER_ROOTS =
	{
		0, 18, 44, 10, 31, 53, 25, 38
	};
	private static final String[] ANCHOR_NAMES =
	{
		"Arden", "Selene", "Eryndor", "Lethiel", "Vaelkor", "Myrentha", "Gorvak", "Zhurak", "Brunna"
	};
	private static final int[] ANCHOR_ROOT_CLASS_IDS =
	{
		0, 10, 18, 25, 31, 38, 44, 49, 53
	};

	private static final String CREATE_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_combat_events (" +
		"event_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT," +
		"occurred_ms BIGINT UNSIGNED NOT NULL," +
		"event_type VARCHAR(16) NOT NULL," +
		"attacker_object_id INT NOT NULL DEFAULT 0," +
		"attacker_name VARCHAR(45) NOT NULL DEFAULT ''," +
		"attacker_kind VARCHAR(12) NOT NULL DEFAULT ''," +
		"attacker_template_id INT NOT NULL DEFAULT 0," +
		"attacker_class_id INT NOT NULL DEFAULT -1," +
		"attacker_level SMALLINT NOT NULL DEFAULT 0," +
		"attacker_cp DOUBLE NOT NULL DEFAULT 0," +
		"attacker_max_cp DOUBLE NOT NULL DEFAULT 0," +
		"attacker_hp DOUBLE NOT NULL DEFAULT 0," +
		"attacker_max_hp DOUBLE NOT NULL DEFAULT 0," +
		"attacker_mp DOUBLE NOT NULL DEFAULT 0," +
		"attacker_max_mp DOUBLE NOT NULL DEFAULT 0," +
		"target_object_id INT NOT NULL DEFAULT 0," +
		"target_name VARCHAR(45) NOT NULL DEFAULT ''," +
		"target_kind VARCHAR(12) NOT NULL DEFAULT ''," +
		"target_template_id INT NOT NULL DEFAULT 0," +
		"target_class_id INT NOT NULL DEFAULT -1," +
		"target_level SMALLINT NOT NULL DEFAULT 0," +
		"target_cp DOUBLE NOT NULL DEFAULT 0," +
		"target_max_cp DOUBLE NOT NULL DEFAULT 0," +
		"target_hp DOUBLE NOT NULL DEFAULT 0," +
		"target_max_hp DOUBLE NOT NULL DEFAULT 0," +
		"target_mp DOUBLE NOT NULL DEFAULT 0," +
		"target_max_mp DOUBLE NOT NULL DEFAULT 0," +
		"skill_id INT NOT NULL DEFAULT 0," +
		"skill_level INT NOT NULL DEFAULT 0," +
		"skill_name VARCHAR(80) NOT NULL DEFAULT ''," +
		"damage DOUBLE NOT NULL DEFAULT 0," +
		"critical TINYINT(1) NOT NULL DEFAULT 0," +
		"damage_over_time TINYINT(1) NOT NULL DEFAULT 0," +
		"target_dead TINYINT(1) NOT NULL DEFAULT 0," +
		"world_x INT NOT NULL DEFAULT 0," +
		"world_y INT NOT NULL DEFAULT 0," +
		"world_z INT NOT NULL DEFAULT 0," +
		"PRIMARY KEY (event_id)," +
		"KEY idx_lab_events_time (occurred_ms)," +
		"KEY idx_lab_events_attacker (attacker_object_id, occurred_ms)," +
		"KEY idx_lab_events_target (target_object_id, occurred_ms)," +
		"KEY idx_lab_events_type (event_type, occurred_ms)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String CREATE_STATS_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_creature_stats (" +
		"template_id INT NOT NULL," +
		"object_id INT NOT NULL DEFAULT 0," +
		"name VARCHAR(45) NOT NULL DEFAULT ''," +
		"observed_ms BIGINT UNSIGNED NOT NULL," +
		"level SMALLINT NOT NULL DEFAULT 0," +
		"current_cp DOUBLE NOT NULL DEFAULT 0,max_cp DOUBLE NOT NULL DEFAULT 0," +
		"current_hp DOUBLE NOT NULL DEFAULT 0,max_hp DOUBLE NOT NULL DEFAULT 0," +
		"current_mp DOUBLE NOT NULL DEFAULT 0,max_mp DOUBLE NOT NULL DEFAULT 0," +
		"p_atk DOUBLE NOT NULL DEFAULT 0,m_atk DOUBLE NOT NULL DEFAULT 0," +
		"p_def DOUBLE NOT NULL DEFAULT 0,m_def DOUBLE NOT NULL DEFAULT 0," +
		"accuracy INT NOT NULL DEFAULT 0,evasion INT NOT NULL DEFAULT 0," +
		"p_critical INT NOT NULL DEFAULT 0,m_critical INT NOT NULL DEFAULT 0," +
		"critical_multiplier DOUBLE NOT NULL DEFAULT 2,critical_add DOUBLE NOT NULL DEFAULT 0," +
		"p_atk_speed DOUBLE NOT NULL DEFAULT 0,m_atk_speed INT NOT NULL DEFAULT 0," +
		"run_speed DOUBLE NOT NULL DEFAULT 0,walk_speed DOUBLE NOT NULL DEFAULT 0,attack_range INT NOT NULL DEFAULT 0," +
		"stat_str INT NOT NULL DEFAULT 0,stat_dex INT NOT NULL DEFAULT 0,stat_con INT NOT NULL DEFAULT 0," +
		"stat_int INT NOT NULL DEFAULT 0,stat_wit INT NOT NULL DEFAULT 0,stat_men INT NOT NULL DEFAULT 0," +
		"PRIMARY KEY (template_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String CREATE_PLAYER_STATS_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_player_stats (" +
		"char_id INT NOT NULL," +
		"object_id INT NOT NULL DEFAULT 0," +
		"class_id INT NOT NULL DEFAULT -1," +
		"name VARCHAR(45) NOT NULL DEFAULT ''," +
		"observed_ms BIGINT UNSIGNED NOT NULL," +
		"level SMALLINT NOT NULL DEFAULT 0," +
		"current_cp DOUBLE NOT NULL DEFAULT 0,max_cp DOUBLE NOT NULL DEFAULT 0," +
		"current_hp DOUBLE NOT NULL DEFAULT 0,max_hp DOUBLE NOT NULL DEFAULT 0," +
		"current_mp DOUBLE NOT NULL DEFAULT 0,max_mp DOUBLE NOT NULL DEFAULT 0," +
		"p_atk DOUBLE NOT NULL DEFAULT 0,m_atk DOUBLE NOT NULL DEFAULT 0," +
		"p_def DOUBLE NOT NULL DEFAULT 0,m_def DOUBLE NOT NULL DEFAULT 0," +
		"accuracy INT NOT NULL DEFAULT 0,evasion INT NOT NULL DEFAULT 0," +
		"p_critical INT NOT NULL DEFAULT 0,m_critical INT NOT NULL DEFAULT 0," +
		"critical_multiplier DOUBLE NOT NULL DEFAULT 2,critical_add DOUBLE NOT NULL DEFAULT 0," +
		"p_atk_speed DOUBLE NOT NULL DEFAULT 0,m_atk_speed INT NOT NULL DEFAULT 0," +
		"run_speed DOUBLE NOT NULL DEFAULT 0,walk_speed DOUBLE NOT NULL DEFAULT 0,attack_range INT NOT NULL DEFAULT 0," +
		"stat_str INT NOT NULL DEFAULT 0,stat_dex INT NOT NULL DEFAULT 0,stat_con INT NOT NULL DEFAULT 0," +
		"stat_int INT NOT NULL DEFAULT 0,stat_wit INT NOT NULL DEFAULT 0,stat_men INT NOT NULL DEFAULT 0," +
		"PRIMARY KEY (char_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String CREATE_PLAYER_PROFILE_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_player_stat_profiles (" +
		"char_id INT NOT NULL,name VARCHAR(45) NOT NULL DEFAULT '',observed_ms BIGINT UNSIGNED NOT NULL," +
		"race_id SMALLINT NOT NULL DEFAULT -1,race_name VARCHAR(20) NOT NULL DEFAULT '',base_class_id INT NOT NULL DEFAULT -1," +
		"class_index SMALLINT NOT NULL DEFAULT 0,class_id INT NOT NULL DEFAULT -1," +
		"sub1_class_id INT NOT NULL DEFAULT -1,sub2_class_id INT NOT NULL DEFAULT -1,sub3_class_id INT NOT NULL DEFAULT -1," +
		"level SMALLINT NOT NULL DEFAULT 0,equipment_key VARCHAR(1000) NOT NULL DEFAULT '',effect_key TEXT NOT NULL," +
		"equipped_count SMALLINT NOT NULL DEFAULT 0,effect_count SMALLINT NOT NULL DEFAULT 0,skill_count SMALLINT NOT NULL DEFAULT 0," +
		"profile_key CHAR(64) NOT NULL," +
		"current_cp DOUBLE NOT NULL DEFAULT 0,max_cp DOUBLE NOT NULL DEFAULT 0," +
		"current_hp DOUBLE NOT NULL DEFAULT 0,max_hp DOUBLE NOT NULL DEFAULT 0," +
		"current_mp DOUBLE NOT NULL DEFAULT 0,max_mp DOUBLE NOT NULL DEFAULT 0," +
		"p_atk DOUBLE NOT NULL DEFAULT 0,m_atk DOUBLE NOT NULL DEFAULT 0,p_def DOUBLE NOT NULL DEFAULT 0,m_def DOUBLE NOT NULL DEFAULT 0," +
		"accuracy INT NOT NULL DEFAULT 0,evasion INT NOT NULL DEFAULT 0,p_critical INT NOT NULL DEFAULT 0,m_critical INT NOT NULL DEFAULT 0," +
		"critical_multiplier DOUBLE NOT NULL DEFAULT 2,critical_add DOUBLE NOT NULL DEFAULT 0," +
		"p_atk_speed DOUBLE NOT NULL DEFAULT 0,m_atk_speed INT NOT NULL DEFAULT 0," +
		"run_speed DOUBLE NOT NULL DEFAULT 0,walk_speed DOUBLE NOT NULL DEFAULT 0,attack_range INT NOT NULL DEFAULT 0," +
		"stat_str INT NOT NULL DEFAULT 0,stat_dex INT NOT NULL DEFAULT 0,stat_con INT NOT NULL DEFAULT 0," +
		"stat_int INT NOT NULL DEFAULT 0,stat_wit INT NOT NULL DEFAULT 0,stat_men INT NOT NULL DEFAULT 0," +
		"PRIMARY KEY (char_id,profile_key)," +
		"KEY idx_lab_profile_class (race_id,class_id,class_index),KEY idx_lab_profile_time (observed_ms)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String CREATE_PAIR_PROFILE_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_class_pair_profiles (" +
		"pair_a_id INT NOT NULL,pair_b_id INT NOT NULL,main_class_id INT NOT NULL,sub_class_id INT NOT NULL," +
		"active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL,char_id INT NOT NULL,char_name VARCHAR(45) NOT NULL DEFAULT ''," +
		"observed_ms BIGINT UNSIGNED NOT NULL,race_id SMALLINT NOT NULL DEFAULT -1,race_name VARCHAR(20) NOT NULL DEFAULT ''," +
		"level SMALLINT NOT NULL DEFAULT 0,equipped_count SMALLINT NOT NULL DEFAULT 0,effect_count SMALLINT NOT NULL DEFAULT 0," +
		"skill_count SMALLINT NOT NULL DEFAULT 0,passive_skill_count SMALLINT NOT NULL DEFAULT 0,active_skill_count SMALLINT NOT NULL DEFAULT 0," +
		"shared_skill_id_count SMALLINT NOT NULL DEFAULT 0,mastery_collision_count SMALLINT NOT NULL DEFAULT 0,expected_skill_count SMALLINT NOT NULL DEFAULT 0," +
		"skill_hash CHAR(64) NOT NULL,skill_key TEXT NOT NULL," +
		"max_cp DOUBLE NOT NULL DEFAULT 0,max_hp DOUBLE NOT NULL DEFAULT 0,max_mp DOUBLE NOT NULL DEFAULT 0," +
		"p_atk DOUBLE NOT NULL DEFAULT 0,m_atk DOUBLE NOT NULL DEFAULT 0,p_def DOUBLE NOT NULL DEFAULT 0,m_def DOUBLE NOT NULL DEFAULT 0," +
		"accuracy INT NOT NULL DEFAULT 0,evasion INT NOT NULL DEFAULT 0,p_critical INT NOT NULL DEFAULT 0,m_critical INT NOT NULL DEFAULT 0," +
		"p_atk_speed DOUBLE NOT NULL DEFAULT 0,m_atk_speed INT NOT NULL DEFAULT 0,run_speed DOUBLE NOT NULL DEFAULT 0,attack_range INT NOT NULL DEFAULT 0," +
		"stat_str INT NOT NULL DEFAULT 0,stat_dex INT NOT NULL DEFAULT 0,stat_con INT NOT NULL DEFAULT 0," +
		"stat_int INT NOT NULL DEFAULT 0,stat_wit INT NOT NULL DEFAULT 0,stat_men INT NOT NULL DEFAULT 0," +
		"PRIMARY KEY (pair_a_id,pair_b_id,active_class_id)," +
		"KEY idx_lab_pair_active (active_class_id),KEY idx_lab_pair_time (observed_ms)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String CREATE_FOUR_CLASS_PROFILE_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_four_class_profiles (" +
		"main_class_id INT NOT NULL,sub1_class_id INT NOT NULL,sub2_class_id INT NOT NULL,sub3_class_id INT NOT NULL," +
		"active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL,char_id INT NOT NULL,char_name VARCHAR(45) NOT NULL DEFAULT ''," +
		"selection_bucket VARCHAR(16) NOT NULL DEFAULT '',observed_ms BIGINT UNSIGNED NOT NULL," +
		"race_id SMALLINT NOT NULL DEFAULT -1,race_name VARCHAR(20) NOT NULL DEFAULT '',level SMALLINT NOT NULL DEFAULT 0," +
		"equipped_count SMALLINT NOT NULL DEFAULT 0,effect_count SMALLINT NOT NULL DEFAULT 0," +
		"skill_count SMALLINT NOT NULL DEFAULT 0,passive_skill_count SMALLINT NOT NULL DEFAULT 0,active_skill_count SMALLINT NOT NULL DEFAULT 0," +
		"expected_skill_count SMALLINT NOT NULL DEFAULT 0,skill_hash CHAR(64) NOT NULL,skill_key MEDIUMTEXT NOT NULL," +
		"max_cp DOUBLE NOT NULL DEFAULT 0,max_hp DOUBLE NOT NULL DEFAULT 0,max_mp DOUBLE NOT NULL DEFAULT 0," +
		"p_atk DOUBLE NOT NULL DEFAULT 0,m_atk DOUBLE NOT NULL DEFAULT 0,p_def DOUBLE NOT NULL DEFAULT 0,m_def DOUBLE NOT NULL DEFAULT 0," +
		"accuracy INT NOT NULL DEFAULT 0,evasion INT NOT NULL DEFAULT 0,p_critical INT NOT NULL DEFAULT 0,m_critical INT NOT NULL DEFAULT 0," +
		"p_atk_speed DOUBLE NOT NULL DEFAULT 0,m_atk_speed INT NOT NULL DEFAULT 0,run_speed DOUBLE NOT NULL DEFAULT 0,attack_range INT NOT NULL DEFAULT 0," +
		"stat_str INT NOT NULL DEFAULT 0,stat_dex INT NOT NULL DEFAULT 0,stat_con INT NOT NULL DEFAULT 0," +
		"stat_int INT NOT NULL DEFAULT 0,stat_wit INT NOT NULL DEFAULT 0,stat_men INT NOT NULL DEFAULT 0," +
		"PRIMARY KEY (main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,active_class_id)," +
		"KEY idx_lab_four_profile_active (active_class_id),KEY idx_lab_four_profile_time (observed_ms),KEY idx_lab_four_profile_bucket (selection_bucket)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String CREATE_BENCHMARK_RUN_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_combat_benchmark_runs (" +
		"case_id VARCHAR(48) NOT NULL,run_number SMALLINT NOT NULL,executed_ms BIGINT UNSIGNED NOT NULL," +
		"engine_mode VARCHAR(32) NOT NULL DEFAULT 'CORE_ACCELERATED',duration_seconds SMALLINT NOT NULL," +
		"char_id INT NOT NULL,char_name VARCHAR(45) NOT NULL,active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL," +
		"opponent_id INT NOT NULL DEFAULT 0,opponent_name VARCHAR(45) NOT NULL DEFAULT '',equipment_kit VARCHAR(32) NOT NULL,weapon_id INT NOT NULL," +
		"rotation VARCHAR(512) NOT NULL DEFAULT '',actions INT NOT NULL DEFAULT 0,hits INT NOT NULL DEFAULT 0,casts INT NOT NULL DEFAULT 0," +
		"critical_count INT NOT NULL DEFAULT 0,miss_count INT NOT NULL DEFAULT 0,soulshots_used INT NOT NULL DEFAULT 0,bss_used INT NOT NULL DEFAULT 0," +
		"damage_dealt DOUBLE NOT NULL DEFAULT 0,owner_damage DOUBLE NOT NULL DEFAULT 0,summon_damage DOUBLE NOT NULL DEFAULT 0," +
		"damage_received DOUBLE NOT NULL DEFAULT 0,effective_heal DOUBLE NOT NULL DEFAULT 0,overheal DOUBLE NOT NULL DEFAULT 0,mp_used DOUBLE NOT NULL DEFAULT 0," +
		"time_alive DOUBLE NOT NULL DEFAULT 0,hp_cp_remaining DOUBLE NOT NULL DEFAULT 0,control_time DOUBLE NOT NULL DEFAULT 0,summon_uptime DOUBLE NOT NULL DEFAULT 0," +
		"notes VARCHAR(512) NOT NULL DEFAULT '',PRIMARY KEY(case_id,run_number),KEY idx_lab_benchmark_run_class(active_class_id)," +
		"KEY idx_lab_benchmark_run_time(executed_ms)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String INSERT_BENCHMARK_RUN =
		"INSERT INTO lab_combat_benchmark_runs (case_id,run_number,executed_ms,engine_mode,duration_seconds,char_id,char_name," +
		"active_class_id,active_class_index,opponent_id,opponent_name,equipment_kit,weapon_id,rotation,actions,hits,casts,critical_count,miss_count," +
		"soulshots_used,bss_used,damage_dealt,owner_damage,summon_damage,damage_received,effective_heal,overheal,mp_used,time_alive,hp_cp_remaining,control_time,summon_uptime,notes) " +
		"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE executed_ms=VALUES(executed_ms)," +
		"engine_mode=VALUES(engine_mode),duration_seconds=VALUES(duration_seconds),char_id=VALUES(char_id),char_name=VALUES(char_name)," +
		"active_class_id=VALUES(active_class_id),active_class_index=VALUES(active_class_index),opponent_id=VALUES(opponent_id),opponent_name=VALUES(opponent_name)," +
		"equipment_kit=VALUES(equipment_kit),weapon_id=VALUES(weapon_id),rotation=VALUES(rotation),actions=VALUES(actions),hits=VALUES(hits),casts=VALUES(casts)," +
		"critical_count=VALUES(critical_count),miss_count=VALUES(miss_count),soulshots_used=VALUES(soulshots_used),bss_used=VALUES(bss_used)," +
		"damage_dealt=VALUES(damage_dealt),owner_damage=VALUES(owner_damage),summon_damage=VALUES(summon_damage),damage_received=VALUES(damage_received)," +
		"effective_heal=VALUES(effective_heal),overheal=VALUES(overheal),mp_used=VALUES(mp_used),time_alive=VALUES(time_alive)," +
		"hp_cp_remaining=VALUES(hp_cp_remaining),control_time=VALUES(control_time),summon_uptime=VALUES(summon_uptime),notes=VALUES(notes)";

	private static final String CREATE_NYX_CALIBRATION_RUN_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_nyx_calibration_runs (" +
		"source_case_id VARCHAR(48) NOT NULL,scale_percent SMALLINT NOT NULL,run_number SMALLINT NOT NULL,executed_ms BIGINT UNSIGNED NOT NULL," +
		"engine_mode VARCHAR(32) NOT NULL DEFAULT 'CORE_ACCELERATED_SCALED',finalist_rank SMALLINT NOT NULL,category VARCHAR(16) NOT NULL," +
		"char_id INT NOT NULL,char_name VARCHAR(45) NOT NULL,active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL," +
		"opponent_id INT NOT NULL,opponent_name VARCHAR(45) NOT NULL,equipment_kit VARCHAR(32) NOT NULL,weapon_id INT NOT NULL," +
		"duration_seconds SMALLINT NOT NULL,rotation VARCHAR(512) NOT NULL DEFAULT '',actions INT NOT NULL DEFAULT 0,hits INT NOT NULL DEFAULT 0," +
		"casts INT NOT NULL DEFAULT 0,critical_count INT NOT NULL DEFAULT 0,miss_count INT NOT NULL DEFAULT 0,bss_used INT NOT NULL DEFAULT 0," +
		"damage_received DOUBLE NOT NULL DEFAULT 0,time_alive DOUBLE NOT NULL DEFAULT 0,hp_cp_remaining DOUBLE NOT NULL DEFAULT 0," +
		"control_time DOUBLE NOT NULL DEFAULT 0,notes VARCHAR(512) NOT NULL DEFAULT ''," +
		"PRIMARY KEY(source_case_id,scale_percent,run_number),KEY idx_lab_nyx_calibration_scale(scale_percent)," +
		"KEY idx_lab_nyx_calibration_category(category,scale_percent)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String INSERT_NYX_CALIBRATION_RUN =
		"INSERT INTO lab_nyx_calibration_runs (source_case_id,scale_percent,run_number,executed_ms,engine_mode,finalist_rank,category," +
		"char_id,char_name,active_class_id,active_class_index,opponent_id,opponent_name,equipment_kit,weapon_id,duration_seconds," +
		"rotation,actions,hits,casts,critical_count,miss_count,bss_used,damage_received,time_alive,hp_cp_remaining,control_time,notes) " +
		"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON DUPLICATE KEY UPDATE executed_ms=VALUES(executed_ms)," +
		"engine_mode=VALUES(engine_mode),char_id=VALUES(char_id),char_name=VALUES(char_name),active_class_id=VALUES(active_class_id)," +
		"active_class_index=VALUES(active_class_index),rotation=VALUES(rotation),actions=VALUES(actions),hits=VALUES(hits),casts=VALUES(casts)," +
		"critical_count=VALUES(critical_count),miss_count=VALUES(miss_count),bss_used=VALUES(bss_used),damage_received=VALUES(damage_received)," +
		"time_alive=VALUES(time_alive),hp_cp_remaining=VALUES(hp_cp_remaining),control_time=VALUES(control_time),notes=VALUES(notes)";

	private static final String CREATE_MAGIC_PROGRESSION_RUN_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_magic_progression_runs (" +
		"stage_index SMALLINT NOT NULL,run_number SMALLINT NOT NULL,executed_ms BIGINT UNSIGNED NOT NULL," +
		"engine_mode VARCHAR(32) NOT NULL DEFAULT 'CORE_ACCELERATED',stage_label VARCHAR(80) NOT NULL," +
		"main_class_id INT NOT NULL,sub1_class_id INT NOT NULL DEFAULT -1,sub2_class_id INT NOT NULL DEFAULT -1,sub3_class_id INT NOT NULL DEFAULT -1," +
		"class_count SMALLINT NOT NULL,char_id INT NOT NULL,char_name VARCHAR(45) NOT NULL,active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL,level SMALLINT NOT NULL," +
		"skill_count SMALLINT NOT NULL,passive_skill_count SMALLINT NOT NULL,active_skill_count SMALLINT NOT NULL," +
		"equipment_kit VARCHAR(32) NOT NULL,weapon_id INT NOT NULL,weapon_name VARCHAR(80) NOT NULL," +
		"p_atk DOUBLE NOT NULL,m_atk DOUBLE NOT NULL,p_def DOUBLE NOT NULL,m_def DOUBLE NOT NULL,p_atk_speed DOUBLE NOT NULL,m_atk_speed DOUBLE NOT NULL," +
		"max_hp DOUBLE NOT NULL,max_cp DOUBLE NOT NULL,max_mp DOUBLE NOT NULL,duration_seconds SMALLINT NOT NULL," +
		"rotation VARCHAR(512) NOT NULL DEFAULT '',actions INT NOT NULL DEFAULT 0,hits INT NOT NULL DEFAULT 0,casts INT NOT NULL DEFAULT 0," +
		"critical_count INT NOT NULL DEFAULT 0,miss_count INT NOT NULL DEFAULT 0,bss_used INT NOT NULL DEFAULT 0," +
		"damage_dealt DOUBLE NOT NULL DEFAULT 0,dps DOUBLE NOT NULL DEFAULT 0,mp_used DOUBLE NOT NULL DEFAULT 0,notes VARCHAR(512) NOT NULL DEFAULT ''," +
		"PRIMARY KEY(stage_index,run_number),KEY idx_lab_magic_progression_time(executed_ms)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String INSERT_MAGIC_PROGRESSION_RUN =
		"INSERT INTO lab_magic_progression_runs (stage_index,run_number,executed_ms,engine_mode,stage_label," +
		"main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,class_count,char_id,char_name,active_class_id,active_class_index,level," +
		"skill_count,passive_skill_count,active_skill_count,equipment_kit,weapon_id,weapon_name," +
		"p_atk,m_atk,p_def,m_def,p_atk_speed,m_atk_speed,max_hp,max_cp,max_mp,duration_seconds," +
		"rotation,actions,hits,casts,critical_count,miss_count,bss_used,damage_dealt,dps,mp_used,notes) " +
		"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE executed_ms=VALUES(executed_ms),engine_mode=VALUES(engine_mode),stage_label=VALUES(stage_label)," +
		"sub1_class_id=VALUES(sub1_class_id),sub2_class_id=VALUES(sub2_class_id),sub3_class_id=VALUES(sub3_class_id),class_count=VALUES(class_count)," +
		"skill_count=VALUES(skill_count),passive_skill_count=VALUES(passive_skill_count),active_skill_count=VALUES(active_skill_count)," +
		"p_atk=VALUES(p_atk),m_atk=VALUES(m_atk),p_def=VALUES(p_def),m_def=VALUES(m_def),p_atk_speed=VALUES(p_atk_speed),m_atk_speed=VALUES(m_atk_speed)," +
		"max_hp=VALUES(max_hp),max_cp=VALUES(max_cp),max_mp=VALUES(max_mp),rotation=VALUES(rotation),actions=VALUES(actions),hits=VALUES(hits)," +
		"casts=VALUES(casts),critical_count=VALUES(critical_count),miss_count=VALUES(miss_count),bss_used=VALUES(bss_used)," +
		"damage_dealt=VALUES(damage_dealt),dps=VALUES(dps),mp_used=VALUES(mp_used),notes=VALUES(notes)";

	private static final String CREATE_MAGIC_COMPARISON_RUN_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_magic_comparison_runs (" +
		"stage_index SMALLINT NOT NULL,protocol VARCHAR(24) NOT NULL,run_number SMALLINT NOT NULL,executed_ms BIGINT UNSIGNED NOT NULL," +
		"engine_mode VARCHAR(32) NOT NULL DEFAULT 'CORE_ACCELERATED',stage_label VARCHAR(80) NOT NULL," +
		"main_class_id INT NOT NULL,sub1_class_id INT NOT NULL DEFAULT -1,sub2_class_id INT NOT NULL DEFAULT -1,sub3_class_id INT NOT NULL DEFAULT -1," +
		"class_count SMALLINT NOT NULL,char_id INT NOT NULL,char_name VARCHAR(45) NOT NULL,active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL,level SMALLINT NOT NULL," +
		"skill_count SMALLINT NOT NULL,passive_skill_count SMALLINT NOT NULL,active_skill_count SMALLINT NOT NULL," +
		"equipment_kit VARCHAR(32) NOT NULL,weapon_id INT NOT NULL,weapon_name VARCHAR(80) NOT NULL," +
		"m_atk DOUBLE NOT NULL,m_atk_speed DOUBLE NOT NULL,max_mp DOUBLE NOT NULL,duration_seconds SMALLINT NOT NULL," +
		"selected_skill_id INT NOT NULL,selected_skill_level INT NOT NULL,selected_skill_name VARCHAR(80) NOT NULL," +
		"selected_skill_power DOUBLE NOT NULL,selected_skill_cycle_ms INT NOT NULL,rotation VARCHAR(512) NOT NULL DEFAULT ''," +
		"actions INT NOT NULL DEFAULT 0,hits INT NOT NULL DEFAULT 0,casts INT NOT NULL DEFAULT 0,critical_count INT NOT NULL DEFAULT 0," +
		"miss_count INT NOT NULL DEFAULT 0,bss_used INT NOT NULL DEFAULT 0,damage_dealt DOUBLE NOT NULL DEFAULT 0,dps DOUBLE NOT NULL DEFAULT 0," +
		"mp_used DOUBLE NOT NULL DEFAULT 0,notes VARCHAR(512) NOT NULL DEFAULT ''," +
		"PRIMARY KEY(stage_index,protocol,run_number),KEY idx_lab_magic_comparison_time(executed_ms)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String INSERT_MAGIC_COMPARISON_RUN =
		"INSERT INTO lab_magic_comparison_runs (stage_index,protocol,run_number,executed_ms,engine_mode,stage_label," +
		"main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,class_count,char_id,char_name,active_class_id,active_class_index,level," +
		"skill_count,passive_skill_count,active_skill_count,equipment_kit,weapon_id,weapon_name,m_atk,m_atk_speed,max_mp,duration_seconds," +
		"selected_skill_id,selected_skill_level,selected_skill_name,selected_skill_power,selected_skill_cycle_ms,rotation," +
		"actions,hits,casts,critical_count,miss_count,bss_used,damage_dealt,dps,mp_used,notes) " +
		"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE executed_ms=VALUES(executed_ms),stage_label=VALUES(stage_label),class_count=VALUES(class_count)," +
		"skill_count=VALUES(skill_count),passive_skill_count=VALUES(passive_skill_count),active_skill_count=VALUES(active_skill_count)," +
		"m_atk=VALUES(m_atk),m_atk_speed=VALUES(m_atk_speed),max_mp=VALUES(max_mp),selected_skill_id=VALUES(selected_skill_id)," +
		"selected_skill_level=VALUES(selected_skill_level),selected_skill_name=VALUES(selected_skill_name)," +
		"selected_skill_power=VALUES(selected_skill_power),selected_skill_cycle_ms=VALUES(selected_skill_cycle_ms),rotation=VALUES(rotation)," +
		"actions=VALUES(actions),hits=VALUES(hits),casts=VALUES(casts),critical_count=VALUES(critical_count),miss_count=VALUES(miss_count)," +
		"bss_used=VALUES(bss_used),damage_dealt=VALUES(damage_dealt),dps=VALUES(dps),mp_used=VALUES(mp_used),notes=VALUES(notes)";

	private static final String CREATE_PHYSICAL_RACE_RUN_TABLE =
		"CREATE TABLE IF NOT EXISTS lab_physical_race_runs (" +
		"anchor_root_class_id INT NOT NULL,race_id SMALLINT NOT NULL,race_name VARCHAR(20) NOT NULL,stage_index SMALLINT NOT NULL," +
		"protocol VARCHAR(24) NOT NULL,run_number SMALLINT NOT NULL,executed_ms BIGINT UNSIGNED NOT NULL," +
		"engine_mode VARCHAR(32) NOT NULL DEFAULT 'CORE_ACCELERATED',stage_label VARCHAR(80) NOT NULL," +
		"main_class_id INT NOT NULL,sub1_class_id INT NOT NULL DEFAULT -1,sub2_class_id INT NOT NULL DEFAULT -1,sub3_class_id INT NOT NULL DEFAULT -1," +
		"class_count SMALLINT NOT NULL,char_id INT NOT NULL,char_name VARCHAR(45) NOT NULL,active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL,level SMALLINT NOT NULL," +
		"skill_count SMALLINT NOT NULL,passive_skill_count SMALLINT NOT NULL,active_skill_count SMALLINT NOT NULL," +
		"equipment_kit VARCHAR(32) NOT NULL,weapon_id INT NOT NULL,weapon_name VARCHAR(80) NOT NULL," +
		"p_atk DOUBLE NOT NULL,p_atk_speed DOUBLE NOT NULL,p_critical DOUBLE NOT NULL,accuracy INT NOT NULL," +
		"max_hp DOUBLE NOT NULL,max_cp DOUBLE NOT NULL,max_mp DOUBLE NOT NULL,stat_str SMALLINT NOT NULL,stat_dex SMALLINT NOT NULL,stat_con SMALLINT NOT NULL," +
		"duration_seconds SMALLINT NOT NULL,selected_skill_id INT NOT NULL,selected_skill_level INT NOT NULL,selected_skill_name VARCHAR(80) NOT NULL," +
		"selected_skill_power DOUBLE NOT NULL,selected_skill_cycle_ms INT NOT NULL,rotation VARCHAR(512) NOT NULL DEFAULT ''," +
		"actions INT NOT NULL DEFAULT 0,hits INT NOT NULL DEFAULT 0,casts INT NOT NULL DEFAULT 0,critical_count INT NOT NULL DEFAULT 0," +
		"miss_count INT NOT NULL DEFAULT 0,soulshots_used INT NOT NULL DEFAULT 0,damage_dealt DOUBLE NOT NULL DEFAULT 0,dps DOUBLE NOT NULL DEFAULT 0," +
		"mp_used DOUBLE NOT NULL DEFAULT 0,notes VARCHAR(512) NOT NULL DEFAULT ''," +
		"PRIMARY KEY(anchor_root_class_id,stage_index,protocol,run_number),KEY idx_lab_physical_race(race_id,stage_index,protocol)" +
		") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";

	private static final String INSERT_PHYSICAL_RACE_RUN =
		"INSERT INTO lab_physical_race_runs (anchor_root_class_id,race_id,race_name,stage_index,protocol,run_number,executed_ms,engine_mode,stage_label," +
		"main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,class_count,char_id,char_name,active_class_id,active_class_index,level," +
		"skill_count,passive_skill_count,active_skill_count,equipment_kit,weapon_id,weapon_name,p_atk,p_atk_speed,p_critical,accuracy," +
		"max_hp,max_cp,max_mp,stat_str,stat_dex,stat_con,duration_seconds,selected_skill_id,selected_skill_level,selected_skill_name," +
		"selected_skill_power,selected_skill_cycle_ms,rotation,actions,hits,casts,critical_count,miss_count,soulshots_used,damage_dealt,dps,mp_used,notes) " +
		"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE executed_ms=VALUES(executed_ms),race_id=VALUES(race_id),race_name=VALUES(race_name),stage_label=VALUES(stage_label)," +
		"skill_count=VALUES(skill_count),passive_skill_count=VALUES(passive_skill_count),active_skill_count=VALUES(active_skill_count)," +
		"p_atk=VALUES(p_atk),p_atk_speed=VALUES(p_atk_speed),p_critical=VALUES(p_critical),accuracy=VALUES(accuracy)," +
		"max_hp=VALUES(max_hp),max_cp=VALUES(max_cp),max_mp=VALUES(max_mp),stat_str=VALUES(stat_str),stat_dex=VALUES(stat_dex),stat_con=VALUES(stat_con)," +
		"selected_skill_id=VALUES(selected_skill_id),selected_skill_level=VALUES(selected_skill_level),selected_skill_name=VALUES(selected_skill_name)," +
		"selected_skill_power=VALUES(selected_skill_power),selected_skill_cycle_ms=VALUES(selected_skill_cycle_ms),rotation=VALUES(rotation)," +
		"actions=VALUES(actions),hits=VALUES(hits),casts=VALUES(casts),critical_count=VALUES(critical_count),miss_count=VALUES(miss_count)," +
		"soulshots_used=VALUES(soulshots_used),damage_dealt=VALUES(damage_dealt),dps=VALUES(dps),mp_used=VALUES(mp_used),notes=VALUES(notes)";

	private static final String INSERT_EVENT =
		"INSERT INTO lab_combat_events (occurred_ms,event_type," +
		"attacker_object_id,attacker_name,attacker_kind,attacker_template_id,attacker_class_id,attacker_level," +
		"attacker_cp,attacker_max_cp,attacker_hp,attacker_max_hp,attacker_mp,attacker_max_mp," +
		"target_object_id,target_name,target_kind,target_template_id,target_class_id,target_level," +
		"target_cp,target_max_cp,target_hp,target_max_hp,target_mp,target_max_mp," +
		"skill_id,skill_level,skill_name,damage,critical,damage_over_time,target_dead,world_x,world_y,world_z) " +
		"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";

	private static final String UPSERT_STATS =
		"INSERT INTO lab_creature_stats (template_id,object_id,name,observed_ms,level," +
		"current_cp,max_cp,current_hp,max_hp,current_mp,max_mp,p_atk,m_atk,p_def,m_def,accuracy,evasion," +
		"p_critical,m_critical,critical_multiplier,critical_add,p_atk_speed,m_atk_speed,run_speed,walk_speed,attack_range," +
		"stat_str,stat_dex,stat_con,stat_int,stat_wit,stat_men) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE object_id=VALUES(object_id),name=VALUES(name),observed_ms=VALUES(observed_ms),level=VALUES(level)," +
		"current_cp=VALUES(current_cp),max_cp=VALUES(max_cp),current_hp=VALUES(current_hp),max_hp=VALUES(max_hp)," +
		"current_mp=VALUES(current_mp),max_mp=VALUES(max_mp),p_atk=VALUES(p_atk),m_atk=VALUES(m_atk)," +
		"p_def=VALUES(p_def),m_def=VALUES(m_def),accuracy=VALUES(accuracy),evasion=VALUES(evasion)," +
		"p_critical=VALUES(p_critical),m_critical=VALUES(m_critical),critical_multiplier=VALUES(critical_multiplier)," +
		"critical_add=VALUES(critical_add),p_atk_speed=VALUES(p_atk_speed),m_atk_speed=VALUES(m_atk_speed)," +
		"run_speed=VALUES(run_speed),walk_speed=VALUES(walk_speed),attack_range=VALUES(attack_range)," +
		"stat_str=VALUES(stat_str),stat_dex=VALUES(stat_dex),stat_con=VALUES(stat_con)," +
		"stat_int=VALUES(stat_int),stat_wit=VALUES(stat_wit),stat_men=VALUES(stat_men)";

	private static final String UPSERT_PLAYER_STATS =
		"INSERT INTO lab_player_stats (char_id,object_id,class_id,name,observed_ms,level," +
		"current_cp,max_cp,current_hp,max_hp,current_mp,max_mp,p_atk,m_atk,p_def,m_def,accuracy,evasion," +
		"p_critical,m_critical,critical_multiplier,critical_add,p_atk_speed,m_atk_speed,run_speed,walk_speed,attack_range," +
		"stat_str,stat_dex,stat_con,stat_int,stat_wit,stat_men) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE object_id=VALUES(object_id),class_id=VALUES(class_id),name=VALUES(name)," +
		"observed_ms=VALUES(observed_ms),level=VALUES(level),current_cp=VALUES(current_cp),max_cp=VALUES(max_cp)," +
		"current_hp=VALUES(current_hp),max_hp=VALUES(max_hp),current_mp=VALUES(current_mp),max_mp=VALUES(max_mp)," +
		"p_atk=VALUES(p_atk),m_atk=VALUES(m_atk),p_def=VALUES(p_def),m_def=VALUES(m_def)," +
		"accuracy=VALUES(accuracy),evasion=VALUES(evasion),p_critical=VALUES(p_critical),m_critical=VALUES(m_critical)," +
		"critical_multiplier=VALUES(critical_multiplier),critical_add=VALUES(critical_add)," +
		"p_atk_speed=VALUES(p_atk_speed),m_atk_speed=VALUES(m_atk_speed),run_speed=VALUES(run_speed)," +
		"walk_speed=VALUES(walk_speed),attack_range=VALUES(attack_range),stat_str=VALUES(stat_str)," +
		"stat_dex=VALUES(stat_dex),stat_con=VALUES(stat_con),stat_int=VALUES(stat_int)," +
		"stat_wit=VALUES(stat_wit),stat_men=VALUES(stat_men)";

	private static final String UPSERT_PLAYER_PROFILE =
		"INSERT INTO lab_player_stat_profiles (char_id,name,observed_ms,race_id,race_name,base_class_id,class_index,class_id," +
		"sub1_class_id,sub2_class_id,sub3_class_id,level,equipment_key,effect_key,equipped_count,effect_count,skill_count,profile_key," +
		"current_cp,max_cp,current_hp,max_hp,current_mp,max_mp,p_atk,m_atk,p_def,m_def,accuracy,evasion,p_critical,m_critical," +
		"critical_multiplier,critical_add,p_atk_speed,m_atk_speed,run_speed,walk_speed,attack_range," +
		"stat_str,stat_dex,stat_con,stat_int,stat_wit,stat_men) " +
		"VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE name=VALUES(name),observed_ms=VALUES(observed_ms),race_id=VALUES(race_id),race_name=VALUES(race_name)," +
		"base_class_id=VALUES(base_class_id),class_index=VALUES(class_index),class_id=VALUES(class_id)," +
		"sub1_class_id=VALUES(sub1_class_id),sub2_class_id=VALUES(sub2_class_id),sub3_class_id=VALUES(sub3_class_id),level=VALUES(level)," +
		"equipment_key=VALUES(equipment_key),effect_key=VALUES(effect_key),equipped_count=VALUES(equipped_count)," +
		"effect_count=VALUES(effect_count),skill_count=VALUES(skill_count),current_cp=VALUES(current_cp),max_cp=VALUES(max_cp)," +
		"current_hp=VALUES(current_hp),max_hp=VALUES(max_hp),current_mp=VALUES(current_mp),max_mp=VALUES(max_mp)," +
		"p_atk=VALUES(p_atk),m_atk=VALUES(m_atk),p_def=VALUES(p_def),m_def=VALUES(m_def),accuracy=VALUES(accuracy),evasion=VALUES(evasion)," +
		"p_critical=VALUES(p_critical),m_critical=VALUES(m_critical),critical_multiplier=VALUES(critical_multiplier),critical_add=VALUES(critical_add)," +
		"p_atk_speed=VALUES(p_atk_speed),m_atk_speed=VALUES(m_atk_speed),run_speed=VALUES(run_speed),walk_speed=VALUES(walk_speed)," +
		"attack_range=VALUES(attack_range),stat_str=VALUES(stat_str),stat_dex=VALUES(stat_dex),stat_con=VALUES(stat_con)," +
		"stat_int=VALUES(stat_int),stat_wit=VALUES(stat_wit),stat_men=VALUES(stat_men)";

	private static final String UPSERT_PAIR_PROFILE =
		"INSERT INTO lab_class_pair_profiles (pair_a_id,pair_b_id,main_class_id,sub_class_id,active_class_id,active_class_index," +
		"char_id,char_name,observed_ms,race_id,race_name,level,equipped_count,effect_count,skill_count,passive_skill_count,active_skill_count," +
		"shared_skill_id_count,mastery_collision_count,expected_skill_count,skill_hash,skill_key,max_cp,max_hp,max_mp," +
		"p_atk,m_atk,p_def,m_def,accuracy,evasion,p_critical,m_critical,p_atk_speed,m_atk_speed,run_speed,attack_range," +
		"stat_str,stat_dex,stat_con,stat_int,stat_wit,stat_men) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE main_class_id=VALUES(main_class_id),sub_class_id=VALUES(sub_class_id),active_class_index=VALUES(active_class_index)," +
		"char_id=VALUES(char_id),char_name=VALUES(char_name),observed_ms=VALUES(observed_ms),race_id=VALUES(race_id),race_name=VALUES(race_name)," +
		"level=VALUES(level),equipped_count=VALUES(equipped_count),effect_count=VALUES(effect_count),skill_count=VALUES(skill_count)," +
		"passive_skill_count=VALUES(passive_skill_count),active_skill_count=VALUES(active_skill_count),shared_skill_id_count=VALUES(shared_skill_id_count)," +
		"mastery_collision_count=VALUES(mastery_collision_count),expected_skill_count=VALUES(expected_skill_count),skill_hash=VALUES(skill_hash),skill_key=VALUES(skill_key)," +
		"max_cp=VALUES(max_cp),max_hp=VALUES(max_hp),max_mp=VALUES(max_mp),p_atk=VALUES(p_atk),m_atk=VALUES(m_atk),p_def=VALUES(p_def),m_def=VALUES(m_def)," +
		"accuracy=VALUES(accuracy),evasion=VALUES(evasion),p_critical=VALUES(p_critical),m_critical=VALUES(m_critical)," +
		"p_atk_speed=VALUES(p_atk_speed),m_atk_speed=VALUES(m_atk_speed),run_speed=VALUES(run_speed),attack_range=VALUES(attack_range)," +
		"stat_str=VALUES(stat_str),stat_dex=VALUES(stat_dex),stat_con=VALUES(stat_con),stat_int=VALUES(stat_int),stat_wit=VALUES(stat_wit),stat_men=VALUES(stat_men)";

	private static final String UPSERT_FOUR_CLASS_PROFILE =
		"INSERT INTO lab_four_class_profiles (main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,active_class_id,active_class_index," +
		"char_id,char_name,selection_bucket,observed_ms,race_id,race_name,level,equipped_count,effect_count," +
		"skill_count,passive_skill_count,active_skill_count,expected_skill_count,skill_hash,skill_key,max_cp,max_hp,max_mp," +
		"p_atk,m_atk,p_def,m_def,accuracy,evasion,p_critical,m_critical,p_atk_speed,m_atk_speed,run_speed,attack_range," +
		"stat_str,stat_dex,stat_con,stat_int,stat_wit,stat_men) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) " +
		"ON DUPLICATE KEY UPDATE active_class_index=VALUES(active_class_index),char_id=VALUES(char_id),char_name=VALUES(char_name)," +
		"selection_bucket=VALUES(selection_bucket),observed_ms=VALUES(observed_ms),race_id=VALUES(race_id),race_name=VALUES(race_name)," +
		"level=VALUES(level),equipped_count=VALUES(equipped_count),effect_count=VALUES(effect_count),skill_count=VALUES(skill_count)," +
		"passive_skill_count=VALUES(passive_skill_count),active_skill_count=VALUES(active_skill_count),expected_skill_count=VALUES(expected_skill_count)," +
		"skill_hash=VALUES(skill_hash),skill_key=VALUES(skill_key),max_cp=VALUES(max_cp),max_hp=VALUES(max_hp),max_mp=VALUES(max_mp)," +
		"p_atk=VALUES(p_atk),m_atk=VALUES(m_atk),p_def=VALUES(p_def),m_def=VALUES(m_def),accuracy=VALUES(accuracy),evasion=VALUES(evasion)," +
		"p_critical=VALUES(p_critical),m_critical=VALUES(m_critical),p_atk_speed=VALUES(p_atk_speed),m_atk_speed=VALUES(m_atk_speed)," +
		"run_speed=VALUES(run_speed),attack_range=VALUES(attack_range),stat_str=VALUES(stat_str),stat_dex=VALUES(stat_dex)," +
		"stat_con=VALUES(stat_con),stat_int=VALUES(stat_int),stat_wit=VALUES(stat_wit),stat_men=VALUES(stat_men)";

	public LabTelemetry()
	{
		INSTANCE = this;
		createTable();
		Containers.Global().addListener(new ConsumerEventListener(Containers.Global(), EventType.ON_CREATURE_DAMAGE_DEALT, (OnCreatureDamageDealt event) -> onDamage(event), this));
		Containers.Global().addListener(new ConsumerEventListener(Containers.Global(), EventType.ON_CREATURE_ATTACK_AVOID, (OnCreatureAttackAvoid event) -> onAvoid(event), this));
		Containers.Global().addListener(new ConsumerEventListener(Containers.Global(), EventType.ON_CREATURE_SKILL_USE, (OnCreatureSkillUse event) -> onSkillUse(event), this));
		Containers.Global().addListener(new ConsumerEventListener(Containers.Global(), EventType.ON_CREATURE_DEATH, (OnCreatureDeath event) -> onDeath(event), this));
		Containers.Global().addListener(new ConsumerEventListener(Containers.Global(), EventType.ON_PLAYER_LOGIN, (OnPlayerLogin event) -> schedulePlayerProfile(event.getPlayer()), this));
		Containers.Global().addListener(new ConsumerEventListener(Containers.Global(), EventType.ON_PLAYER_PROFESSION_CHANGE, (OnPlayerProfessionChange event) -> schedulePlayerProfile(event.getPlayer()), this));
		LOGGER.info("Laboratorio L2: telemetria de combate activa.");
		ThreadPool.schedule(this::runCleanClassCoverage, 10000);
		ThreadPool.schedule(this::runPairCoverage, 20000);
		ThreadPool.schedule(this::runFourClassCoverage, 30000);
		ThreadPool.schedule(this::runCombatBenchmarks, 45000);
		ThreadPool.schedule(this::runNyxCalibration, 60000);
		ThreadPool.schedule(this::runMagicProgression, 75000);
		ThreadPool.schedule(this::runMagicComparison, 105000);
		ThreadPool.schedule(this::runPhysicalRaceBaseline, 135000);
	}

	/**
	 * Stores a profile synchronously. Used by controlled laboratory runners that
	 * load real Player objects without a game client.
	 * @param player the fully loaded player
	 * @return {@code true} when the profile was stored
	 */
	public static boolean captureProfileNow(Player player)
	{
		if ((INSTANCE == null) || (player == null))
		{
			return false;
		}
		final CreatureSnapshot snapshot = new CreatureSnapshot(player);
		try (Connection con = DatabaseFactory.getConnection())
		{
			INSTANCE.upsertPlayerProfile(con, snapshot);
			return true;
		}
		catch (SQLException ex)
		{
			LOGGER.log(Level.WARNING, "No se pudo guardar el perfil sincrono del laboratorio.", ex);
			return false;
		}
	}

	/**
	 * Phase 2: loads each physical anchor, walks every class in its racial
	 * branch at level 80, and captures the calculated values from the real
	 * Player object. The anchor is returned to its level-one root afterward.
	 */
	private void runCleanClassCoverage()
	{
		try
		{
			final int expected = PlayerClass.values().length;
			final int existing = countCleanClassProfiles();
			if (existing >= expected)
			{
				LOGGER.info("Laboratorio L2 fase 2: cobertura limpia completa (" + existing + "/" + expected + "); no se modifica el roster.");
				return;
			}

			LOGGER.info("Laboratorio L2 fase 2: generando perfiles reales de clase (" + existing + "/" + expected + ").");
			int captured = 0;
			for (int anchorIndex = 0; anchorIndex < ANCHOR_NAMES.length; anchorIndex++)
			{
				final String anchorName = ANCHOR_NAMES[anchorIndex];
				final PlayerClass root = PlayerClass.getPlayerClass(ANCHOR_ROOT_CLASS_IDS[anchorIndex]);
				final int objectId = findCharacterId(anchorName);
				if ((root == null) || (objectId <= 0))
				{
					LOGGER.warning("Laboratorio L2 fase 2: falta el ancla " + anchorName + ".");
					continue;
				}

				Player player = null;
				try
				{
					player = Player.load(objectId);
					if (player == null)
					{
						LOGGER.warning("Laboratorio L2 fase 2: no se pudo cargar " + anchorName + ".");
						continue;
					}

					CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
					prepareAnchor(player);
					final List<PlayerClass> branch = new ArrayList<>();
					for (PlayerClass playerClass : PlayerClass.values())
					{
						if (rootOf(playerClass) == root)
						{
							branch.add(playerClass);
						}
					}
					branch.sort(Comparator.comparingInt(PlayerClass::getId));

					for (PlayerClass playerClass : branch)
					{
						configureCleanClass(player, playerClass, CLEAN_PROFILE_LEVEL);
						if (captureProfileNow(player))
						{
							captured++;
						}
					}
				}
				catch (Exception e)
				{
					LOGGER.log(Level.WARNING, "Laboratorio L2 fase 2: fallo el recorrido de " + anchorName + ".", e);
				}
				finally
				{
					if (player != null)
					{
						try
						{
							configureCleanClass(player, root, 1);
						}
						catch (Exception e)
						{
							LOGGER.log(Level.WARNING, "Laboratorio L2 fase 2: no se pudo restaurar " + anchorName + " a nivel 1.", e);
						}
						Disconnection.of(player).storeAndDelete();
						CONTROLLED_CAPTURE_IDS.remove(player.getObjectId());
					}
				}
			}
			LOGGER.info("Laboratorio L2 fase 2: recorrido terminado; capturas=" + captured + ", cobertura=" + countCleanClassProfiles() + "/" + expected + ".");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 2: no se pudo generar la cobertura limpia.", e);
		}
	}

	private static void prepareAnchor(Player player) throws SQLException
	{
		player.setActiveClass(0);
		try (Connection con = DatabaseFactory.getConnection())
		{
			deleteAllClassRows(con, "character_hennas", player.getObjectId());
			deleteAllClassRows(con, "character_shortcuts", player.getObjectId());
			deleteAllClassRows(con, "character_skills_save", player.getObjectId());
			deleteAllClassRows(con, "character_skills", player.getObjectId());
			deleteAllClassRows(con, "character_subclasses", player.getObjectId());
		}
		player.getSubClasses().clear();
	}

	private static void configureCleanClass(Player player, PlayerClass playerClass, int level) throws SQLException
	{
		player.stopAllEffects();
		for (int slot = 0; slot < Inventory.PAPERDOLL_TOTALSLOTS; slot++)
		{
			player.getInventory().unEquipItemInSlot(slot);
		}
		for (Skill skill : new ArrayList<>(player.getAllSkills()))
		{
			player.removeSkill(skill, false, true);
		}
		try (Connection con = DatabaseFactory.getConnection())
		{
			deleteMainClassRows(con, "character_hennas", player.getObjectId());
			deleteMainClassRows(con, "character_skills_save", player.getObjectId());
			deleteMainClassRows(con, "character_skills", player.getObjectId());
		}

		player.setBaseClass(playerClass);
		player.setPlayerClass(playerClass.getId());
		player.getStat().setExp(ExperienceData.getInstance().getExpForLevel(level));
		player.getStat().setLevel((byte) level);
		player.rewardSkills();
		player.stopAllEffects();
		player.setCurrentHpMp(player.getMaxHp(), player.getMaxMp());
		player.setCurrentCp(player.getMaxCp());
		player.storeMe();
	}

	private static void deleteMainClassRows(Connection con, String table, int objectId) throws SQLException
	{
		try (PreparedStatement ps = con.prepareStatement("DELETE FROM " + table + " WHERE charId=? AND class_index=0"))
		{
			ps.setInt(1, objectId);
			ps.executeUpdate();
		}
	}

	private static void deleteAllClassRows(Connection con, String table, int objectId) throws SQLException
	{
		try (PreparedStatement ps = con.prepareStatement("DELETE FROM " + table + " WHERE charId=?"))
		{
			ps.setInt(1, objectId);
			ps.executeUpdate();
		}
	}

	private static PlayerClass rootOf(PlayerClass playerClass)
	{
		while ((playerClass != null) && (playerClass.getParent() != null))
		{
			playerClass = playerClass.getParent();
		}
		return playerClass;
	}

	private static int findCharacterId(String name) throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT charId FROM characters WHERE char_name=? AND account_name IN ('telemetryf','telemetrym')"))
		{
			ps.setString(1, name);
			try (ResultSet rs = ps.executeQuery())
			{
				return rs.next() ? rs.getInt(1) : 0;
			}
		}
	}

	private static int countCleanClassProfiles() throws SQLException
	{
		final String sql = "SELECT COUNT(DISTINCT p.class_id) FROM lab_player_stat_profiles p JOIN characters c ON c.charId=p.char_id " +
			"WHERE c.account_name IN ('telemetryf','telemetrym') AND p.level=80 AND p.base_class_id=p.class_id AND p.class_index=0 " +
			"AND p.sub1_class_id=-1 AND p.sub2_class_id=-1 AND p.sub3_class_id=-1 AND p.equipped_count=0 AND p.effect_count=0";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	/**
	 * Phase 3: measures every unordered pair of third professions. Each pair is
	 * stored twice, once with the main class active and once with the subclass
	 * active, while both skill trees remain cumulative.
	 */
	private void runPairCoverage()
	{
		try
		{
			if (countCleanClassProfiles() < PlayerClass.values().length)
			{
				LOGGER.info("Laboratorio L2 fase 3: espera la cobertura limpia de fase 2.");
				ThreadPool.schedule(this::runPairCoverage, 60000);
				return;
			}

			final Set<String> completedPairs = loadCompletedPairKeys();
			if (completedPairs.size() >= EXPECTED_PAIR_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 3: parejas completas (" + completedPairs.size() + "/" + EXPECTED_PAIR_COUNT + "); no se modifica el roster.");
				return;
			}

			final List<PlayerClass> thirdClasses = new ArrayList<>();
			for (PlayerClass playerClass : PlayerClass.values())
			{
				if (playerClass.level() == 3)
				{
					thirdClasses.add(playerClass);
				}
			}
			thirdClasses.sort(Comparator.comparingInt(PlayerClass::getId));
			final List<PairDefinition> pairs = new ArrayList<>(EXPECTED_PAIR_COUNT);
			for (int first = 0; first < thirdClasses.size(); first++)
			{
				for (int second = first + 1; second < thirdClasses.size(); second++)
				{
					pairs.add(new PairDefinition(thirdClasses.get(first), thirdClasses.get(second)));
				}
			}
			if (pairs.size() != EXPECTED_PAIR_COUNT)
			{
				throw new IllegalStateException("Se esperaban " + EXPECTED_PAIR_COUNT + " parejas y se calcularon " + pairs.size() + ".");
			}

			LOGGER.info("Laboratorio L2 fase 3: preparando inventario real de skills para 31 terceras profesiones.");
			final Map<Integer, Map<Integer, Skill>> classSkillSets = buildThirdClassSkillSets(thirdClasses);
			if (classSkillSets.size() != thirdClasses.size())
			{
				throw new IllegalStateException("Solo se pudieron preparar " + classSkillSets.size() + " inventarios de skills.");
			}

			LOGGER.info("Laboratorio L2 fase 3: midiendo parejas desde " + completedPairs.size() + "/" + EXPECTED_PAIR_COUNT + " con " + PAIR_WORKER_COUNT + " anclas.");
			final CountDownLatch workers = new CountDownLatch(PAIR_WORKER_COUNT);
			final AtomicInteger measured = new AtomicInteger(completedPairs.size());
			final AtomicInteger failures = new AtomicInteger();
			for (int workerIndex = 0; workerIndex < PAIR_WORKER_COUNT; workerIndex++)
			{
				final int assignedWorker = workerIndex;
				ThreadPool.execute(() ->
				{
					try
					{
						runPairWorker(assignedWorker, pairs, completedPairs, classSkillSets, measured, failures);
					}
					finally
					{
						workers.countDown();
					}
				});
			}
			workers.await();
			LOGGER.info("Laboratorio L2 fase 3: recorrido terminado; parejas=" + countCompletePairs() + "/" + EXPECTED_PAIR_COUNT + ", estados=" + countPairStates() + "/" + (EXPECTED_PAIR_COUNT * 2) + ", fallos=" + failures.get() + ".");
		}
		catch (InterruptedException e)
		{
			Thread.currentThread().interrupt();
			LOGGER.warning("Laboratorio L2 fase 3: recorrido interrumpido.");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 3: no se pudo generar la matriz de parejas.", e);
		}
	}

	private static Map<Integer, Map<Integer, Skill>> buildThirdClassSkillSets(List<PlayerClass> thirdClasses) throws Exception
	{
		final Map<Integer, Map<Integer, Skill>> result = new HashMap<>();
		final int objectId = findCharacterId("Myrentha");
		final PlayerClass root = PlayerClass.getPlayerClass(38);
		Player player = null;
		try
		{
			player = Player.load(objectId);
			if (player == null)
			{
				throw new IllegalStateException("No se pudo cargar Myrentha para catalogar skills.");
			}
			CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
			prepareAnchor(player);
			for (PlayerClass playerClass : thirdClasses)
			{
				configureCleanClass(player, playerClass, CLEAN_PROFILE_LEVEL);
				final Map<Integer, Skill> skills = new HashMap<>();
				for (Skill skill : player.getAllSkills())
				{
					skills.put(skill.getId(), skill);
				}
				result.put(playerClass.getId(), skills);
			}
		}
		finally
		{
			if (player != null)
			{
				try
				{
					prepareAnchor(player);
					configureCleanClass(player, root, 1);
				}
				finally
				{
					Disconnection.of(player).storeAndDelete();
					CONTROLLED_CAPTURE_IDS.remove(player.getObjectId());
				}
			}
		}
		return result;
	}

	private void runPairWorker(int workerIndex, List<PairDefinition> pairs, Set<String> completedPairs, Map<Integer, Map<Integer, Skill>> classSkillSets, AtomicInteger measured, AtomicInteger failures)
	{
		final String anchorName = PAIR_WORKER_NAMES[workerIndex];
		final PlayerClass root = PlayerClass.getPlayerClass(PAIR_WORKER_ROOTS[workerIndex]);
		Player player = null;
		try
		{
			player = Player.load(findCharacterId(anchorName));
			if (player == null)
			{
				throw new IllegalStateException("No se pudo cargar el ancla " + anchorName + ".");
			}
			CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
			for (int pairIndex = workerIndex; pairIndex < pairs.size(); pairIndex += PAIR_WORKER_COUNT)
			{
				final PairDefinition pair = pairs.get(pairIndex);
				if (completedPairs.contains(pair.key()))
				{
					continue;
				}
				try
				{
					measurePair(player, pair, classSkillSets.get(pair.first.getId()), classSkillSets.get(pair.second.getId()));
					final int total = measured.incrementAndGet();
					if ((total % 25) == 0)
					{
						LOGGER.info("Laboratorio L2 fase 3: progreso " + total + "/" + EXPECTED_PAIR_COUNT + " parejas.");
					}
				}
				catch (Exception e)
				{
					failures.incrementAndGet();
					LOGGER.log(Level.WARNING, "Laboratorio L2 fase 3: fallo la pareja " + pair.key() + " en " + anchorName + ".", e);
				}
			}
		}
		catch (Exception e)
		{
			failures.incrementAndGet();
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 3: fallo el trabajador " + anchorName + ".", e);
		}
		finally
		{
			if (player != null)
			{
				try
				{
					prepareAnchor(player);
					configureCleanClass(player, root, 1);
				}
				catch (Exception e)
				{
					LOGGER.log(Level.WARNING, "Laboratorio L2 fase 3: no se pudo restaurar " + anchorName + ".", e);
				}
				Disconnection.of(player).storeAndDelete();
				CONTROLLED_CAPTURE_IDS.remove(player.getObjectId());
			}
		}
	}

	private void measurePair(Player player, PairDefinition pair, Map<Integer, Skill> firstSkills, Map<Integer, Skill> secondSkills) throws Exception
	{
		prepareAnchor(player);
		configureCleanClass(player, pair.first, CLEAN_PROFILE_LEVEL);
		if (!player.addSubClass(pair.second.getId(), 1))
		{
			throw new IllegalStateException("No se pudo agregar Sub 1 " + pair.second.getId() + ".");
		}

		player.setActiveClass(1);
		maximizeActiveClass(player, CLEAN_PROFILE_LEVEL);
		player.setActiveClass(0);
		cleanPairState(player);
		upsertPairProfile(player, pair, new PairSkillMetrics(firstSkills, secondSkills));

		player.setActiveClass(1);
		cleanPairState(player);
		upsertPairProfile(player, pair, new PairSkillMetrics(firstSkills, secondSkills));
	}

	private static void maximizeActiveClass(Player player, int level)
	{
		player.getStat().setExp(ExperienceData.getInstance().getExpForLevel(level));
		player.getStat().setLevel((byte) level);
		player.rewardSkills();
		cleanPairState(player);
		player.storeMe();
	}

	private static void cleanPairState(Player player)
	{
		player.stopAllEffects();
		for (int slot = 0; slot < Inventory.PAPERDOLL_TOTALSLOTS; slot++)
		{
			player.getInventory().unEquipItemInSlot(slot);
		}
		player.setCurrentHpMp(player.getMaxHp(), player.getMaxMp());
		player.setCurrentCp(player.getMaxCp());
	}

	private void upsertPairProfile(Player player, PairDefinition pair, PairSkillMetrics metrics) throws SQLException
	{
		final CreatureSnapshot c = new CreatureSnapshot(player);
		final List<String> skillParts = new ArrayList<>();
		int passiveSkills = 0;
		for (Skill skill : player.getAllSkills())
		{
			skillParts.add(skill.getId() + ":" + skill.getLevel());
			if (skill.isPassive())
			{
				passiveSkills++;
			}
		}
		Collections.sort(skillParts);
		final String skillKey = String.join(",", skillParts);
		if (!skillKey.equals(metrics.expectedSkillKey))
		{
			throw new SQLException("El conjunto restaurado de skills no coincide con la union normalizada para " + pair.key() + " activa=" + c.classId + ".");
		}
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(UPSERT_PAIR_PROFILE))
		{
			int i = 1;
			ps.setInt(i++, pair.first.getId()); ps.setInt(i++, pair.second.getId());
			ps.setInt(i++, pair.first.getId()); ps.setInt(i++, pair.second.getId());
			ps.setInt(i++, c.classId); ps.setInt(i++, c.classIndex); ps.setInt(i++, c.objectId); ps.setString(i++, c.name);
			ps.setLong(i++, c.observedMs); ps.setInt(i++, c.raceId); ps.setString(i++, c.raceName); ps.setInt(i++, c.level);
			ps.setInt(i++, c.equippedCount); ps.setInt(i++, c.effectCount); ps.setInt(i++, c.skillCount);
			ps.setInt(i++, passiveSkills); ps.setInt(i++, c.skillCount - passiveSkills); ps.setInt(i++, metrics.sharedSkillIds);
			ps.setInt(i++, metrics.masteryCollisions); ps.setInt(i++, metrics.expectedSkillCount);
			ps.setString(i++, CreatureSnapshot.sha256(skillKey)); ps.setString(i++, skillKey);
			ps.setDouble(i++, c.maxCp); ps.setDouble(i++, c.maxHp); ps.setDouble(i++, c.maxMp);
			ps.setDouble(i++, c.pAtk); ps.setDouble(i++, c.mAtk); ps.setDouble(i++, c.pDef); ps.setDouble(i++, c.mDef);
			ps.setInt(i++, c.accuracy); ps.setInt(i++, c.evasion); ps.setInt(i++, c.pCritical); ps.setInt(i++, c.mCritical);
			ps.setDouble(i++, c.pAtkSpeed); ps.setInt(i++, c.mAtkSpeed); ps.setDouble(i++, c.runSpeed); ps.setInt(i++, c.attackRange);
			ps.setInt(i++, c.statStr); ps.setInt(i++, c.statDex); ps.setInt(i++, c.statCon); ps.setInt(i++, c.statInt); ps.setInt(i++, c.statWit); ps.setInt(i, c.statMen);
			ps.executeUpdate();
		}
	}

	private static Set<String> loadCompletedPairKeys() throws SQLException
	{
		final Set<String> result = new HashSet<>();
		final String sql = "SELECT pair_a_id,pair_b_id FROM lab_class_pair_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0 AND skill_count>0 " +
			"GROUP BY pair_a_id,pair_b_id HAVING COUNT(*)=2 AND COUNT(DISTINCT active_class_id)=2 AND SUM(active_class_index=0)=1 AND SUM(active_class_index=1)=1";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(rs.getInt(1) + ":" + rs.getInt(2));
			}
		}
		return result;
	}

	private static int countCompletePairs() throws SQLException
	{
		return loadCompletedPairKeys().size();
	}

	private static int countPairStates() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_class_pair_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0 AND skill_count>0"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	/**
	 * Phase 4B: builds the 155 candidates selected by phase 4A on real Player
	 * objects. Every build is measured in its four active class slots and is
	 * accepted only when the exact ID:level skill catalog matches the theoretical
	 * candidate.
	 */
	private void runFourClassCoverage()
	{
		try
		{
			if (countCompletePairs() < EXPECTED_PAIR_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 4B: espera la matriz completa de fase 3.");
				ThreadPool.schedule(this::runFourClassCoverage, 60000);
				return;
			}
			if (countSelectedBuildCandidates() != EXPECTED_BUILD_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 4B: espera 155 candidatos seleccionados por fase 4A.");
				ThreadPool.schedule(this::runFourClassCoverage, 60000);
				return;
			}

			final List<FourClassBuild> builds = loadSelectedBuilds();
			if (builds.size() != EXPECTED_BUILD_COUNT)
			{
				throw new IllegalStateException("Se esperaban " + EXPECTED_BUILD_COUNT + " builds seleccionadas y se cargaron " + builds.size() + ".");
			}
			final Set<String> completedBuilds = loadCompletedBuildKeys();
			if (completedBuilds.size() >= EXPECTED_BUILD_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 4B: builds completas (" + completedBuilds.size() + "/" + EXPECTED_BUILD_COUNT + ", estados=" + countFourClassStates() + "/" + EXPECTED_BUILD_STATE_COUNT + "); no se modifica el roster.");
				return;
			}

			LOGGER.info("Laboratorio L2 fase 4B: midiendo builds reales desde " + completedBuilds.size() + "/" + EXPECTED_BUILD_COUNT + " con " + ANCHOR_NAMES.length + " anclas raciales.");
			final CountDownLatch workers = new CountDownLatch(ANCHOR_NAMES.length);
			final AtomicInteger measured = new AtomicInteger(completedBuilds.size());
			final AtomicInteger failures = new AtomicInteger();
			for (int workerIndex = 0; workerIndex < ANCHOR_NAMES.length; workerIndex++)
			{
				final int assignedWorker = workerIndex;
				ThreadPool.execute(() ->
				{
					try
					{
						runFourClassWorker(assignedWorker, builds, completedBuilds, measured, failures);
					}
					finally
					{
						workers.countDown();
					}
				});
			}
			workers.await();
			LOGGER.info("Laboratorio L2 fase 4B: recorrido terminado; builds=" + countCompleteBuilds() + "/" + EXPECTED_BUILD_COUNT + ", estados=" + countFourClassStates() + "/" + EXPECTED_BUILD_STATE_COUNT + ", fallos=" + failures.get() + ".");
		}
		catch (InterruptedException e)
		{
			Thread.currentThread().interrupt();
			LOGGER.warning("Laboratorio L2 fase 4B: recorrido interrumpido.");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4B: no se pudo medir la muestra de cuatro clases.", e);
		}
	}

	private void runFourClassWorker(int workerIndex, List<FourClassBuild> builds, Set<String> completedBuilds, AtomicInteger measured, AtomicInteger failures)
	{
		final String anchorName = ANCHOR_NAMES[workerIndex];
		final PlayerClass root = PlayerClass.getPlayerClass(ANCHOR_ROOT_CLASS_IDS[workerIndex]);
		Player player = null;
		try
		{
			player = Player.load(findCharacterId(anchorName));
			if (player == null)
			{
				throw new IllegalStateException("No se pudo cargar el ancla " + anchorName + ".");
			}
			CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
			for (FourClassBuild build : builds)
			{
				if ((rootOf(build.main) != root) || completedBuilds.contains(build.key()))
				{
					continue;
				}
				try
				{
					measureFourClassBuild(player, build);
					final int total = measured.incrementAndGet();
					if ((total % 10) == 0)
					{
						LOGGER.info("Laboratorio L2 fase 4B: progreso " + total + "/" + EXPECTED_BUILD_COUNT + " builds.");
					}
				}
				catch (Exception e)
				{
					failures.incrementAndGet();
					LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4B: fallo la build " + build.key() + " en " + anchorName + ".", e);
				}
			}
		}
		catch (Exception e)
		{
			failures.incrementAndGet();
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4B: fallo el trabajador " + anchorName + ".", e);
		}
		finally
		{
			if (player != null)
			{
				try
				{
					prepareAnchor(player);
					configureCleanClass(player, root, 1);
				}
				catch (Exception e)
				{
					LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4B: no se pudo restaurar " + anchorName + ".", e);
				}
				Disconnection.of(player).storeAndDelete();
				CONTROLLED_CAPTURE_IDS.remove(player.getObjectId());
			}
		}
	}

	private void measureFourClassBuild(Player player, FourClassBuild build) throws Exception
	{
		prepareAnchor(player);
		configureCleanClass(player, build.main, CLEAN_PROFILE_LEVEL);
		for (int index = 1; index <= 3; index++)
		{
			final PlayerClass subClass = build.classAt(index);
			if (!player.addSubClass(subClass.getId(), index))
			{
				throw new IllegalStateException("No se pudo agregar Sub " + index + " " + subClass.getId() + ".");
			}
			player.setActiveClass(index);
			maximizeActiveClass(player, CLEAN_PROFILE_LEVEL);
		}

		for (int index = 0; index <= 3; index++)
		{
			player.setActiveClass(index);
			cleanPairState(player);
			upsertFourClassProfile(player, build);
		}
	}

	private void upsertFourClassProfile(Player player, FourClassBuild build) throws SQLException
	{
		final CreatureSnapshot c = new CreatureSnapshot(player);
		if ((c.classIndex < 0) || (c.classIndex > 3) || (c.classId != build.classAt(c.classIndex).getId()))
		{
			throw new SQLException("La clase activa no coincide con la ranura esperada para " + build.key() + ".");
		}
		final List<String> skillParts = new ArrayList<>();
		int passiveSkills = 0;
		for (Skill skill : player.getAllSkills())
		{
			skillParts.add(skill.getId() + ":" + skill.getLevel());
			if (skill.isPassive())
			{
				passiveSkills++;
			}
		}
		Collections.sort(skillParts);
		final String skillKey = String.join(",", skillParts);
		final String skillHash = CreatureSnapshot.sha256(skillKey);
		if (!skillKey.equals(build.expectedSkillKey) || !skillHash.equals(build.expectedSkillHash) || (skillParts.size() != build.expectedSkillCount))
		{
			throw new SQLException("El conjunto real de skills no coincide con fase 4A para " + build.key() + " activa=" + c.classId + ".");
		}
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(UPSERT_FOUR_CLASS_PROFILE))
		{
			int i = 1;
			ps.setInt(i++, build.main.getId()); ps.setInt(i++, build.sub1.getId()); ps.setInt(i++, build.sub2.getId()); ps.setInt(i++, build.sub3.getId());
			ps.setInt(i++, c.classId); ps.setInt(i++, c.classIndex); ps.setInt(i++, c.objectId); ps.setString(i++, c.name);
			ps.setString(i++, build.bucket); ps.setLong(i++, c.observedMs); ps.setInt(i++, c.raceId); ps.setString(i++, c.raceName); ps.setInt(i++, c.level);
			ps.setInt(i++, c.equippedCount); ps.setInt(i++, c.effectCount); ps.setInt(i++, c.skillCount);
			ps.setInt(i++, passiveSkills); ps.setInt(i++, c.skillCount - passiveSkills); ps.setInt(i++, build.expectedSkillCount);
			ps.setString(i++, skillHash); ps.setString(i++, skillKey);
			ps.setDouble(i++, c.maxCp); ps.setDouble(i++, c.maxHp); ps.setDouble(i++, c.maxMp);
			ps.setDouble(i++, c.pAtk); ps.setDouble(i++, c.mAtk); ps.setDouble(i++, c.pDef); ps.setDouble(i++, c.mDef);
			ps.setInt(i++, c.accuracy); ps.setInt(i++, c.evasion); ps.setInt(i++, c.pCritical); ps.setInt(i++, c.mCritical);
			ps.setDouble(i++, c.pAtkSpeed); ps.setInt(i++, c.mAtkSpeed); ps.setDouble(i++, c.runSpeed); ps.setInt(i++, c.attackRange);
			ps.setInt(i++, c.statStr); ps.setInt(i++, c.statDex); ps.setInt(i++, c.statCon); ps.setInt(i++, c.statInt); ps.setInt(i++, c.statWit); ps.setInt(i, c.statMen);
			ps.executeUpdate();
		}
	}

	private static List<FourClassBuild> loadSelectedBuilds() throws SQLException
	{
		final List<FourClassBuild> result = new ArrayList<>(EXPECTED_BUILD_COUNT);
		final String sql = "SELECT main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,selection_bucket,skill_count,skill_hash,skill_key " +
			"FROM lab_four_class_candidates WHERE selected=1 ORDER BY selection_order";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				final FourClassBuild build = new FourClassBuild(rs.getInt(1), rs.getInt(2), rs.getInt(3), rs.getInt(4), rs.getString(5), rs.getInt(6), rs.getString(7), rs.getString(8));
				if (!build.isValid())
				{
					throw new SQLException("Candidato 4A invalido: " + build.key() + ".");
				}
				result.add(build);
			}
		}
		return result;
	}

	private static int countSelectedBuildCandidates() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_four_class_candidates WHERE selected=1 AND skill_key IS NOT NULL AND skill_key<>''"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static Set<String> loadCompletedBuildKeys() throws SQLException
	{
		final Set<String> result = new HashSet<>();
		final String sql = "SELECT p.main_class_id,p.sub1_class_id,p.sub2_class_id,p.sub3_class_id FROM lab_four_class_profiles p " +
			"JOIN lab_four_class_candidates c ON c.main_class_id=p.main_class_id AND c.sub1_class_id=p.sub1_class_id AND c.sub2_class_id=p.sub2_class_id AND c.sub3_class_id=p.sub3_class_id " +
			"WHERE c.selected=1 AND p.level=80 AND p.equipped_count=0 AND p.effect_count=0 AND p.skill_count=p.expected_skill_count AND p.skill_hash=c.skill_hash " +
			"GROUP BY p.main_class_id,p.sub1_class_id,p.sub2_class_id,p.sub3_class_id HAVING COUNT(*)=4 AND COUNT(DISTINCT p.active_class_id)=4 " +
			"AND SUM(p.active_class_index=0 AND p.active_class_id=p.main_class_id)=1 AND SUM(p.active_class_index=1 AND p.active_class_id=p.sub1_class_id)=1 " +
			"AND SUM(p.active_class_index=2 AND p.active_class_id=p.sub2_class_id)=1 AND SUM(p.active_class_index=3 AND p.active_class_id=p.sub3_class_id)=1";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(rs.getInt(1) + ":" + rs.getInt(2) + ":" + rs.getInt(3) + ":" + rs.getInt(4));
			}
		}
		return result;
	}

	private static int countCompleteBuilds() throws SQLException
	{
		return loadCompletedBuildKeys().size();
	}

	private static int countFourClassStates() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_four_class_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0 AND skill_count=expected_skill_count"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	/**
	 * Phase 4D: runs the fixed benchmark queue with real Player/Npc objects,
	 * real equipment and the combat formulas/effect handlers from the core. The
	 * 45/60 second window is advanced by action cadence instead of wall-clock
	 * sleeping, and that execution mode is stored explicitly with every run.
	 */
	private void runCombatBenchmarks()
	{
		Player player = null;
		PlayerClass restoreRoot = null;
		String loadedBuild = "";
		try
		{
			if (countBenchmarkCases() != EXPECTED_BENCHMARK_CASE_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 4D: espera la cola completa de 95 casos.");
				ThreadPool.schedule(this::runCombatBenchmarks, 60000);
				return;
			}
			final int completed = countBenchmarkRuns();
			if (completed >= EXPECTED_BENCHMARK_RUN_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 4D: combate controlado completo (" + completed + "/" + EXPECTED_BENCHMARK_RUN_COUNT + "); no se modifica el roster.");
				return;
			}
			if (countOnlineCharacters() > 0)
			{
				LOGGER.info("Laboratorio L2 fase 4D: hay jugadores conectados; la ejecucion automatica se posterga.");
				ThreadPool.schedule(this::runCombatBenchmarks, 60000);
				return;
			}

			final Npc atlas = getBenchmarkNpc(BENCHMARK_ATLAS_ID);
			final Npc ares = getBenchmarkNpc(BENCHMARK_ARES_ID);
			final Npc nyx = getBenchmarkNpc(BENCHMARK_NYX_ID);
			if ((atlas == null) || (ares == null) || (nyx == null))
			{
				LOGGER.info("Laboratorio L2 fase 4D: espera los tres NPC del Coliseo.");
				ThreadPool.schedule(this::runCombatBenchmarks, 60000);
				return;
			}

			final Set<String> completedRuns = loadCompletedBenchmarkRuns();
			final List<BenchmarkCase> cases = loadBenchmarkCases();
			int measured = completedRuns.size();
			int failures = 0;
			LOGGER.info("Laboratorio L2 fase 4D: ejecutando motor acelerado desde " + measured + "/" + EXPECTED_BENCHMARK_RUN_COUNT + " pasadas.");

			for (BenchmarkCase benchmark : cases)
			{
				boolean caseComplete = true;
				for (int runNumber = 1; runNumber <= benchmark.repetitions; runNumber++)
				{
					if (!completedRuns.contains(benchmark.caseId + ":" + runNumber))
					{
						caseComplete = false;
						break;
					}
				}
				if (caseComplete)
				{
					continue;
				}
				if (!benchmark.buildKey().equals(loadedBuild))
				{
					if (player != null)
					{
						restoreBenchmarkAnchor(player, restoreRoot);
						player = null;
					}
					restoreRoot = rootOf(benchmark.main);
					player = Player.load(findCharacterId(anchorForRoot(restoreRoot)));
					if (player == null)
					{
						throw new IllegalStateException("No se pudo cargar el ancla para " + benchmark.buildKey() + ".");
					}
					CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
					BENCHMARK_CAPTURE_IDS.add(player.getObjectId());
					configureBenchmarkBuild(player, benchmark);
					loadedBuild = benchmark.buildKey();
				}

				player.setActiveClass(benchmark.activeClassIndex);
				cleanPairState(player);
				final List<Item> createdItems = new ArrayList<>();
				try
				{
					equipBenchmarkKit(player, benchmark, createdItems);
					for (int runNumber = 1; runNumber <= benchmark.repetitions; runNumber++)
					{
						final String runKey = benchmark.caseId + ":" + runNumber;
						if (completedRuns.contains(runKey))
						{
							continue;
						}
						try
						{
							final BenchmarkResult result = executeBenchmarkRun(player, benchmark, runNumber, atlas, ares, nyx);
							storeBenchmarkRun(result);
							completedRuns.add(runKey);
							measured++;
							if ((measured % 15) == 0)
							{
								LOGGER.info("Laboratorio L2 fase 4D: progreso " + measured + "/" + EXPECTED_BENCHMARK_RUN_COUNT + " pasadas.");
							}
						}
						catch (Exception e)
						{
							failures++;
							LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4D: fallo " + runKey + ".", e);
						}
					}
				}
				finally
				{
					removeBenchmarkKit(player, createdItems);
					cleanBenchmarkActors(player, atlas, ares, nyx);
				}
			}

			LOGGER.info("Laboratorio L2 fase 4D: recorrido terminado; pasadas=" + countBenchmarkRuns() + "/" + EXPECTED_BENCHMARK_RUN_COUNT + ", fallos=" + failures + ".");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4D: no se pudo ejecutar la cola de combate.", e);
		}
		finally
		{
			if (player != null)
			{
				restoreBenchmarkAnchor(player, restoreRoot);
			}
		}
		try
		{
			if (countBenchmarkRuns() < EXPECTED_BENCHMARK_RUN_COUNT)
			{
				ThreadPool.schedule(this::runCombatBenchmarks, 60000);
			}
		}
		catch (SQLException e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4D: no se pudo verificar el progreso final.", e);
		}
	}

	/**
	 * Phase 5A: replays the 30 Nyx resistance cases at four damage scales.
	 * The original Phase 4D rows remain untouched; only the final damage from
	 * the real core formula is scaled. Rotation, control, debuffs, equipment
	 * and class builds are identical across profiles.
	 */
	private void runNyxCalibration()
	{
		Player player = null;
		PlayerClass restoreRoot = null;
		String loadedBuild = "";
		try
		{
			if (countBenchmarkRuns() < EXPECTED_BENCHMARK_RUN_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 5A: espera las 285 pasadas de fase 4D.");
				return;
			}
			final List<BenchmarkCase> cases = loadNyxCalibrationCases();
			if (cases.size() != EXPECTED_NYX_CALIBRATION_CASE_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 5A: espera 30 casos de resistencia contra Nyx.");
				return;
			}
			final int completed = countNyxCalibrationRuns();
			if (completed >= EXPECTED_NYX_CALIBRATION_RUN_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 5A: calibracion de Nyx completa (" + completed + "/" + EXPECTED_NYX_CALIBRATION_RUN_COUNT + "); fase 4D permanece intacta.");
				return;
			}
			if (countOnlineCharacters() > 0)
			{
				LOGGER.info("Laboratorio L2 fase 5A: hay jugadores conectados; la calibracion se posterga.");
				return;
			}
			final Npc nyx = getBenchmarkNpc(BENCHMARK_NYX_ID);
			if (nyx == null)
			{
				LOGGER.info("Laboratorio L2 fase 5A: espera a Nyx en el Coliseo.");
				return;
			}

			final Set<String> completedRuns = loadCompletedNyxCalibrationRuns();
			int measured = completedRuns.size();
			int failures = 0;
			LOGGER.info("Laboratorio L2 fase 5A: calibrando Nyx desde " + measured + "/" + EXPECTED_NYX_CALIBRATION_RUN_COUNT + " pasadas.");

			for (BenchmarkCase benchmark : cases)
			{
				if (!benchmark.buildKey().equals(loadedBuild))
				{
					if (player != null)
					{
						restoreBenchmarkAnchor(player, restoreRoot);
						player = null;
					}
					restoreRoot = rootOf(benchmark.main);
					player = Player.load(findCharacterId(anchorForRoot(restoreRoot)));
					if (player == null)
					{
						throw new IllegalStateException("No se pudo cargar el ancla para " + benchmark.buildKey() + ".");
					}
					CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
					BENCHMARK_CAPTURE_IDS.add(player.getObjectId());
					configureBenchmarkBuild(player, benchmark);
					loadedBuild = benchmark.buildKey();
				}

				player.setActiveClass(benchmark.activeClassIndex);
				cleanPairState(player);
				final List<Item> createdItems = new ArrayList<>();
				try
				{
					equipBenchmarkKit(player, benchmark, createdItems);
					for (int scalePercent : NYX_CALIBRATION_SCALES)
					{
						for (int runNumber = 1; runNumber <= benchmark.repetitions; runNumber++)
						{
							final String runKey = benchmark.caseId + ":" + scalePercent + ":" + runNumber;
							if (completedRuns.contains(runKey))
							{
								continue;
							}
							try
							{
								final BenchmarkResult result = executeNyxCalibrationRun(player, benchmark, runNumber, nyx, scalePercent);
								storeNyxCalibrationRun(result, benchmark, scalePercent);
								completedRuns.add(runKey);
								measured++;
								if ((measured % 30) == 0)
								{
									LOGGER.info("Laboratorio L2 fase 5A: progreso " + measured + "/" + EXPECTED_NYX_CALIBRATION_RUN_COUNT + " pasadas.");
								}
							}
							catch (Exception e)
							{
								failures++;
								LOGGER.log(Level.WARNING, "Laboratorio L2 fase 5A: fallo " + runKey + ".", e);
							}
						}
					}
				}
				finally
				{
					removeBenchmarkKit(player, createdItems);
					cleanBenchmarkActors(player, nyx);
				}
			}
			LOGGER.info("Laboratorio L2 fase 5A: recorrido terminado; pasadas=" + countNyxCalibrationRuns() + "/" + EXPECTED_NYX_CALIBRATION_RUN_COUNT + ", fallos=" + failures + ".");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 5A: no se pudo ejecutar la calibracion de Nyx.", e);
		}
		finally
		{
			if (player != null)
			{
				restoreBenchmarkAnchor(player, restoreRoot);
			}
		}
		try
		{
			if (countNyxCalibrationRuns() < EXPECTED_NYX_CALIBRATION_RUN_COUNT)
			{
				ThreadPool.schedule(this::runNyxCalibration, 60000);
			}
		}
		catch (SQLException e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 5A: no se pudo verificar el progreso final.", e);
		}
	}

	private static List<BenchmarkCase> loadNyxCalibrationCases() throws SQLException
	{
		final List<BenchmarkCase> result = new ArrayList<>(EXPECTED_NYX_CALIBRATION_CASE_COUNT);
		final String sql = "SELECT case_id,finalist_rank,category,main_class_id,sub1_class_id,sub2_class_id,sub3_class_id," +
			"active_class_id,active_class_index,benchmark_code,opponent_id,opponent_name,equipment_kit,weapon_id,duration_seconds,repetitions " +
			"FROM lab_combat_benchmark_plan WHERE benchmark_code='resistencia_nyx' ORDER BY finalist_rank,priority";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(new BenchmarkCase(rs));
			}
		}
		return result;
	}

	private static int countNyxCalibrationRuns() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_nyx_calibration_runs"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static Set<String> loadCompletedNyxCalibrationRuns() throws SQLException
	{
		final Set<String> result = new HashSet<>();
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT source_case_id,scale_percent,run_number FROM lab_nyx_calibration_runs"); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(rs.getString(1) + ":" + rs.getInt(2) + ":" + rs.getInt(3));
			}
		}
		return result;
	}

	private static BenchmarkResult executeNyxCalibrationRun(Player player, BenchmarkCase benchmark, int runNumber, Npc nyx, int scalePercent)
	{
		cleanBenchmarkActors(player, nyx);
		final BenchmarkResult result = new BenchmarkResult(player, benchmark, runNumber);
		runSurvival(result, player, nyx, new int[] {337, 1064, 1074, 1341, 1239, 1291, 1159}, scalePercent / 100.0);
		result.notes = "Fase 5A; formula real de Nyx con dano final al " + scalePercent + "%; control, debuffs y cadencia sin escalar.";
		cleanBenchmarkActors(player, nyx);
		return result;
	}

	private static void storeNyxCalibrationRun(BenchmarkResult r, BenchmarkCase benchmark, int scalePercent) throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(INSERT_NYX_CALIBRATION_RUN))
		{
			int i = 1;
			ps.setString(i++, r.caseId); ps.setInt(i++, scalePercent); ps.setInt(i++, r.runNumber); ps.setLong(i++, System.currentTimeMillis());
			ps.setString(i++, "CORE_ACCELERATED_SCALED"); ps.setInt(i++, benchmark.finalistRank); ps.setString(i++, benchmark.category);
			ps.setInt(i++, r.charId); ps.setString(i++, r.charName); ps.setInt(i++, r.activeClassId); ps.setInt(i++, r.activeClassIndex);
			ps.setInt(i++, r.opponentId); ps.setString(i++, r.opponentName); ps.setString(i++, r.equipmentKit); ps.setInt(i++, r.weaponId);
			ps.setInt(i++, r.durationSeconds); ps.setString(i++, r.rotation); ps.setInt(i++, r.actions); ps.setInt(i++, r.hits); ps.setInt(i++, r.casts);
			ps.setInt(i++, r.criticals); ps.setInt(i++, r.misses); ps.setInt(i++, r.bssUsed); ps.setDouble(i++, r.damageReceived);
			ps.setDouble(i++, r.timeAlive); ps.setDouble(i++, r.hpCpRemaining); ps.setDouble(i++, r.controlTime); ps.setString(i, r.notes);
			ps.executeUpdate();
		}
	}

	/**
	 * Phase 5A.2: measures a normal Storm Screamer and the same character after
	 * each cumulative subclass is added. Storm Screamer remains active in every
	 * stage and all stages use the same S-grade equipment without external buffs.
	 */
	private void runMagicProgression()
	{
		Player player = null;
		final PlayerClass restoreRoot = PlayerClass.getPlayerClass(38); // Dark Mystic.
		try
		{
			if (countMagicProgressionRuns() >= EXPECTED_MAGIC_PROGRESSION_RUN_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 5A.2: progresion magica completa (" + EXPECTED_MAGIC_PROGRESSION_RUN_COUNT + "/" + EXPECTED_MAGIC_PROGRESSION_RUN_COUNT + ").");
				return;
			}
			if (countOnlineCharacters() > 0)
			{
				LOGGER.info("Laboratorio L2 fase 5A.2: hay jugadores conectados; la progresion se posterga.");
				ThreadPool.schedule(this::runMagicProgression, 60000);
				return;
			}
			final Npc atlas = getBenchmarkNpc(BENCHMARK_ATLAS_ID);
			if (atlas == null)
			{
				LOGGER.info("Laboratorio L2 fase 5A.2: espera a Atlas en el Coliseo.");
				ThreadPool.schedule(this::runMagicProgression, 60000);
				return;
			}

			final PlayerClass mainClass = PlayerClass.getPlayerClass(MAGIC_PROGRESSION_CLASS_IDS[0]);
			player = Player.load(findCharacterId(anchorForRoot(restoreRoot)));
			if ((player == null) || (mainClass == null))
			{
				throw new IllegalStateException("No se pudo cargar el ancla Dark Mystic o Storm Screamer.");
			}
			CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
			BENCHMARK_CAPTURE_IDS.add(player.getObjectId());
			prepareAnchor(player);
			configureCleanClass(player, mainClass, CLEAN_PROFILE_LEVEL);
			final Set<String> completedRuns = loadCompletedMagicProgressionRuns();
			int measured = completedRuns.size();

			for (int stage = 0; stage < MAGIC_PROGRESSION_CLASS_IDS.length; stage++)
			{
				if (stage > 0)
				{
					final PlayerClass subClass = PlayerClass.getPlayerClass(MAGIC_PROGRESSION_CLASS_IDS[stage]);
					if ((subClass == null) || !player.addSubClass(subClass.getId(), stage))
					{
						throw new IllegalStateException("No se pudo agregar Sub " + stage + " " + MAGIC_PROGRESSION_CLASS_IDS[stage] + ".");
					}
					player.setActiveClass(stage);
					maximizeActiveClass(player, CLEAN_PROFILE_LEVEL);
				}
				player.setActiveClass(0);
				cleanPairState(player);

				final List<Item> createdItems = new ArrayList<>();
				try
				{
					equipMagicProgressionKit(player, createdItems);
					final CreatureSnapshot snapshot = new CreatureSnapshot(player);
					int passiveSkills = 0;
					for (Skill skill : player.getAllSkills())
					{
						if (skill.isPassive())
						{
							passiveSkills++;
						}
					}
					for (int runNumber = 1; runNumber <= MAGIC_PROGRESSION_REPETITIONS; runNumber++)
					{
						final String runKey = stage + ":" + runNumber;
						if (completedRuns.contains(runKey))
						{
							continue;
						}
						final BenchmarkResult result = new BenchmarkResult(player, "magic-progression-" + stage, runNumber,
							MAGIC_PROGRESSION_DURATION_SECONDS, BENCHMARK_ATLAS_ID, "Atlas", "S_ROBE", MAGIC_PROGRESSION_WEAPON_ID);
						cleanBenchmarkActors(player, atlas);
						runMagicalOutput(result, player, atlas);
						storeMagicProgressionRun(stage, result, snapshot, passiveSkills);
						completedRuns.add(runKey);
						measured++;
						LOGGER.info("Laboratorio L2 fase 5A.2: progreso " + measured + "/" + EXPECTED_MAGIC_PROGRESSION_RUN_COUNT +
							" (" + MAGIC_PROGRESSION_LABELS[stage] + ").");
					}
				}
				finally
				{
					removeBenchmarkKit(player, createdItems);
					cleanBenchmarkActors(player, atlas);
				}
			}
			LOGGER.info("Laboratorio L2 fase 5A.2: progresion terminada; pasadas=" + countMagicProgressionRuns() + "/" + EXPECTED_MAGIC_PROGRESSION_RUN_COUNT + ".");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 5A.2: no se pudo medir la progresion magica.", e);
		}
		finally
		{
			if (player != null)
			{
				restoreBenchmarkAnchor(player, restoreRoot);
			}
		}
	}

	private static int countMagicProgressionRuns() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_magic_progression_runs"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static Set<String> loadCompletedMagicProgressionRuns() throws SQLException
	{
		final Set<String> result = new HashSet<>();
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT stage_index,run_number FROM lab_magic_progression_runs"); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(rs.getInt(1) + ":" + rs.getInt(2));
			}
		}
		return result;
	}

	private static void equipMagicProgressionKit(Player player, List<Item> createdItems)
	{
		for (int itemId : ROBE_ARMOR_IDS)
		{
			addAndEquipBenchmarkItem(player, itemId, createdItems);
		}
		for (int itemId : COMMON_JEWELRY_IDS)
		{
			addAndEquipBenchmarkItem(player, itemId, createdItems);
		}
		addAndEquipBenchmarkItem(player, MAGIC_PROGRESSION_WEAPON_ID, createdItems);
		player.setCurrentHpMp(player.getMaxHp(), player.getMaxMp());
		player.setCurrentCp(player.getMaxCp());
	}

	private static void storeMagicProgressionRun(int stage, BenchmarkResult r, CreatureSnapshot s, int passiveSkills) throws SQLException
	{
		final int sub1 = stage >= 1 ? MAGIC_PROGRESSION_CLASS_IDS[1] : -1;
		final int sub2 = stage >= 2 ? MAGIC_PROGRESSION_CLASS_IDS[2] : -1;
		final int sub3 = stage >= 3 ? MAGIC_PROGRESSION_CLASS_IDS[3] : -1;
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(INSERT_MAGIC_PROGRESSION_RUN))
		{
			int i = 1;
			ps.setInt(i++, stage); ps.setInt(i++, r.runNumber); ps.setLong(i++, System.currentTimeMillis()); ps.setString(i++, "CORE_ACCELERATED");
			ps.setString(i++, MAGIC_PROGRESSION_LABELS[stage]); ps.setInt(i++, MAGIC_PROGRESSION_CLASS_IDS[0]);
			ps.setInt(i++, sub1); ps.setInt(i++, sub2); ps.setInt(i++, sub3); ps.setInt(i++, stage + 1);
			ps.setInt(i++, r.charId); ps.setString(i++, r.charName); ps.setInt(i++, r.activeClassId); ps.setInt(i++, r.activeClassIndex); ps.setInt(i++, s.level);
			ps.setInt(i++, s.skillCount); ps.setInt(i++, passiveSkills); ps.setInt(i++, s.skillCount - passiveSkills);
			ps.setString(i++, r.equipmentKit); ps.setInt(i++, r.weaponId); ps.setString(i++, "Arcana Mace");
			ps.setDouble(i++, s.pAtk); ps.setDouble(i++, s.mAtk); ps.setDouble(i++, s.pDef); ps.setDouble(i++, s.mDef);
			ps.setDouble(i++, s.pAtkSpeed); ps.setDouble(i++, s.mAtkSpeed); ps.setDouble(i++, s.maxHp); ps.setDouble(i++, s.maxCp); ps.setDouble(i++, s.maxMp);
			ps.setInt(i++, r.durationSeconds); ps.setString(i++, r.rotation); ps.setInt(i++, r.actions); ps.setInt(i++, r.hits); ps.setInt(i++, r.casts);
			ps.setInt(i++, r.criticals); ps.setInt(i++, r.misses); ps.setInt(i++, r.bssUsed); ps.setDouble(i++, r.damageDealt);
			ps.setDouble(i++, r.damageDealt / Math.max(1, r.durationSeconds)); ps.setDouble(i++, r.mpUsed);
			ps.setString(i, "Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.");
			ps.executeUpdate();
		}
	}

	/**
	 * Phase 5A.3: compares the same Hurricane in every cumulative stage against
	 * the best nuke available to that build. This separates stat growth from the
	 * practical value of the accumulated skill catalog.
	 */
	private void runMagicComparison()
	{
		Player player = null;
		final PlayerClass restoreRoot = PlayerClass.getPlayerClass(38); // Dark Mystic.
		try
		{
			if (countMagicComparisonRuns() >= EXPECTED_MAGIC_COMPARISON_RUN_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 5A.3: comparacion magica completa (" + EXPECTED_MAGIC_COMPARISON_RUN_COUNT + "/" + EXPECTED_MAGIC_COMPARISON_RUN_COUNT + ").");
				return;
			}
			if (countMagicProgressionRuns() < EXPECTED_MAGIC_PROGRESSION_RUN_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 5A.3: espera a que termine la progresion 5A.2.");
				ThreadPool.schedule(this::runMagicComparison, 60000);
				return;
			}
			if (countOnlineCharacters() > 0)
			{
				LOGGER.info("Laboratorio L2 fase 5A.3: hay jugadores conectados; la comparacion se posterga.");
				ThreadPool.schedule(this::runMagicComparison, 60000);
				return;
			}
			final Npc atlas = getBenchmarkNpc(BENCHMARK_ATLAS_ID);
			if (atlas == null)
			{
				LOGGER.info("Laboratorio L2 fase 5A.3: espera a Atlas en el Coliseo.");
				ThreadPool.schedule(this::runMagicComparison, 60000);
				return;
			}

			final PlayerClass mainClass = PlayerClass.getPlayerClass(MAGIC_PROGRESSION_CLASS_IDS[0]);
			player = Player.load(findCharacterId(anchorForRoot(restoreRoot)));
			if ((player == null) || (mainClass == null))
			{
				throw new IllegalStateException("No se pudo cargar el ancla Dark Mystic o Storm Screamer.");
			}
			CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
			BENCHMARK_CAPTURE_IDS.add(player.getObjectId());
			prepareAnchor(player);
			configureCleanClass(player, mainClass, CLEAN_PROFILE_LEVEL);
			final Set<String> completedRuns = loadCompletedMagicComparisonRuns();
			int measured = completedRuns.size();

			for (int stage = 0; stage < MAGIC_PROGRESSION_CLASS_IDS.length; stage++)
			{
				if (stage > 0)
				{
					final PlayerClass subClass = PlayerClass.getPlayerClass(MAGIC_PROGRESSION_CLASS_IDS[stage]);
					if ((subClass == null) || !player.addSubClass(subClass.getId(), stage))
					{
						throw new IllegalStateException("No se pudo agregar Sub " + stage + " " + MAGIC_PROGRESSION_CLASS_IDS[stage] + ".");
					}
					player.setActiveClass(stage);
					maximizeActiveClass(player, CLEAN_PROFILE_LEVEL);
				}
				player.setActiveClass(0);
				cleanPairState(player);

				final List<Item> createdItems = new ArrayList<>();
				try
				{
					equipMagicProgressionKit(player, createdItems);
					final CreatureSnapshot snapshot = new CreatureSnapshot(player);
					int passiveSkills = 0;
					for (Skill skill : player.getAllSkills())
					{
						if (skill.isPassive())
						{
							passiveSkills++;
						}
					}

					for (String protocol : MAGIC_COMPARISON_PROTOCOLS)
					{
						final Skill selectedSkill = "FIXED_HURRICANE".equals(protocol) ? player.getKnownSkill(MAGIC_COMPARISON_FIXED_SKILL_ID) : selectDamageSkill(player, true);
						if (selectedSkill == null)
						{
							throw new IllegalStateException("No se encontro la skill para el protocolo " + protocol + " en la etapa " + stage + ".");
						}
						for (int runNumber = 1; runNumber <= MAGIC_COMPARISON_REPETITIONS; runNumber++)
						{
							final String runKey = stage + ":" + protocol + ":" + runNumber;
							if (completedRuns.contains(runKey))
							{
								continue;
							}
							final BenchmarkResult result = new BenchmarkResult(player, "magic-comparison-" + stage + "-" + protocol, runNumber,
								MAGIC_PROGRESSION_DURATION_SECONDS, BENCHMARK_ATLAS_ID, "Atlas", "S_ROBE", MAGIC_PROGRESSION_WEAPON_ID);
							cleanBenchmarkActors(player, atlas);
							runMagicalOutput(result, player, atlas, selectedSkill,
								"FIXED_HURRICANE".equals(protocol) ?
									"Skill fija Hurricane; formula magica real, MP finito y Blessed Spiritshot S." :
									"Mejor nuke por potencia/cadencia; formula magica real, MP finito y Blessed Spiritshot S.");
							storeMagicComparisonRun(stage, protocol, result, snapshot, passiveSkills, selectedSkill, player, atlas);
							completedRuns.add(runKey);
							measured++;
							LOGGER.info("Laboratorio L2 fase 5A.3: progreso " + measured + "/" + EXPECTED_MAGIC_COMPARISON_RUN_COUNT +
								" (" + MAGIC_PROGRESSION_LABELS[stage] + ", " + protocol + ").");
						}
					}
				}
				finally
				{
					removeBenchmarkKit(player, createdItems);
					cleanBenchmarkActors(player, atlas);
				}
			}
			LOGGER.info("Laboratorio L2 fase 5A.3: comparacion terminada; pasadas=" + countMagicComparisonRuns() + "/" + EXPECTED_MAGIC_COMPARISON_RUN_COUNT + ".");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 5A.3: no se pudo medir la comparacion magica.", e);
		}
		finally
		{
			if (player != null)
			{
				restoreBenchmarkAnchor(player, restoreRoot);
			}
		}
	}

	private static int countMagicComparisonRuns() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_magic_comparison_runs"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static Set<String> loadCompletedMagicComparisonRuns() throws SQLException
	{
		final Set<String> result = new HashSet<>();
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT stage_index,protocol,run_number FROM lab_magic_comparison_runs"); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(rs.getInt(1) + ":" + rs.getString(2) + ":" + rs.getInt(3));
			}
		}
		return result;
	}

	private static void storeMagicComparisonRun(int stage, String protocol, BenchmarkResult r, CreatureSnapshot s, int passiveSkills, Skill skill, Player player, Npc target) throws SQLException
	{
		final int sub1 = stage >= 1 ? MAGIC_PROGRESSION_CLASS_IDS[1] : -1;
		final int sub2 = stage >= 2 ? MAGIC_PROGRESSION_CLASS_IDS[2] : -1;
		final int sub3 = stage >= 3 ? MAGIC_PROGRESSION_CLASS_IDS[3] : -1;
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(INSERT_MAGIC_COMPARISON_RUN))
		{
			int i = 1;
			ps.setInt(i++, stage); ps.setString(i++, protocol); ps.setInt(i++, r.runNumber); ps.setLong(i++, System.currentTimeMillis());
			ps.setString(i++, "CORE_ACCELERATED"); ps.setString(i++, MAGIC_PROGRESSION_LABELS[stage]); ps.setInt(i++, MAGIC_PROGRESSION_CLASS_IDS[0]);
			ps.setInt(i++, sub1); ps.setInt(i++, sub2); ps.setInt(i++, sub3); ps.setInt(i++, stage + 1);
			ps.setInt(i++, r.charId); ps.setString(i++, r.charName); ps.setInt(i++, r.activeClassId); ps.setInt(i++, r.activeClassIndex); ps.setInt(i++, s.level);
			ps.setInt(i++, s.skillCount); ps.setInt(i++, passiveSkills); ps.setInt(i++, s.skillCount - passiveSkills);
			ps.setString(i++, r.equipmentKit); ps.setInt(i++, r.weaponId); ps.setString(i++, "Arcana Mace");
			ps.setDouble(i++, s.mAtk); ps.setDouble(i++, s.mAtkSpeed); ps.setDouble(i++, s.maxMp); ps.setInt(i++, r.durationSeconds);
			ps.setInt(i++, skill.getId()); ps.setInt(i++, skill.getLevel()); ps.setString(i++, skill.getName());
			ps.setDouble(i++, skill.getPower(player, target, false, false)); ps.setInt(i++, skillCycleMs(player, skill)); ps.setString(i++, r.rotation);
			ps.setInt(i++, r.actions); ps.setInt(i++, r.hits); ps.setInt(i++, r.casts); ps.setInt(i++, r.criticals);
			ps.setInt(i++, r.misses); ps.setInt(i++, r.bssUsed); ps.setDouble(i++, r.damageDealt);
			ps.setDouble(i++, r.damageDealt / Math.max(1, r.durationSeconds)); ps.setDouble(i++, r.mpUsed); ps.setString(i, r.notes);
			ps.executeUpdate();
		}
	}



	/**
	 * Phase 5A.4: establishes a human physical baseline while preserving the
	 * birth race through every class and subclass change. The table is keyed by
	 * racial anchor so the exact same build can later be repeated on other races.
	 */
	private void runPhysicalRaceBaseline()
	{
		if (countSafePhysicalRaceRuns() >= EXPECTED_PHYSICAL_RACE_RUN_COUNT)
		{
			LOGGER.info("Laboratorio L2 fase 5A.4: base fisica racial completa (" + EXPECTED_PHYSICAL_RACE_RUN_COUNT + "/" + EXPECTED_PHYSICAL_RACE_RUN_COUNT + ").");
			return;
		}
		try
		{
			if (countMagicComparisonRuns() < EXPECTED_MAGIC_COMPARISON_RUN_COUNT)
			{
				LOGGER.info("Laboratorio L2 fase 5A.4: espera a que termine la comparacion magica 5A.3.");
				ThreadPool.schedule(this::runPhysicalRaceBaseline, 60000);
				return;
			}
			if (countOnlineCharacters() > 0)
			{
				LOGGER.info("Laboratorio L2 fase 5A.4: hay jugadores conectados; la base fisica se posterga.");
				ThreadPool.schedule(this::runPhysicalRaceBaseline, 60000);
				return;
			}
			final Npc atlas = getBenchmarkNpc(BENCHMARK_ATLAS_ID);
			if (atlas == null)
			{
				LOGGER.info("Laboratorio L2 fase 5A.4: espera a Atlas en el Coliseo.");
				ThreadPool.schedule(this::runPhysicalRaceBaseline, 60000);
				return;
			}
			final Set<String> completedRuns = loadCompletedPhysicalRaceRuns();
			int measured = completedRuns.size();
			for (int rootId : PHYSICAL_RACE_ROOT_CLASS_IDS)
			{
				final PlayerClass restoreRoot = PlayerClass.getPlayerClass(rootId);
				final PlayerClass mainClass = PlayerClass.getPlayerClass(PHYSICAL_RACE_CLASS_IDS[0]);
				Player player = null;
				try
				{
					player = Player.load(findCharacterId(anchorForRoot(restoreRoot)));
					if ((player == null) || (restoreRoot == null) || (mainClass == null))
					{
						throw new IllegalStateException("No se pudo cargar el ancla racial o Dreadnought.");
					}
					final int expectedRaceId = restoreRoot.getRace().ordinal();
					final String expectedRaceName = restoreRoot.getRace().name();
					CONTROLLED_CAPTURE_IDS.add(player.getObjectId());
					BENCHMARK_CAPTURE_IDS.add(player.getObjectId());
					prepareAnchor(player);
					configureCleanClass(player, mainClass, CLEAN_PROFILE_LEVEL);

					for (int stage = 0; stage < PHYSICAL_RACE_CLASS_IDS.length; stage++)
					{
						if (stage > 0)
						{
							final PlayerClass subClass = PlayerClass.getPlayerClass(PHYSICAL_RACE_CLASS_IDS[stage]);
							if ((subClass == null) || !player.addSubClass(subClass.getId(), stage))
							{
								throw new IllegalStateException("No se pudo agregar Sub fisica " + stage + " " + PHYSICAL_RACE_CLASS_IDS[stage] + ".");
							}
							player.setActiveClass(stage);
							maximizeActiveClass(player, CLEAN_PROFILE_LEVEL);
						}
						player.setActiveClass(0);
						cleanPairState(player);

						final List<Item> createdItems = new ArrayList<>();
						try
						{
							equipPhysicalRaceKit(player, createdItems);
							final CreatureSnapshot snapshot = new CreatureSnapshot(player);
							if ((snapshot.raceId != expectedRaceId) || !expectedRaceName.equals(snapshot.raceName))
							{
								throw new IllegalStateException("La raza base cambio de " + expectedRaceName + " a " + snapshot.raceName + " en la etapa " + stage + ".");
							}
							int passiveSkills = 0;
							for (Skill skill : player.getAllSkills())
							{
								if (skill.isPassive())
								{
									passiveSkills++;
								}
							}
							final Skill bestSkill = selectCompatiblePhysicalDamageSkill(player, atlas);
							for (String protocol : PHYSICAL_RACE_PROTOCOLS)
							{
								for (int runNumber = 1; runNumber <= PHYSICAL_RACE_REPETITIONS; runNumber++)
								{
									final String runKey = rootId + ":" + stage + ":" + protocol + ":" + runNumber;
									if (completedRuns.contains(runKey))
									{
										continue;
									}
									final BenchmarkResult result = new BenchmarkResult(player, "physical-race-" + rootId + "-" + stage + "-" + protocol, runNumber,
										MAGIC_PROGRESSION_DURATION_SECONDS, BENCHMARK_ATLAS_ID, "Atlas", "S_HEAVY", PHYSICAL_RACE_WEAPON_ID);
									cleanBenchmarkActors(player, atlas);
									final Skill selectedSkill;
									if ("BEST_COMPATIBLE".equals(protocol) && (bestSkill != null))
									{
										selectedSkill = bestSkill;
										runPhysicalSkillOutput(result, player, atlas, bestSkill);
									}
									else
									{
										selectedSkill = null;
										runPhysicalOutput(result, player, atlas);
										if ("BEST_COMPATIBLE".equals(protocol))
										{
											result.notes = "No hubo skill fisica compatible; el mejor carril recurre al autoataque con Soulshot S.";
										}
									}
									storePhysicalRaceRun(rootId, stage, protocol, result, snapshot, passiveSkills, selectedSkill, player, atlas);
									completedRuns.add(runKey);
									measured++;
									LOGGER.info("Laboratorio L2 fase 5A.4: progreso " + measured + "/" + EXPECTED_PHYSICAL_RACE_RUN_COUNT +
										" (" + expectedRaceName + ", " + PHYSICAL_RACE_STAGE_LABELS[stage] + ", " + protocol + ").");
								}
							}
						}
						finally
						{
							removeBenchmarkKit(player, createdItems);
							cleanBenchmarkActors(player, atlas);
						}
					}
				}
				finally
				{
					if (player != null)
					{
						restoreBenchmarkAnchor(player, restoreRoot);
					}
				}
			}
			LOGGER.info("Laboratorio L2 fase 5A.4: base fisica racial terminada; pasadas=" + countPhysicalRaceRuns() + "/" + EXPECTED_PHYSICAL_RACE_RUN_COUNT + ".");
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 5A.4: no se pudo medir la base fisica racial.", e);
		}
	}

	private static int countSafePhysicalRaceRuns()
	{
		try
		{
			return countPhysicalRaceRuns();
		}
		catch (SQLException e)
		{
			return 0;
		}
	}

	private static int countPhysicalRaceRuns() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_physical_race_runs"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static Set<String> loadCompletedPhysicalRaceRuns() throws SQLException
	{
		final Set<String> result = new HashSet<>();
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT anchor_root_class_id,stage_index,protocol,run_number FROM lab_physical_race_runs"); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(rs.getInt(1) + ":" + rs.getInt(2) + ":" + rs.getString(3) + ":" + rs.getInt(4));
			}
		}
		return result;
	}

	private static void equipPhysicalRaceKit(Player player, List<Item> createdItems)
	{
		for (int itemId : HEAVY_ARMOR_IDS)
		{
			addAndEquipBenchmarkItem(player, itemId, createdItems);
		}
		for (int itemId : COMMON_JEWELRY_IDS)
		{
			addAndEquipBenchmarkItem(player, itemId, createdItems);
		}
		addAndEquipBenchmarkItem(player, PHYSICAL_RACE_WEAPON_ID, createdItems);
		player.setCurrentHpMp(player.getMaxHp(), player.getMaxMp());
		player.setCurrentCp(player.getMaxCp());
	}

	private static Skill selectCompatiblePhysicalDamageSkill(Player player, Npc target)
	{
		Skill best = null;
		double bestScore = -1;
		for (Skill skill : player.getAllSkills())
		{
			if (skill.isPassive() || !skill.isDamage() || skill.isSuicideAttack() || skill.isMagic())
			{
				continue;
			}
			try
			{
				if (!skill.checkCondition(player, target, false))
				{
					continue;
				}
			}
			catch (RuntimeException e)
			{
				continue;
			}
			final double power = Math.max(0, skill.getPower(player, target, false, false));
			final double score = power / Math.max(1, skillCycleMs(player, skill));
			if (score > bestScore)
			{
				best = skill;
				bestScore = score;
			}
		}
		return best;
	}

	private static void runPhysicalSkillOutput(BenchmarkResult result, Player player, Npc target, Skill skill)
	{
		final int cycle = skillCycleMs(player, skill);
		final int mpCost = skillMpCost(skill);
		int casts = Math.max(1, (result.durationSeconds * 1000) / cycle);
		if (mpCost > 0)
		{
			casts = Math.min(casts, Math.max(1, player.getMaxMp() / mpCost));
		}
		result.rotation = skill.getId() + ":" + skill.getLevel() + " " + skill.getName() + "+Soulshot_S";
		result.actions = casts;
		result.casts = casts;
		result.soulshotsUsed = casts;
		result.mpUsed = (double) casts * mpCost;
		for (int i = 0; i < casts; i++)
		{
			if (Formulas.calcHitMiss(player, target))
			{
				result.misses++;
				continue;
			}
			final boolean critical = Formulas.calcCrit(player, target);
			final double damage = Formulas.calcPhysDam(player, target, skill, Formulas.calcShldUse(player, target), critical, true);
			result.hits++;
			result.damageDealt += Math.max(0, damage);
			if (critical)
			{
				result.criticals++;
			}
		}
		result.ownerDamage = result.damageDealt;
		result.notes = "Mejor skill fisica compatible con Saint Spear; formula fisica real, MP finito y Soulshot S.";
	}

	private static void storePhysicalRaceRun(int rootId, int stage, String protocol, BenchmarkResult r, CreatureSnapshot s, int passiveSkills, Skill skill, Player player, Npc target) throws SQLException
	{
		final int sub1 = stage >= 1 ? PHYSICAL_RACE_CLASS_IDS[1] : -1;
		final int sub2 = stage >= 2 ? PHYSICAL_RACE_CLASS_IDS[2] : -1;
		final int sub3 = stage >= 3 ? PHYSICAL_RACE_CLASS_IDS[3] : -1;
		final int skillId = skill != null ? skill.getId() : 0;
		final int skillLevel = skill != null ? skill.getLevel() : 0;
		final String skillName = skill != null ? skill.getName() : "Autoattack";
		final double skillPower = skill != null ? skill.getPower(player, target, false, false) : 0;
		final int cycle = skill != null ? skillCycleMs(player, skill) : Math.max(250, player.calculateTimeBetweenAttacks());
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(INSERT_PHYSICAL_RACE_RUN))
		{
			int i = 1;
			ps.setInt(i++, rootId); ps.setInt(i++, s.raceId); ps.setString(i++, s.raceName); ps.setInt(i++, stage);
			ps.setString(i++, protocol); ps.setInt(i++, r.runNumber); ps.setLong(i++, System.currentTimeMillis()); ps.setString(i++, "CORE_ACCELERATED");
			ps.setString(i++, PHYSICAL_RACE_STAGE_LABELS[stage]); ps.setInt(i++, PHYSICAL_RACE_CLASS_IDS[0]);
			ps.setInt(i++, sub1); ps.setInt(i++, sub2); ps.setInt(i++, sub3); ps.setInt(i++, stage + 1);
			ps.setInt(i++, r.charId); ps.setString(i++, r.charName); ps.setInt(i++, r.activeClassId); ps.setInt(i++, r.activeClassIndex); ps.setInt(i++, s.level);
			ps.setInt(i++, s.skillCount); ps.setInt(i++, passiveSkills); ps.setInt(i++, s.skillCount - passiveSkills);
			ps.setString(i++, r.equipmentKit); ps.setInt(i++, r.weaponId); ps.setString(i++, "Saint Spear");
			ps.setDouble(i++, s.pAtk); ps.setDouble(i++, s.pAtkSpeed); ps.setDouble(i++, s.pCritical); ps.setInt(i++, s.accuracy);
			ps.setDouble(i++, s.maxHp); ps.setDouble(i++, s.maxCp); ps.setDouble(i++, s.maxMp);
			ps.setInt(i++, s.statStr); ps.setInt(i++, s.statDex); ps.setInt(i++, s.statCon); ps.setInt(i++, r.durationSeconds);
			ps.setInt(i++, skillId); ps.setInt(i++, skillLevel); ps.setString(i++, skillName); ps.setDouble(i++, skillPower); ps.setInt(i++, cycle);
			ps.setString(i++, r.rotation); ps.setInt(i++, r.actions); ps.setInt(i++, r.hits); ps.setInt(i++, r.casts); ps.setInt(i++, r.criticals);
			ps.setInt(i++, r.misses); ps.setInt(i++, r.soulshotsUsed); ps.setDouble(i++, r.damageDealt);
			ps.setDouble(i++, r.damageDealt / Math.max(1, r.durationSeconds)); ps.setDouble(i++, r.mpUsed); ps.setString(i, r.notes);
			ps.executeUpdate();
		}
	}

	private static int countBenchmarkCases() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_combat_benchmark_plan"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static int countBenchmarkRuns() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM lab_combat_benchmark_runs"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static int countOnlineCharacters() throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT COUNT(*) FROM characters WHERE online=1"); ResultSet rs = ps.executeQuery())
		{
			return rs.next() ? rs.getInt(1) : 0;
		}
	}

	private static Set<String> loadCompletedBenchmarkRuns() throws SQLException
	{
		final Set<String> result = new HashSet<>();
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("SELECT case_id,run_number FROM lab_combat_benchmark_runs"); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(rs.getString(1) + ":" + rs.getInt(2));
			}
		}
		return result;
	}

	private static List<BenchmarkCase> loadBenchmarkCases() throws SQLException
	{
		final List<BenchmarkCase> result = new ArrayList<>(EXPECTED_BENCHMARK_CASE_COUNT);
		final String sql = "SELECT case_id,finalist_rank,category,main_class_id,sub1_class_id,sub2_class_id,sub3_class_id," +
			"active_class_id,active_class_index,benchmark_code,opponent_id,opponent_name,equipment_kit,weapon_id,duration_seconds,repetitions " +
			"FROM lab_combat_benchmark_plan ORDER BY finalist_rank,priority";
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(sql); ResultSet rs = ps.executeQuery())
		{
			while (rs.next())
			{
				result.add(new BenchmarkCase(rs));
			}
		}
		return result;
	}

	private static Npc getBenchmarkNpc(int npcId)
	{
		return SpawnTable.getInstance().getAnySpawn(npcId) != null ? SpawnTable.getInstance().getAnySpawn(npcId).getLastSpawn() : null;
	}

	private static String anchorForRoot(PlayerClass root)
	{
		for (int index = 0; index < ANCHOR_ROOT_CLASS_IDS.length; index++)
		{
			if (ANCHOR_ROOT_CLASS_IDS[index] == root.getId())
			{
				return ANCHOR_NAMES[index];
			}
		}
		throw new IllegalArgumentException("No existe ancla para la raiz " + root.getId() + ".");
	}

	private static void configureBenchmarkBuild(Player player, BenchmarkCase benchmark) throws Exception
	{
		prepareAnchor(player);
		configureCleanClass(player, benchmark.main, CLEAN_PROFILE_LEVEL);
		for (int index = 1; index <= 3; index++)
		{
			final PlayerClass subClass = benchmark.classAt(index);
			if (!player.addSubClass(subClass.getId(), index))
			{
				throw new IllegalStateException("No se pudo agregar Sub " + index + " " + subClass.getId() + ".");
			}
			player.setActiveClass(index);
			maximizeActiveClass(player, CLEAN_PROFILE_LEVEL);
		}
		player.setActiveClass(benchmark.activeClassIndex);
		cleanPairState(player);
	}

	private static void restoreBenchmarkAnchor(Player player, PlayerClass root)
	{
		try
		{
			cleanBenchmarkActors(player);
			prepareAnchor(player);
			configureCleanClass(player, root, 1);
		}
		catch (Exception e)
		{
			LOGGER.log(Level.WARNING, "Laboratorio L2 fase 4D: no se pudo restaurar " + player.getName() + ".", e);
		}
		finally
		{
			BENCHMARK_CAPTURE_IDS.remove(player.getObjectId());
			CONTROLLED_CAPTURE_IDS.remove(player.getObjectId());
			Disconnection.of(player).storeAndDelete();
		}
	}

	private static void equipBenchmarkKit(Player player, BenchmarkCase benchmark, List<Item> createdItems)
	{
		final int[] armor = switch (benchmark.equipmentKit)
		{
			case "S_ROBE" -> ROBE_ARMOR_IDS;
			case "S_LIGHT" -> LIGHT_ARMOR_IDS;
			default -> HEAVY_ARMOR_IDS;
		};
		for (int itemId : armor)
		{
			addAndEquipBenchmarkItem(player, itemId, createdItems);
		}
		for (int itemId : COMMON_JEWELRY_IDS)
		{
			addAndEquipBenchmarkItem(player, itemId, createdItems);
		}
		addAndEquipBenchmarkItem(player, benchmark.weaponId, createdItems);
		if (SHIELD_CLASS_IDS.contains(benchmark.activeClassId))
		{
			addAndEquipBenchmarkItem(player, 6377, createdItems);
		}
		player.setCurrentHpMp(player.getMaxHp(), player.getMaxMp());
		player.setCurrentCp(player.getMaxCp());
	}

	private static void addAndEquipBenchmarkItem(Player player, int itemId, List<Item> createdItems)
	{
		final Item item = player.getInventory().addItem(ItemProcessType.NONE, itemId, 1, player, null);
		if (item == null)
		{
			throw new IllegalStateException("No se pudo crear el objeto de benchmark " + itemId + ".");
		}
		item.setEnchantLevel(0);
		createdItems.add(item);
		player.getInventory().equipItem(item);
	}

	private static void removeBenchmarkKit(Player player, List<Item> createdItems)
	{
		for (int slot = 0; slot < Inventory.PAPERDOLL_TOTALSLOTS; slot++)
		{
			player.getInventory().unEquipItemInSlot(slot);
		}
		for (Item item : createdItems)
		{
			player.getInventory().destroyItem(ItemProcessType.NONE, item, player, null);
		}
		createdItems.clear();
	}

	private static void cleanBenchmarkActors(Creature... actors)
	{
		for (Creature actor : actors)
		{
			if (actor == null)
			{
				continue;
			}
			if (actor instanceof Player)
			{
				final Summon summon = ((Player) actor).getSummon();
				if (summon != null)
				{
					summon.unSummon((Player) actor);
				}
			}
			actor.stopAllEffects();
			actor.setCurrentHpMp(actor.getMaxHp(), actor.getMaxMp());
			actor.setCurrentCp(actor.getMaxCp());
		}
	}

	private static BenchmarkResult executeBenchmarkRun(Player player, BenchmarkCase benchmark, int runNumber, Npc atlas, Npc ares, Npc nyx)
	{
		cleanBenchmarkActors(player, atlas, ares, nyx);
		final BenchmarkResult result = new BenchmarkResult(player, benchmark, runNumber);
		switch (benchmark.code)
		{
			case "salida_fisica" -> runPhysicalOutput(result, player, atlas);
			case "salida_magica" -> runMagicalOutput(result, player, atlas);
			case "soporte_sostenido" -> runSupportOutput(result, player);
			case "salida_invocacion" -> runSummonOutput(result, player, atlas);
			case "resistencia_ares" -> runSurvival(result, player, ares, new int[] {8, 6, 9, 261, 1}, 1.0);
			case "resistencia_nyx" -> runSurvival(result, player, nyx, new int[] {337, 1064, 1074, 1341, 1239, 1291, 1159}, 1.0);
			default -> throw new IllegalArgumentException("Protocolo 4D desconocido: " + benchmark.code);
		}
		cleanBenchmarkActors(player, atlas, ares, nyx);
		return result;
	}

	private static void runPhysicalOutput(BenchmarkResult result, Player player, Npc target)
	{
		final int delay = Math.max(250, player.calculateTimeBetweenAttacks());
		final int actions = Math.max(1, (result.durationSeconds * 1000) / delay);
		result.rotation = "ataque_basico+Soulshot_S";
		result.actions = actions;
		result.soulshotsUsed = actions;
		for (int i = 0; i < actions; i++)
		{
			if (Formulas.calcHitMiss(player, target))
			{
				result.misses++;
				continue;
			}
			final boolean critical = Formulas.calcCrit(player, target);
			final double damage = Formulas.calcPhysDam(player, target, null, Formulas.calcShldUse(player, target), critical, true);
			result.hits++;
			result.damageDealt += Math.max(0, damage);
			if (critical)
			{
				result.criticals++;
			}
		}
		result.ownerDamage = result.damageDealt;
		result.notes = "Autoataque normalizado con arma S real; cadencia del nucleo y Soulshot S por golpe.";
	}

	private static void runMagicalOutput(BenchmarkResult result, Player player, Npc target)
	{
		final Skill skill = selectDamageSkill(player, true);
		runMagicalOutput(result, player, target, skill, "Mejor nuke por potencia/cadencia; formula magica real, MP finito y Blessed Spiritshot S.");
	}

	private static void runMagicalOutput(BenchmarkResult result, Player player, Npc target, Skill skill, String notes)
	{
		if (skill == null)
		{
			throw new IllegalStateException("La clase " + player.getPlayerClass().getId() + " no tiene una skill magica de dano.");
		}
		final int cycle = skillCycleMs(player, skill);
		final int mpCost = skillMpCost(skill);
		int casts = Math.max(1, (result.durationSeconds * 1000) / cycle);
		if (mpCost > 0)
		{
			casts = Math.min(casts, Math.max(1, player.getMaxMp() / mpCost));
		}
		result.rotation = skill.getId() + ":" + skill.getLevel() + " " + skill.getName() + "+Blessed_Spiritshot_S";
		result.actions = casts;
		result.casts = casts;
		result.bssUsed = casts;
		result.mpUsed = (double) casts * mpCost;
		for (int i = 0; i < casts; i++)
		{
			final boolean critical = Formulas.calcMCrit(player.getMCriticalHit(target, skill));
			final double damage = Formulas.calcMagicDam(player, target, skill, Formulas.calcShldUse(player, target, skill), false, true, critical);
			result.damageDealt += Math.max(0, damage);
			if (damage <= 1)
			{
				result.misses++;
			}
			else
			{
				result.hits++;
			}
			if (critical)
			{
				result.criticals++;
			}
		}
		result.ownerDamage = result.damageDealt;
		result.notes = notes;
	}

	private static void runSupportOutput(BenchmarkResult result, Player player)
	{
		Skill best = null;
		double bestHeal = 0;
		double bestScore = -1;
		for (Skill skill : player.getAllSkills())
		{
			if (skill.isPassive() || !skill.hasEffectType(EffectType.HEAL))
			{
				continue;
			}
			final double heal = calculateDirectHeal(player, skill);
			final double score = heal / Math.max(1, skillCycleMs(player, skill));
			if (score > bestScore)
			{
				best = skill;
				bestHeal = heal;
				bestScore = score;
			}
		}
		if ((best == null) || (bestHeal <= 0))
		{
			throw new IllegalStateException("La clase " + player.getPlayerClass().getId() + " no produjo una curacion medible.");
		}
		final int mpCost = skillMpCost(best);
		int casts = Math.max(1, (result.durationSeconds * 1000) / skillCycleMs(player, best));
		if (mpCost > 0)
		{
			casts = Math.min(casts, Math.max(1, player.getMaxMp() / mpCost));
		}
		final double deficit = player.getMaxHp() * 0.5;
		result.rotation = best.getId() + ":" + best.getLevel() + " " + best.getName() + "+Blessed_Spiritshot_S";
		result.actions = casts;
		result.casts = casts;
		result.bssUsed = casts;
		result.effectiveHeal = Math.min(bestHeal, deficit) * casts;
		result.overheal = Math.max(0, bestHeal - deficit) * casts;
		result.mpUsed = (double) casts * mpCost;
		result.notes = "Curacion calculada con la misma formula y potencia del effect handler; aliado controlado al 50% de HP, MP finito.";
	}

	private static double calculateDirectHeal(Player player, Skill skill)
	{
		double power = 0;
		for (EffectScope scope : EffectScope.values())
		{
			final List<AbstractEffect> effects = skill.getEffects(scope);
			if (effects == null)
			{
				continue;
			}
			for (AbstractEffect effect : effects)
			{
				if (effect.getEffectType() != EffectType.HEAL)
				{
					continue;
				}
				try
				{
					final java.lang.reflect.Field powerField = effect.getClass().getDeclaredField("_power");
					powerField.setAccessible(true);
					power = Math.max(power, powerField.getDouble(effect));
				}
				catch (ReflectiveOperationException e)
				{
					throw new IllegalStateException("No se pudo leer la potencia Heal de " + skill.getId() + ":" + skill.getLevel() + ".", e);
				}
			}
		}
		if (power <= 0)
		{
			return 0;
		}
		double amount = power;
		if (!skill.isStatic())
		{
			amount += (skill.getMpConsume() * 2.4) + Math.sqrt(4 * player.getMAtk(player, null));
			amount = player.calcStat(Stat.HEAL_EFFECT, amount, null, null);
			if (skill.getItemConsumeCount() <= 0)
			{
				amount *= ClassBalanceConfig.PLAYER_HEALING_SKILL_MULTIPLIERS[player.getPlayerClass().getId()];
			}
		}
		return Math.max(0, amount);
	}

	private static void runSummonOutput(BenchmarkResult result, Player player, Npc target)
	{
		Skill summonSkill = null;
		for (Skill skill : player.getAllSkills())
		{
			if (!skill.isPassive() && hasEffectNamed(skill, "Summon"))
			{
				if ((summonSkill == null) || (skill.getLevel() > summonSkill.getLevel()))
				{
					summonSkill = skill;
				}
			}
		}
		if (summonSkill == null)
		{
			throw new IllegalStateException("La clase " + player.getPlayerClass().getId() + " no tiene invocacion.");
		}
		summonSkill.activateSkill(player, Collections.<WorldObject>singletonList(player));
		final Summon summon = player.getSummon();
		if (summon == null)
		{
			throw new IllegalStateException("La skill " + summonSkill.getId() + " no creo una invocacion.");
		}
		final int petDelay = Math.max(250, summon.calculateTimeBetweenAttacks());
		final int petActions = Math.max(1, (result.durationSeconds * 1000) / petDelay);
		for (int i = 0; i < petActions; i++)
		{
			if (Formulas.calcHitMiss(summon, target))
			{
				result.misses++;
				continue;
			}
			final boolean critical = Formulas.calcCrit(summon, target);
			result.summonDamage += Math.max(0, Formulas.calcPhysDam(summon, target, null, Formulas.calcShldUse(summon, target), critical, true));
			result.hits++;
			if (critical)
			{
				result.criticals++;
			}
		}
		final Skill ownerSkill = selectDamageSkill(player, true);
		int ownerCasts = 0;
		if (ownerSkill != null)
		{
			final int mpCost = skillMpCost(ownerSkill);
			ownerCasts = Math.max(1, (result.durationSeconds * 1000) / skillCycleMs(player, ownerSkill));
			if (mpCost > 0)
			{
				ownerCasts = Math.min(ownerCasts, Math.max(1, (player.getMaxMp() - skillMpCost(summonSkill)) / mpCost));
			}
			for (int i = 0; i < ownerCasts; i++)
			{
				final boolean critical = Formulas.calcMCrit(player.getMCriticalHit(target, ownerSkill));
				result.ownerDamage += Math.max(0, Formulas.calcMagicDam(player, target, ownerSkill, Formulas.calcShldUse(player, target, ownerSkill), false, true, critical));
				if (critical)
				{
					result.criticals++;
				}
			}
			result.mpUsed = skillMpCost(summonSkill) + ((double) ownerCasts * mpCost);
			result.bssUsed = ownerCasts;
		}
		result.soulshotsUsed = petActions;
		result.casts = ownerCasts + 1;
		result.actions = petActions + ownerCasts + 1;
		result.damageDealt = result.ownerDamage + result.summonDamage;
		result.summonUptime = result.durationSeconds;
		result.rotation = summonSkill.getId() + ":" + summonSkill.getLevel() + " " + summonSkill.getName() + "+ataque_invocacion" + (ownerSkill != null ? "+" + ownerSkill.getId() + ":" + ownerSkill.getLevel() : "");
		result.notes = "Invocacion creada por el handler real; dano del pet y del dueno almacenados por separado.";
		summon.unSummon(player);
	}

	private static boolean hasEffectNamed(Skill skill, String simpleClassName)
	{
		for (EffectScope scope : EffectScope.values())
		{
			final List<AbstractEffect> effects = skill.getEffects(scope);
			if (effects == null)
			{
				continue;
			}
			for (AbstractEffect effect : effects)
			{
				if (effect.getClass().getSimpleName().equals(simpleClassName))
				{
					return true;
				}
			}
		}
		return false;
	}

	private static void runSurvival(BenchmarkResult result, Player player, Npc opponent, int[] rotationIds, double damageScale)
	{
		final double pool = player.getMaxHp() + player.getMaxCp();
		double elapsed = 0;
		double accumulatedDamage = 0;
		int rotationIndex = 0;
		final List<String> used = new ArrayList<>();
		final Map<Integer, Double> readyAt = new HashMap<>();
		int safety = 0;
		while ((elapsed < result.durationSeconds) && (accumulatedDamage < pool) && (++safety < 1000))
		{
			Skill skill = null;
			double nextReady = Double.MAX_VALUE;
			for (int scan = 0; scan < rotationIds.length; scan++)
			{
				final int skillId = rotationIds[rotationIndex++ % rotationIds.length];
				final Skill candidate = opponent.getKnownSkill(skillId);
				if (candidate == null)
				{
					continue;
				}
				final double candidateReady = readyAt.getOrDefault(skillId, 0.0);
				nextReady = Math.min(nextReady, candidateReady);
				if (candidateReady <= elapsed)
				{
					skill = candidate;
					break;
				}
			}
			if (skill == null)
			{
				if ((nextReady == Double.MAX_VALUE) || (nextReady >= result.durationSeconds))
				{
					break;
				}
				elapsed = Math.max(elapsed + 0.001, nextReady);
				continue;
			}
			final double actionSeconds = skillCastMs(opponent, skill, skill.isMagic()) / 1000.0;
			if ((elapsed + actionSeconds) > result.durationSeconds)
			{
				break;
			}
			final double remaining = result.durationSeconds - elapsed;
			if (!used.contains(skill.getId() + ":" + skill.getLevel()))
			{
				used.add(skill.getId() + ":" + skill.getLevel());
			}
			if (skill.isDamage())
			{
				double damage = 0;
				if (skill.isMagic())
				{
					final boolean critical = Formulas.calcMCrit(opponent.getMCriticalHit(player, skill));
					damage = Formulas.calcMagicDam(opponent, player, skill, Formulas.calcShldUse(opponent, player, skill), false, true, critical);
					result.bssUsed++;
					if (critical)
					{
						result.criticals++;
					}
				}
				else
				{
					result.soulshotsUsed++;
					if (!Formulas.calcPhysicalSkillEvasion(opponent, player, skill))
					{
						final boolean critical = Formulas.calcCrit(opponent, player, skill);
						damage = Formulas.calcPhysDam(opponent, player, skill, Formulas.calcShldUse(opponent, player, skill), critical, true);
						if (critical)
						{
							result.criticals++;
						}
					}
				}
				damage = Math.max(0, damage) * damageScale;
				accumulatedDamage += damage;
				result.hits += damage > 0 ? 1 : 0;
				result.misses += damage > 0 ? 0 : 1;
				result.casts++;
			}
			else
			{
				final Creature target = skill.isDebuff() ? player : opponent;
				skill.activateSkill(opponent, Collections.<WorldObject>singletonList(target));
				if ((target == player) && player.isAffectedBySkill(skill.getId()))
				{
					result.controlTime += Math.min(remaining, Math.max(0, skill.getAbnormalTime()));
				}
				result.casts++;
			}
				result.actions++;
			readyAt.put(skill.getId(), elapsed + (skillReuseMs(opponent, skill) / 1000.0));
			elapsed += Math.max(0.25, actionSeconds);
		}
		result.damageReceived = accumulatedDamage;
		result.timeAlive = accumulatedDamage >= pool ? Math.min(result.durationSeconds, elapsed) : result.durationSeconds;
		result.hpCpRemaining = Math.max(0, pool - accumulatedDamage);
		result.rotation = String.join(",", used);
		result.notes = "Rotacion real del NPC acelerada; buffs y debuffs persisten dentro de cada pasada.";
		player.stopAllEffects();
		opponent.stopAllEffects();
	}

	private static Skill selectDamageSkill(Creature creature, boolean magical)
	{
		Skill best = null;
		double bestScore = -1;
		for (Skill skill : creature.getAllSkills())
		{
			if (skill.isPassive() || !skill.isDamage() || skill.isSuicideAttack() || (magical != skill.isMagic()))
			{
				continue;
			}
			final double power = Math.max(0, skill.getPower(creature, creature, false, false));
			final double score = power / Math.max(1, skillCycleMs(creature, skill));
			if (score > bestScore)
			{
				best = skill;
				bestScore = score;
			}
		}
		return best;
	}

	private static int skillMpCost(Skill skill)
	{
		return Math.max(0, skill.getMpInitialConsume()) + Math.max(0, skill.getMpConsume());
	}

	private static int skillCycleMs(Creature creature, Skill skill)
	{
		return Math.max(skillCastMs(creature, skill, skill.isMagic()), skillReuseMs(creature, skill));
	}

	private static int skillCastMs(Creature creature, Skill skill, boolean chargedMagicShot)
	{
		final int baseTime = skill.getHitTime() + skill.getCoolTime();
		int castTime = skill.isStatic() ? baseTime : Formulas.calcAtkSpd(creature, skill, baseTime);
		if (skill.isMagic() && chargedMagicShot)
		{
			castTime = (int) (castTime * 0.7);
		}
		if (skill.isMagic() && (baseTime > 550) && (castTime < 550))
		{
			castTime = 550;
		}
		else if (!skill.isStatic() && (baseTime >= 500) && (castTime < 500))
		{
			castTime = 500;
		}
		return Math.max(250, castTime);
	}

	private static int skillReuseMs(Creature creature, Skill skill)
	{
		if (skill.isStaticReuse() || skill.isStatic())
		{
			return Math.max(0, skill.getReuseDelay());
		}
		double reuse = skill.getReuseDelay();
		if (skill.isMagic())
		{
			reuse *= creature.calcStat(Stat.MAGIC_REUSE_RATE, 1, null, null) * 333.0 / Math.max(1, creature.getMAtkSpd());
		}
		else if (skill.isPhysical())
		{
			reuse *= creature.calcStat(Stat.P_REUSE, 1, null, null) * 333.0 / Math.max(1, creature.getPAtkSpd());
		}
		else
		{
			reuse *= creature.calcStat(Stat.DANCE_REUSE, 1, null, null) * 333.0 / Math.max(1, creature.getPAtkSpd());
		}
		return (int) Math.max(0, reuse);
	}

	private static void storeBenchmarkRun(BenchmarkResult r) throws SQLException
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(INSERT_BENCHMARK_RUN))
		{
			int i = 1;
			ps.setString(i++, r.caseId); ps.setInt(i++, r.runNumber); ps.setLong(i++, System.currentTimeMillis()); ps.setString(i++, "CORE_ACCELERATED");
			ps.setInt(i++, r.durationSeconds); ps.setInt(i++, r.charId); ps.setString(i++, r.charName); ps.setInt(i++, r.activeClassId); ps.setInt(i++, r.activeClassIndex);
			ps.setInt(i++, r.opponentId); ps.setString(i++, r.opponentName); ps.setString(i++, r.equipmentKit); ps.setInt(i++, r.weaponId); ps.setString(i++, r.rotation);
			ps.setInt(i++, r.actions); ps.setInt(i++, r.hits); ps.setInt(i++, r.casts); ps.setInt(i++, r.criticals); ps.setInt(i++, r.misses);
			ps.setInt(i++, r.soulshotsUsed); ps.setInt(i++, r.bssUsed); ps.setDouble(i++, r.damageDealt); ps.setDouble(i++, r.ownerDamage); ps.setDouble(i++, r.summonDamage);
			ps.setDouble(i++, r.damageReceived); ps.setDouble(i++, r.effectiveHeal); ps.setDouble(i++, r.overheal); ps.setDouble(i++, r.mpUsed); ps.setDouble(i++, r.timeAlive);
			ps.setDouble(i++, r.hpCpRemaining); ps.setDouble(i++, r.controlTime); ps.setDouble(i++, r.summonUptime); ps.setString(i, r.notes);
			ps.executeUpdate();
		}
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement("UPDATE lab_combat_benchmark_plan p SET completed_runs=(SELECT COUNT(*) FROM lab_combat_benchmark_runs r WHERE r.case_id=p.case_id),status=IF((SELECT COUNT(*) FROM lab_combat_benchmark_runs r WHERE r.case_id=p.case_id)>=p.repetitions,'COMPLETE','RUNNING') WHERE p.case_id=?"))
		{
			ps.setString(1, r.caseId);
			ps.executeUpdate();
		}
	}

	private static final class BenchmarkCase
	{
		private final String caseId;
		private final int finalistRank;
		private final String category;
		private final PlayerClass main;
		private final PlayerClass sub1;
		private final PlayerClass sub2;
		private final PlayerClass sub3;
		private final int activeClassId;
		private final int activeClassIndex;
		private final String code;
		private final int opponentId;
		private final String opponentName;
		private final String equipmentKit;
		private final int weaponId;
		private final int durationSeconds;
		private final int repetitions;

		private BenchmarkCase(ResultSet rs) throws SQLException
		{
			caseId = rs.getString(1); finalistRank = rs.getInt(2); category = rs.getString(3);
			main = PlayerClass.getPlayerClass(rs.getInt(4)); sub1 = PlayerClass.getPlayerClass(rs.getInt(5)); sub2 = PlayerClass.getPlayerClass(rs.getInt(6)); sub3 = PlayerClass.getPlayerClass(rs.getInt(7));
			activeClassId = rs.getInt(8); activeClassIndex = rs.getInt(9); code = rs.getString(10); opponentId = rs.getInt(11); opponentName = rs.getString(12);
			equipmentKit = rs.getString(13); weaponId = rs.getInt(14); durationSeconds = rs.getInt(15); repetitions = rs.getInt(16);
			if ((classAt(activeClassIndex) == null) || (classAt(activeClassIndex).getId() != activeClassId))
			{
				throw new SQLException("Caso 4D invalido " + caseId + ": clase activa fuera de la build.");
			}
		}

		private PlayerClass classAt(int index)
		{
			return switch (index)
			{
				case 0 -> main;
				case 1 -> sub1;
				case 2 -> sub2;
				case 3 -> sub3;
				default -> null;
			};
		}

		private String buildKey()
		{
			return main.getId() + ":" + sub1.getId() + ":" + sub2.getId() + ":" + sub3.getId();
		}
	}

	private static final class BenchmarkResult
	{
		private final String caseId;
		private final int runNumber;
		private final int durationSeconds;
		private final int charId;
		private final String charName;
		private final int activeClassId;
		private final int activeClassIndex;
		private final int opponentId;
		private final String opponentName;
		private final String equipmentKit;
		private final int weaponId;
		private String rotation = "";
		private int actions;
		private int hits;
		private int casts;
		private int criticals;
		private int misses;
		private int soulshotsUsed;
		private int bssUsed;
		private double damageDealt;
		private double ownerDamage;
		private double summonDamage;
		private double damageReceived;
		private double effectiveHeal;
		private double overheal;
		private double mpUsed;
		private double timeAlive;
		private double hpCpRemaining;
		private double controlTime;
		private double summonUptime;
		private String notes = "";

		private BenchmarkResult(Player player, BenchmarkCase benchmark, int number)
		{
			caseId = benchmark.caseId; runNumber = number; durationSeconds = benchmark.durationSeconds;
			charId = player.getObjectId(); charName = player.getName(); activeClassId = benchmark.activeClassId; activeClassIndex = benchmark.activeClassIndex;
			opponentId = benchmark.opponentId; opponentName = benchmark.opponentName; equipmentKit = benchmark.equipmentKit; weaponId = benchmark.weaponId;
		}

		private BenchmarkResult(Player player, String id, int number, int seconds, int targetId, String targetName, String kit, int itemId)
		{
			caseId = id; runNumber = number; durationSeconds = seconds;
			charId = player.getObjectId(); charName = player.getName(); activeClassId = player.getPlayerClass().getId(); activeClassIndex = player.getClassIndex();
			opponentId = targetId; opponentName = targetName; equipmentKit = kit; weaponId = itemId;
		}
	}

	private static final class FourClassBuild
	{
		private final PlayerClass main;
		private final PlayerClass sub1;
		private final PlayerClass sub2;
		private final PlayerClass sub3;
		private final String bucket;
		private final int expectedSkillCount;
		private final String expectedSkillHash;
		private final String expectedSkillKey;

		private FourClassBuild(int mainId, int sub1Id, int sub2Id, int sub3Id, String selectionBucket, int skillCount, String skillHash, String skillKey)
		{
			main = PlayerClass.getPlayerClass(mainId);
			sub1 = PlayerClass.getPlayerClass(sub1Id);
			sub2 = PlayerClass.getPlayerClass(sub2Id);
			sub3 = PlayerClass.getPlayerClass(sub3Id);
			bucket = selectionBucket;
			expectedSkillCount = skillCount;
			expectedSkillHash = skillHash;
			expectedSkillKey = skillKey;
		}

		private boolean isValid()
		{
			return (main != null) && (sub1 != null) && (sub2 != null) && (sub3 != null) && (main.level() == 3) && (sub1.level() == 3) && (sub2.level() == 3) && (sub3.level() == 3) &&
				(main != sub1) && (main != sub2) && (main != sub3) && (sub1 != sub2) && (sub1 != sub3) && (sub2 != sub3) &&
				(expectedSkillCount > 0) && (expectedSkillHash != null) && (expectedSkillHash.length() == 64) && (expectedSkillKey != null) && !expectedSkillKey.isEmpty();
		}

		private PlayerClass classAt(int index)
		{
			return switch (index)
			{
				case 0 -> main;
				case 1 -> sub1;
				case 2 -> sub2;
				case 3 -> sub3;
				default -> throw new IllegalArgumentException("Indice de clase invalido: " + index);
			};
		}

		private String key()
		{
			return main.getId() + ":" + sub1.getId() + ":" + sub2.getId() + ":" + sub3.getId();
		}
	}

	private static final class PairDefinition
	{
		private final PlayerClass first;
		private final PlayerClass second;

		private PairDefinition(PlayerClass firstClass, PlayerClass secondClass)
		{
			first = firstClass;
			second = secondClass;
		}

		private String key()
		{
			return first.getId() + ":" + second.getId();
		}
	}

	private static final class PairSkillMetrics
	{
		private final int sharedSkillIds;
		private final int masteryCollisions;
		private final int expectedSkillCount;
		private final String expectedSkillKey;

		private PairSkillMetrics(Map<Integer, Skill> firstSkills, Map<Integer, Skill> secondSkills)
		{
			final Set<Integer> sharedIds = new HashSet<>(firstSkills.keySet());
			sharedIds.retainAll(secondSkills.keySet());
			sharedSkillIds = sharedIds.size();

			final Set<String> firstMasteries = masteryNames(firstSkills.values());
			final Set<String> secondMasteries = masteryNames(secondSkills.values());
			firstMasteries.retainAll(secondMasteries);
			masteryCollisions = firstMasteries.size();

			final Map<Integer, Skill> expected = new HashMap<>();
			mergeHighestSkills(expected, firstSkills.values());
			mergeHighestSkills(expected, secondSkills.values());
			final Map<String, Skill> masteryWinners = new HashMap<>();
			for (Skill skill : new ArrayList<>(expected.values()))
			{
				if (!isNonStackingMastery(skill))
				{
					continue;
				}
				final String name = skill.getName().toLowerCase();
				final Skill previous = masteryWinners.get(name);
				if ((previous != null) && ((previous.getLevel() > skill.getLevel()) || ((previous.getLevel() == skill.getLevel()) && (previous.getId() < skill.getId()))))
				{
					expected.remove(skill.getId());
				}
				else
				{
					if (previous != null)
					{
						expected.remove(previous.getId());
					}
					masteryWinners.put(name, skill);
				}
			}
			expectedSkillCount = expected.size();
			final List<String> expectedParts = new ArrayList<>();
			for (Skill skill : expected.values())
			{
				expectedParts.add(skill.getId() + ":" + skill.getLevel());
			}
			Collections.sort(expectedParts);
			expectedSkillKey = String.join(",", expectedParts);
		}

		private static Set<String> masteryNames(Iterable<Skill> skills)
		{
			final Set<String> result = new HashSet<>();
			for (Skill skill : skills)
			{
				if (isNonStackingMastery(skill))
				{
					result.add(skill.getName().toLowerCase());
				}
			}
			return result;
		}

		private static boolean isNonStackingMastery(Skill skill)
		{
			return (skill != null) && skill.isPassive() && skill.getName().endsWith(" Mastery");
		}

		private static void mergeHighestSkills(Map<Integer, Skill> target, Iterable<Skill> skills)
		{
			for (Skill skill : skills)
			{
				final Skill previous = target.get(skill.getId());
				if ((previous == null) || (skill.getLevel() > previous.getLevel()))
				{
					target.put(skill.getId(), skill);
				}
			}
		}
	}

	private void createTable()
	{
		try (Connection con = DatabaseFactory.getConnection(); Statement st = con.createStatement())
		{
			st.executeUpdate(CREATE_TABLE);
			st.executeUpdate(CREATE_STATS_TABLE);
			st.executeUpdate(CREATE_PLAYER_STATS_TABLE);
			st.executeUpdate(CREATE_PLAYER_PROFILE_TABLE);
			st.executeUpdate(CREATE_PAIR_PROFILE_TABLE);
			st.executeUpdate(CREATE_FOUR_CLASS_PROFILE_TABLE);
			st.executeUpdate(CREATE_BENCHMARK_RUN_TABLE);
			st.executeUpdate(CREATE_NYX_CALIBRATION_RUN_TABLE);
			st.executeUpdate(CREATE_MAGIC_PROGRESSION_RUN_TABLE);
			st.executeUpdate(CREATE_MAGIC_COMPARISON_RUN_TABLE);
			st.executeUpdate(CREATE_PHYSICAL_RACE_RUN_TABLE);
		}
		catch (SQLException e)
		{
			LOGGER.log(Level.WARNING, "No se pudo crear la tabla de telemetria.", e);
		}
	}

	private void schedulePlayerProfile(Player player)
	{
		if (player != null)
		{
			// Profession events fire before the class-index switch is fully complete.
			ThreadPool.schedule(() ->
			{
				if (!CONTROLLED_CAPTURE_IDS.contains(player.getObjectId()))
				{
					capturePlayerProfile(player);
				}
			}, 1500);
		}
	}

	private void capturePlayerProfile(Player player)
	{
		if ((player == null) || !player.isOnline() || CONTROLLED_CAPTURE_IDS.contains(player.getObjectId()))
		{
			return;
		}
		final CreatureSnapshot snapshot = new CreatureSnapshot(player);
		ThreadPool.execute(() ->
		{
			try (Connection con = DatabaseFactory.getConnection())
			{
				upsertPlayerProfile(con, snapshot);
			}
			catch (SQLException ex)
			{
				LOGGER.log(Level.WARNING, "No se pudo guardar el perfil de clase del jugador.", ex);
			}
		});
	}

	private void onDamage(OnCreatureDamageDealt event)
	{
		record("DAMAGE", event.getAttacker(), event.getTarget(), event.getSkill(), event.getDamage(), event.isCritical(), event.isDamageOverTime());
	}

	private void onAvoid(OnCreatureAttackAvoid event)
	{
		record("MISS", event.getAttacker(), event.getTarget(), null, 0, false, event.isDamageOverTime());
	}

	private void onSkillUse(OnCreatureSkillUse event)
	{
		record("SKILL", event.getCaster(), event.getTarget(), event.getSkill(), 0, false, false);
	}

	private void onDeath(OnCreatureDeath event)
	{
		record("DEATH", event.getAttacker(), event.getTarget(), null, 0, false, false);
	}

	private void record(String type, Creature attacker, Creature target, Skill skill, double damage, boolean critical, boolean damageOverTime)
	{
		if (!isInteresting(attacker, target))
		{
			return;
		}

		final CombatSnapshot snapshot = new CombatSnapshot(type, attacker, target, skill, damage, critical, damageOverTime);
		ThreadPool.execute(() -> insert(snapshot));
	}

	private boolean isInteresting(Creature attacker, Creature target)
	{
		if ((attacker == null) && (target == null))
		{
			return false;
		}
		if (((attacker != null) && BENCHMARK_CAPTURE_IDS.contains(attacker.getObjectId())) || ((target != null) && BENCHMARK_CAPTURE_IDS.contains(target.getObjectId())))
		{
			return false;
		}
		return isPlayer(attacker) || isPlayer(target) || isLabOpponent(attacker) || isLabOpponent(target);
	}

	private boolean isPlayer(Creature creature)
	{
		return creature instanceof Player;
	}

	private boolean isLabOpponent(Creature creature)
	{
		if (!(creature instanceof Npc))
		{
			return false;
		}
		final int id = ((Npc) creature).getId();
		return (id >= LAB_NPC_ID_MIN) && (id <= LAB_NPC_ID_MAX);
	}

	private void insert(CombatSnapshot e)
	{
		try (Connection con = DatabaseFactory.getConnection(); PreparedStatement ps = con.prepareStatement(INSERT_EVENT))
		{
			int i = 1;
			ps.setLong(i++, e.time);
			ps.setString(i++, e.type);
			i = bindCreature(ps, i, e.attacker);
			i = bindCreature(ps, i, e.target);
			ps.setInt(i++, e.skillId);
			ps.setInt(i++, e.skillLevel);
			ps.setString(i++, e.skillName);
			ps.setDouble(i++, e.damage);
			ps.setBoolean(i++, e.critical);
			ps.setBoolean(i++, e.damageOverTime);
			ps.setBoolean(i++, e.targetDead);
			ps.setInt(i++, e.x);
			ps.setInt(i++, e.y);
			ps.setInt(i, e.z);
			ps.executeUpdate();
			upsertStats(con, e.attacker);
			upsertStats(con, e.target);
			upsertPlayerStats(con, e.attacker);
			upsertPlayerStats(con, e.target);
			upsertPlayerProfile(con, e.attacker);
			upsertPlayerProfile(con, e.target);
		}
		catch (SQLException ex)
		{
			LOGGER.log(Level.WARNING, "No se pudo guardar un evento de telemetria.", ex);
		}
	}

	private void upsertPlayerProfile(Connection con, CreatureSnapshot c) throws SQLException
	{
		if (!"PLAYER".equals(c.kind) || (c.objectId <= 0))
		{
			return;
		}
		try (PreparedStatement ps = con.prepareStatement(UPSERT_PLAYER_PROFILE))
		{
			int i = 1;
			ps.setInt(i++, c.objectId); ps.setString(i++, c.name); ps.setLong(i++, c.observedMs);
			ps.setInt(i++, c.raceId); ps.setString(i++, c.raceName); ps.setInt(i++, c.baseClassId); ps.setInt(i++, c.classIndex); ps.setInt(i++, c.classId);
			ps.setInt(i++, c.sub1ClassId); ps.setInt(i++, c.sub2ClassId); ps.setInt(i++, c.sub3ClassId); ps.setInt(i++, c.level);
			ps.setString(i++, c.equipmentKey); ps.setString(i++, c.effectKey); ps.setInt(i++, c.equippedCount); ps.setInt(i++, c.effectCount); ps.setInt(i++, c.skillCount); ps.setString(i++, c.profileKey);
			ps.setDouble(i++, c.cp); ps.setDouble(i++, c.maxCp); ps.setDouble(i++, c.hp); ps.setDouble(i++, c.maxHp); ps.setDouble(i++, c.mp); ps.setDouble(i++, c.maxMp);
			ps.setDouble(i++, c.pAtk); ps.setDouble(i++, c.mAtk); ps.setDouble(i++, c.pDef); ps.setDouble(i++, c.mDef);
			ps.setInt(i++, c.accuracy); ps.setInt(i++, c.evasion); ps.setInt(i++, c.pCritical); ps.setInt(i++, c.mCritical);
			ps.setDouble(i++, c.criticalMultiplier); ps.setDouble(i++, c.criticalAdd); ps.setDouble(i++, c.pAtkSpeed); ps.setInt(i++, c.mAtkSpeed);
			ps.setDouble(i++, c.runSpeed); ps.setDouble(i++, c.walkSpeed); ps.setInt(i++, c.attackRange);
			ps.setInt(i++, c.statStr); ps.setInt(i++, c.statDex); ps.setInt(i++, c.statCon); ps.setInt(i++, c.statInt); ps.setInt(i++, c.statWit); ps.setInt(i, c.statMen);
			ps.executeUpdate();
		}
	}

	private void upsertStats(Connection con, CreatureSnapshot c) throws SQLException
	{
		if ((c.templateId < LAB_NPC_ID_MIN) || (c.templateId > LAB_NPC_ID_MAX))
		{
			return;
		}
		try (PreparedStatement ps = con.prepareStatement(UPSERT_STATS))
		{
			int i = 1;
			ps.setInt(i++, c.templateId); ps.setInt(i++, c.objectId); ps.setString(i++, c.name); ps.setLong(i++, c.observedMs); ps.setInt(i++, c.level);
			ps.setDouble(i++, c.cp); ps.setDouble(i++, c.maxCp); ps.setDouble(i++, c.hp); ps.setDouble(i++, c.maxHp); ps.setDouble(i++, c.mp); ps.setDouble(i++, c.maxMp);
			ps.setDouble(i++, c.pAtk); ps.setDouble(i++, c.mAtk); ps.setDouble(i++, c.pDef); ps.setDouble(i++, c.mDef);
			ps.setInt(i++, c.accuracy); ps.setInt(i++, c.evasion); ps.setInt(i++, c.pCritical); ps.setInt(i++, c.mCritical);
			ps.setDouble(i++, c.criticalMultiplier); ps.setDouble(i++, c.criticalAdd); ps.setDouble(i++, c.pAtkSpeed); ps.setInt(i++, c.mAtkSpeed);
			ps.setDouble(i++, c.runSpeed); ps.setDouble(i++, c.walkSpeed); ps.setInt(i++, c.attackRange);
			ps.setInt(i++, c.statStr); ps.setInt(i++, c.statDex); ps.setInt(i++, c.statCon); ps.setInt(i++, c.statInt); ps.setInt(i++, c.statWit); ps.setInt(i, c.statMen);
			ps.executeUpdate();
		}
	}

	private void upsertPlayerStats(Connection con, CreatureSnapshot c) throws SQLException
	{
		if (!"PLAYER".equals(c.kind) || (c.objectId <= 0))
		{
			return;
		}
		try (PreparedStatement ps = con.prepareStatement(UPSERT_PLAYER_STATS))
		{
			int i = 1;
			ps.setInt(i++, c.objectId); ps.setInt(i++, c.objectId); ps.setInt(i++, c.classId); ps.setString(i++, c.name); ps.setLong(i++, c.observedMs); ps.setInt(i++, c.level);
			ps.setDouble(i++, c.cp); ps.setDouble(i++, c.maxCp); ps.setDouble(i++, c.hp); ps.setDouble(i++, c.maxHp); ps.setDouble(i++, c.mp); ps.setDouble(i++, c.maxMp);
			ps.setDouble(i++, c.pAtk); ps.setDouble(i++, c.mAtk); ps.setDouble(i++, c.pDef); ps.setDouble(i++, c.mDef);
			ps.setInt(i++, c.accuracy); ps.setInt(i++, c.evasion); ps.setInt(i++, c.pCritical); ps.setInt(i++, c.mCritical);
			ps.setDouble(i++, c.criticalMultiplier); ps.setDouble(i++, c.criticalAdd); ps.setDouble(i++, c.pAtkSpeed); ps.setInt(i++, c.mAtkSpeed);
			ps.setDouble(i++, c.runSpeed); ps.setDouble(i++, c.walkSpeed); ps.setInt(i++, c.attackRange);
			ps.setInt(i++, c.statStr); ps.setInt(i++, c.statDex); ps.setInt(i++, c.statCon); ps.setInt(i++, c.statInt); ps.setInt(i++, c.statWit); ps.setInt(i, c.statMen);
			ps.executeUpdate();
		}
	}

	private int bindCreature(PreparedStatement ps, int index, CreatureSnapshot c) throws SQLException
	{
		ps.setInt(index++, c.objectId);
		ps.setString(index++, c.name);
		ps.setString(index++, c.kind);
		ps.setInt(index++, c.templateId);
		ps.setInt(index++, c.classId);
		ps.setInt(index++, c.level);
		ps.setDouble(index++, c.cp);
		ps.setDouble(index++, c.maxCp);
		ps.setDouble(index++, c.hp);
		ps.setDouble(index++, c.maxHp);
		ps.setDouble(index++, c.mp);
		ps.setDouble(index++, c.maxMp);
		return index;
	}

	private static final class CombatSnapshot
	{
		private final long time = System.currentTimeMillis();
		private final String type;
		private final CreatureSnapshot attacker;
		private final CreatureSnapshot target;
		private final int skillId;
		private final int skillLevel;
		private final String skillName;
		private final double damage;
		private final boolean critical;
		private final boolean damageOverTime;
		private final boolean targetDead;
		private final int x;
		private final int y;
		private final int z;

		private CombatSnapshot(String eventType, Creature source, Creature victim, Skill skill, double amount, boolean crit, boolean dot)
		{
			type = eventType;
			attacker = new CreatureSnapshot(source);
			target = new CreatureSnapshot(victim);
			skillId = skill != null ? skill.getId() : 0;
			skillLevel = skill != null ? skill.getLevel() : 0;
			skillName = skill != null ? skill.getName() : ("DAMAGE".equals(eventType) ? "Ataque basico" : "");
			damage = amount;
			critical = crit;
			damageOverTime = dot;
			targetDead = (victim != null) && victim.isDead();
			x = source != null ? source.getX() : (victim != null ? victim.getX() : 0);
			y = source != null ? source.getY() : (victim != null ? victim.getY() : 0);
			z = source != null ? source.getZ() : (victim != null ? victim.getZ() : 0);
		}
	}

	private static final class CreatureSnapshot
	{
		private final int objectId;
		private final String name;
		private final String kind;
		private final int templateId;
		private final int classId;
		private final int baseClassId;
		private final int classIndex;
		private final int raceId;
		private final String raceName;
		private final int sub1ClassId;
		private final int sub2ClassId;
		private final int sub3ClassId;
		private final String equipmentKey;
		private final String effectKey;
		private final int equippedCount;
		private final int effectCount;
		private final int skillCount;
		private final String profileKey;
		private final int level;
		private final double cp;
		private final double maxCp;
		private final double hp;
		private final double maxHp;
		private final double mp;
		private final double maxMp;
		private final long observedMs;
		private final double pAtk;
		private final double mAtk;
		private final double pDef;
		private final double mDef;
		private final int accuracy;
		private final int evasion;
		private final int pCritical;
		private final int mCritical;
		private final double criticalMultiplier;
		private final double criticalAdd;
		private final double pAtkSpeed;
		private final int mAtkSpeed;
		private final double runSpeed;
		private final double walkSpeed;
		private final int attackRange;
		private final int statStr;
		private final int statDex;
		private final int statCon;
		private final int statInt;
		private final int statWit;
		private final int statMen;

		private CreatureSnapshot(Creature creature)
		{
			if (creature == null)
			{
				objectId = 0;
				name = "";
				kind = "";
				templateId = 0;
				classId = -1;
				baseClassId = -1; classIndex = 0; raceId = -1; raceName = "";
				sub1ClassId = -1; sub2ClassId = -1; sub3ClassId = -1;
				equipmentKey = ""; effectKey = ""; equippedCount = 0; effectCount = 0; skillCount = 0; profileKey = "";
				level = 0;
				cp = 0;
				maxCp = 0;
				hp = 0;
				maxHp = 0;
				mp = 0;
				maxMp = 0;
				observedMs = 0; pAtk = 0; mAtk = 0; pDef = 0; mDef = 0; accuracy = 0; evasion = 0; pCritical = 0; mCritical = 0;
				criticalMultiplier = 2; criticalAdd = 0; pAtkSpeed = 0; mAtkSpeed = 0; runSpeed = 0; walkSpeed = 0; attackRange = 0;
				statStr = 0; statDex = 0; statCon = 0; statInt = 0; statWit = 0; statMen = 0;
				return;
			}

			objectId = creature.getObjectId();
			name = creature.getName() != null ? creature.getName() : "";
			kind = creature instanceof Player ? "PLAYER" : (creature instanceof Npc ? "NPC" : "CREATURE");
			templateId = creature instanceof Npc ? ((Npc) creature).getId() : 0;
			final Player player = creature instanceof Player ? (Player) creature : null;
			classId = player != null ? player.getPlayerClass().getId() : -1;
			baseClassId = player != null ? player.getBaseClass() : -1;
			classIndex = player != null ? player.getClassIndex() : 0;
			raceId = player != null ? player.getRace().ordinal() : -1;
			raceName = player != null ? player.getRace().name() : "";
			sub1ClassId = subClassId(player, 1);
			sub2ClassId = subClassId(player, 2);
			sub3ClassId = subClassId(player, 3);
			equipmentKey = equipmentKey(player);
			effectKey = effectKey(player);
			equippedCount = player != null ? countEquipped(player) : 0;
			effectCount = player != null ? player.getEffectList().getEffects().size() : 0;
			skillCount = player != null ? player.getAllSkills().size() : 0;
			profileKey = player != null ? sha256(baseClassId + ":" + classIndex + ":" + classId + ":" + sub1ClassId + ":" + sub2ClassId + ":" + sub3ClassId + ":" + creature.getLevel() + ":" + equipmentKey + ":" + effectKey) : "";
			level = creature.getLevel();
			cp = creature.getCurrentCp();
			maxCp = creature.getMaxCp();
			hp = creature.getCurrentHp();
			maxHp = creature.getMaxHp();
			mp = creature.getCurrentMp();
			maxMp = creature.getMaxMp();
			observedMs = System.currentTimeMillis();
			pAtk = creature.getPAtk(null);
			mAtk = creature.getMAtk(null, null);
			pDef = creature.getPDef(null);
			mDef = creature.getMDef(null, null);
			accuracy = creature.getAccuracy();
			evasion = creature.getEvasionRate(null);
			pCritical = creature.getCriticalHit(null, null);
			mCritical = creature.getMCriticalHit(null, null);
			criticalMultiplier = 2 * creature.calcStat(Stat.CRITICAL_DAMAGE, 1, null, null) * creature.calcStat(Stat.CRITICAL_DAMAGE_POS, 1, null, null);
			criticalAdd = creature.calcStat(Stat.CRITICAL_DAMAGE_ADD, 0, null, null);
			pAtkSpeed = creature.getPAtkSpd();
			mAtkSpeed = creature.getMAtkSpd();
			runSpeed = creature.getRunSpeed();
			walkSpeed = creature.getWalkSpeed();
			attackRange = creature.getPhysicalAttackRange();
			statStr = creature.getSTR(); statDex = creature.getDEX(); statCon = creature.getCON();
			statInt = creature.getINT(); statWit = creature.getWIT(); statMen = creature.getMEN();
		}

		private static int subClassId(Player player, int slot)
		{
			if (player == null)
			{
				return -1;
			}
			final SubClassHolder sub = player.getSubClasses().get(slot);
			return sub != null ? sub.getId() : -1;
		}

		private static int countEquipped(Player player)
		{
			int count = 0;
			for (Item item : player.getInventory().getItems())
			{
				if (item.isEquipped())
				{
					count++;
				}
			}
			return count;
		}

		private static String equipmentKey(Player player)
		{
			if (player == null)
			{
				return "";
			}
			final List<String> equipment = new ArrayList<>();
			for (Item item : player.getInventory().getItems())
			{
				if (item.isEquipped())
				{
					equipment.add(item.getId() + ":" + item.getEnchantLevel());
				}
			}
			Collections.sort(equipment);
			return String.join(",", equipment);
		}

		private static String effectKey(Player player)
		{
			if (player == null)
			{
				return "";
			}
			final List<String> effects = new ArrayList<>();
			for (BuffInfo info : player.getEffectList().getEffects())
			{
				if ((info != null) && (info.getSkill() != null))
				{
					effects.add(info.getSkill().getId() + ":" + info.getSkill().getLevel());
				}
			}
			Collections.sort(effects);
			return String.join(",", effects);
		}

		private static String sha256(String value)
		{
			try
			{
				final byte[] digest = MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
				final StringBuilder result = new StringBuilder(64);
				for (byte part : digest)
				{
					result.append(String.format("%02x", part & 0xff));
				}
				return result.toString();
			}
			catch (NoSuchAlgorithmException e)
			{
				throw new IllegalStateException(e);
			}
		}
	}

	public static void main(String[] args)
	{
		new LabTelemetry();
	}
}
