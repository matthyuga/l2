/*M!999999\- enable the sandbox mode */
-- MariaDB dump 10.20-11.8.9-MariaDB, for Win64 (AMD64)
--
-- Host: 127.0.0.1    Database: l2jmobiusinterlude
-- ------------------------------------------------------
-- Server version	11.8.9-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `lab_magic_progression_runs`
--

DROP TABLE IF EXISTS `lab_magic_progression_runs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lab_magic_progression_runs` (
  `stage_index` smallint(6) NOT NULL,
  `run_number` smallint(6) NOT NULL,
  `executed_ms` bigint(20) unsigned NOT NULL,
  `engine_mode` varchar(32) NOT NULL DEFAULT 'CORE_ACCELERATED',
  `stage_label` varchar(80) NOT NULL,
  `main_class_id` int(11) NOT NULL,
  `sub1_class_id` int(11) NOT NULL DEFAULT -1,
  `sub2_class_id` int(11) NOT NULL DEFAULT -1,
  `sub3_class_id` int(11) NOT NULL DEFAULT -1,
  `class_count` smallint(6) NOT NULL,
  `char_id` int(11) NOT NULL,
  `char_name` varchar(45) NOT NULL,
  `active_class_id` int(11) NOT NULL,
  `active_class_index` smallint(6) NOT NULL,
  `level` smallint(6) NOT NULL,
  `skill_count` smallint(6) NOT NULL,
  `passive_skill_count` smallint(6) NOT NULL,
  `active_skill_count` smallint(6) NOT NULL,
  `equipment_kit` varchar(32) NOT NULL,
  `weapon_id` int(11) NOT NULL,
  `weapon_name` varchar(80) NOT NULL,
  `p_atk` double NOT NULL,
  `m_atk` double NOT NULL,
  `p_def` double NOT NULL,
  `m_def` double NOT NULL,
  `p_atk_speed` double NOT NULL,
  `m_atk_speed` double NOT NULL,
  `max_hp` double NOT NULL,
  `max_cp` double NOT NULL,
  `max_mp` double NOT NULL,
  `duration_seconds` smallint(6) NOT NULL,
  `rotation` varchar(512) NOT NULL DEFAULT '',
  `actions` int(11) NOT NULL DEFAULT 0,
  `hits` int(11) NOT NULL DEFAULT 0,
  `casts` int(11) NOT NULL DEFAULT 0,
  `critical_count` int(11) NOT NULL DEFAULT 0,
  `miss_count` int(11) NOT NULL DEFAULT 0,
  `bss_used` int(11) NOT NULL DEFAULT 0,
  `damage_dealt` double NOT NULL DEFAULT 0,
  `dps` double NOT NULL DEFAULT 0,
  `mp_used` double NOT NULL DEFAULT 0,
  `notes` varchar(512) NOT NULL DEFAULT '',
  PRIMARY KEY (`stage_index`,`run_number`),
  KEY `idx_lab_magic_progression_time` (`executed_ms`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lab_magic_progression_runs`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `lab_magic_progression_runs` WRITE;
/*!40000 ALTER TABLE `lab_magic_progression_runs` DISABLE KEYS */;
INSERT INTO `lab_magic_progression_runs` VALUES
(0,1,1791407472410,'CORE_ACCELERATED','Storm Screamer',110,-1,-1,-1,1,268436111,'Myrentha',110,0,80,74,24,50,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1239:28 Hurricane+Blessed_Spiritshot_S',15,15,15,0,0,15,2738.192864433602,45.63654774056003,1035,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(0,2,1791407472427,'CORE_ACCELERATED','Storm Screamer',110,-1,-1,-1,1,268436111,'Myrentha',110,0,80,74,24,50,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1239:28 Hurricane+Blessed_Spiritshot_S',15,15,15,0,0,15,2614.2125924346683,43.57020987391114,1035,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(0,3,1791407472458,'CORE_ACCELERATED','Storm Screamer',110,-1,-1,-1,1,268436111,'Myrentha',110,0,80,74,24,50,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1239:28 Hurricane+Blessed_Spiritshot_S',15,15,15,0,0,15,2580.5608043206717,43.00934673867786,1035,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(1,1,1791407477604,'CORE_ACCELERATED','+ Mystic Muse',110,103,-1,-1,2,268436111,'Myrentha',110,0,80,103,24,79,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,0,0,37,5167.081240367062,86.11802067278435,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(1,2,1791407477630,'CORE_ACCELERATED','+ Mystic Muse',110,103,-1,-1,2,268436111,'Myrentha',110,0,80,103,24,79,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,0,0,37,5254.236827553977,87.57061379256628,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(1,3,1791407477657,'CORE_ACCELERATED','+ Mystic Muse',110,103,-1,-1,2,268436111,'Myrentha',110,0,80,103,24,79,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,1,0,37,5306.8068642698945,88.4467810711649,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(2,1,1791407481674,'CORE_ACCELERATED','+ Archmage',110,103,94,-1,3,268436111,'Myrentha',110,0,80,118,24,94,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,0,0,37,4960.617937541076,82.67696562568459,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(2,2,1791407481690,'CORE_ACCELERATED','+ Archmage',110,103,94,-1,3,268436111,'Myrentha',110,0,80,118,24,94,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,0,0,37,4819.150602628825,80.31917671048042,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(2,3,1791407481706,'CORE_ACCELERATED','+ Archmage',110,103,94,-1,3,268436111,'Myrentha',110,0,80,118,24,94,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1308.680599252712,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,3,0,37,5554.439405642237,92.57399009403728,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(3,1,1791407486823,'CORE_ACCELERATED','+ Soultaker',110,103,94,95,4,268436111,'Myrentha',110,0,80,139,25,114,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1344.9620172302937,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,0,0,37,4887.599862422094,81.4599977070349,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(3,2,1791407486839,'CORE_ACCELERATED','+ Soultaker',110,103,94,95,4,268436111,'Myrentha',110,0,80,139,25,114,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1344.9620172302937,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,0,0,37,4789.427124869857,79.82378541449762,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.'),
(3,3,1791407486854,'CORE_ACCELERATED','+ Soultaker',110,103,94,95,4,268436111,'Myrentha',110,0,80,139,25,114,'S_ROBE',6579,'Arcana Mace',443.29925000000003,1344.9620172302937,677.8700000000001,907.1333999999999,390,366,2958,1479,4015,60,'1231:28 Aura Flare+Blessed_Spiritshot_S',37,37,37,1,0,37,5343.40185820034,89.05669763667234,2553,'Storm Screamer activa; Arcana Mace +0, set robe S y joyeria comun S; sin buffs externos.');
/*!40000 ALTER TABLE `lab_magic_progression_runs` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-10-07 18:12:38
