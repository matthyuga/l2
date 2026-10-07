'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const mysql = require('mysql2/promise');
const { createDataStore } = require('../lib/data');

const PANEL_ROOT = path.resolve(__dirname, '..');
const PROJECT_ROOT = path.resolve(PANEL_ROOT, '..');
const SERVER_DATA = path.join(PROJECT_ROOT, 'server', 'game', 'data');
const SOURCE_DATA = path.join(PROJECT_ROOT, 'source', 'L2J_Mobius_CT_0_Interlude', 'dist', 'game', 'data');
const config = JSON.parse(fs.readFileSync(path.join(PANEL_ROOT, 'config.json'), 'utf8'));
config.paths.serverData = SERVER_DATA;
config.paths.sourceData = SOURCE_DATA;
config.paths.backupRoot = path.join(PROJECT_ROOT, 'backups', 'lab-panel');
const data = createDataStore(config);

const EXPECTED_PAIRS = 465;
const EXPECTED_CANDIDATES = 125860;
const EXPECTED_SELECTED = 155;
const MAGE_ROOTS = new Set([10, 25, 38, 49]);
const SUMMONERS = new Set([96, 104, 111]);

function walk(dir, output) {
  const files = output || [];
  fs.readdirSync(dir, { withFileTypes: true }).forEach(function (entry) {
    const target = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(target, files);
    else if (/\.xml$/i.test(entry.name)) files.push(target);
  });
  return files;
}

function attributes(source) {
  const result = {};
  String(source).replace(/([\w:-]+)="([^"]*)"/g, function (whole, key, value) {
    result[key] = value;
    return whole;
  });
  return result;
}

function loadSkillMetadata() {
  const result = new Map();
  const skillRoot = path.join(SERVER_DATA, 'stats', 'skills');
  walk(skillRoot).forEach(function (file) {
    const xml = fs.readFileSync(file, 'utf8');
    const regex = /<skill\s+([^>]*\bid="\d+"[^>]*)>([\s\S]*?)<\/skill>/g;
    let match;
    while ((match = regex.exec(xml)) !== null) {
      const attr = attributes(match[1]);
      const id = Number(attr.id);
      if (!Number.isInteger(id) || result.has(id)) continue;
      const operateType = (match[2].match(/<operateType>([^<]+)<\/operateType>/i) || [null, ''])[1].trim().toUpperCase();
      result.set(id, {
        name: attr.name || ('Skill ' + id),
        passive: operateType === 'P'
      });
    }
  });
  return result;
}

function parseSkillKey(value) {
  const result = new Map();
  String(value || '').split(',').forEach(function (part) {
    if (!part) return;
    const pieces = part.split(':');
    const id = Number(pieces[0]);
    const level = Number(pieces[1]);
    if (!Number.isInteger(id) || !Number.isInteger(level)) throw new Error('Skill key inválida: ' + part);
    const previous = result.get(id);
    if (previous === undefined || level > previous) result.set(id, level);
  });
  return result;
}

function pairKey(first, second) {
  return first < second ? first + ':' + second : second + ':' + first;
}

function buildKey(main, subA, subB, subC) {
  return main + ':' + subA + ':' + subB + ':' + subC;
}

function compareIds(left, right) {
  return left.mainId - right.mainId || left.subA - right.subA || left.subB - right.subB || left.subC - right.subC;
}

function composeCandidate(mainId, subA, subB, subC, pairMap, classMap, skillMetadata, includeSkillKey) {
  const firstPair = pairMap.get(pairKey(mainId, subA));
  const secondPair = pairMap.get(pairKey(subB, subC));
  if (!firstPair || !secondPair) throw new Error('Falta una pareja para ' + buildKey(mainId, subA, subB, subC));

  const skills = new Map(firstPair.skills);
  secondPair.skills.forEach(function (level, id) {
    const previous = skills.get(id);
    if (previous === undefined || level > previous) skills.set(id, level);
  });

  const masteryWinners = new Map();
  Array.from(skills.entries()).forEach(function (entry) {
    const id = entry[0];
    const level = entry[1];
    const meta = skillMetadata.get(id);
    if (!meta) throw new Error('No existe metadata XML para skill ' + id + '.');
    if (!meta.passive || !meta.name.endsWith(' Mastery')) return;
    const name = meta.name.toLowerCase();
    const previous = masteryWinners.get(name);
    if (previous && ((previous.level > level) || ((previous.level === level) && (previous.id < id)))) {
      skills.delete(id);
    } else {
      if (previous) skills.delete(previous.id);
      masteryWinners.set(name, { id: id, level: level });
    }
  });

  let passiveCount = 0;
  skills.forEach(function (_, id) {
    if (skillMetadata.get(id).passive) passiveCount += 1;
  });
  const parts = Array.from(skills.entries()).map(function (entry) { return entry[0] + ':' + entry[1]; }).sort();
  const exactSkillKey = parts.join(',');
  const ids = [mainId, subA, subB, subC];
  const classes = ids.map(function (id) { return classMap.get(id); });
  const mageCount = classes.filter(function (item) { return item.isMage; }).length;
  const summonerCount = ids.filter(function (id) { return SUMMONERS.has(id); }).length;
  const main = classMap.get(mainId);
  const sameRaceCount = classes.filter(function (item) { return item.race === main.race; }).length;
  const sameArchetypeCount = classes.filter(function (item) { return item.isMage === main.isMage; }).length;
  const raceCount = new Set(classes.map(function (item) { return item.race; })).size;
  const pairs = [
    pairMap.get(pairKey(mainId, subA)), pairMap.get(pairKey(mainId, subB)), pairMap.get(pairKey(mainId, subC)),
    pairMap.get(pairKey(subA, subB)), pairMap.get(pairKey(subA, subC)), pairMap.get(pairKey(subB, subC))
  ];
  const sharedScore = pairs.reduce(function (sum, item) { return sum + item.shared; }, 0);
  const masteryScore = pairs.reduce(function (sum, item) { return sum + item.masteries; }, 0);

  return {
    key: buildKey(mainId, subA, subB, subC),
    mainId: mainId,
    subA: subA,
    subB: subB,
    subC: subC,
    skillCount: skills.size,
    passiveCount: passiveCount,
    activeCount: skills.size - passiveCount,
    sharedScore: sharedScore,
    masteryScore: masteryScore,
    mageCount: mageCount,
    summonerCount: summonerCount,
    raceCount: raceCount,
    sameRaceCount: sameRaceCount,
    sameArchetypeCount: sameArchetypeCount,
    composition: mageCount === 0 ? 'Física' : mageCount === 4 ? 'Mágica' : 'Híbrida',
    skillHash: crypto.createHash('sha256').update(exactSkillKey, 'utf8').digest('hex'),
    skillKey: includeSkillKey ? exactSkillKey : null,
    selected: false,
    bucket: '',
    selectionOrder: 0
  };
}

function pick(candidates, used, comparator) {
  const ordered = candidates.slice().sort(comparator);
  for (let index = 0; index < ordered.length; index += 1) {
    if (!used.has(ordered[index].key)) return ordered[index];
  }
  throw new Error('No quedan candidatos únicos para seleccionar.');
}

function selectCandidates(byMain, thirdIds) {
  const selected = [];
  const used = new Set();
  function add(candidate, bucket) {
    candidate.selected = true;
    candidate.bucket = bucket;
    candidate.selectionOrder = selected.length + 1;
    selected.push(candidate);
    used.add(candidate.key);
  }

  thirdIds.forEach(function (mainId) {
    const candidates = byMain.get(mainId);
    add(pick(candidates, used, function (a, b) {
      return b.skillCount - a.skillCount || a.sharedScore - b.sharedScore || a.masteryScore - b.masteryScore || compareIds(a, b);
    }), 'amplitud');
    add(pick(candidates, used, function (a, b) {
      return b.sameArchetypeCount - a.sameArchetypeCount || b.sameRaceCount - a.sameRaceCount || b.skillCount - a.skillCount || a.masteryScore - b.masteryScore || compareIds(a, b);
    }), 'afinidad');
    add(pick(candidates, used, function (a, b) {
      return b.masteryScore - a.masteryScore || b.sharedScore - a.sharedScore || b.skillCount - a.skillCount || compareIds(a, b);
    }), 'estrés');
    add(pick(candidates, used, function (a, b) {
      return Math.abs(a.mageCount - 2) - Math.abs(b.mageCount - 2) || b.raceCount - a.raceCount || b.skillCount - a.skillCount || a.sharedScore - b.sharedScore || compareIds(a, b);
    }), 'híbrida');
  });

  const appearances = new Map(thirdIds.map(function (id) { return [id, 0]; }));
  selected.forEach(function (candidate) {
    [candidate.mainId, candidate.subA, candidate.subB, candidate.subC].forEach(function (id) {
      appearances.set(id, appearances.get(id) + 1);
    });
  });
  thirdIds.forEach(function (mainId) {
    const candidate = pick(byMain.get(mainId), used, function (a, b) {
      const aCoverage = [a.subA, a.subB, a.subC].reduce(function (score, id) { return score + (10000 / (appearances.get(id) + 1)); }, 0);
      const bCoverage = [b.subA, b.subB, b.subC].reduce(function (score, id) { return score + (10000 / (appearances.get(id) + 1)); }, 0);
      return bCoverage - aCoverage || a.skillHash.localeCompare(b.skillHash) || compareIds(a, b);
    });
    add(candidate, 'cobertura');
    [candidate.mainId, candidate.subA, candidate.subB, candidate.subC].forEach(function (id) {
      appearances.set(id, appearances.get(id) + 1);
    });
  });
  return selected;
}

async function main() {
  const connection = await mysql.createConnection(Object.assign({}, config.database, { charset: 'utf8mb4', decimalNumbers: true }));
  try {
    const pairRows = (await connection.query(
      'SELECT pair_a_id,pair_b_id,skill_key,shared_skill_id_count,mastery_collision_count ' +
      'FROM lab_class_pair_profiles WHERE active_class_index=0 AND level=80 AND equipped_count=0 AND effect_count=0 ORDER BY pair_a_id,pair_b_id'
    ))[0];
    if (pairRows.length !== EXPECTED_PAIRS) throw new Error('Se esperaban 465 parejas limpias y se encontraron ' + pairRows.length + '.');

    const classes = data.classes().filter(function (item) { return item.stage === 3; }).sort(function (a, b) { return a.id - b.id; });
    if (classes.length !== 31) throw new Error('Se esperaban 31 terceras profesiones y se encontraron ' + classes.length + '.');
    const classMap = new Map(classes.map(function (item) {
      return [item.id, Object.assign({}, item, { isMage: MAGE_ROOTS.has(item.rootId) })];
    }));
    const thirdIds = classes.map(function (item) { return item.id; });
    const skillMetadata = loadSkillMetadata();
    const pairMap = new Map();
    pairRows.forEach(function (row) {
      pairMap.set(pairKey(Number(row.pair_a_id), Number(row.pair_b_id)), {
        skills: parseSkillKey(row.skill_key),
        shared: Number(row.shared_skill_id_count),
        masteries: Number(row.mastery_collision_count)
      });
    });

    const generatedMs = Date.now();
    const candidates = [];
    const byMain = new Map();
    thirdIds.forEach(function (mainId) {
      const others = thirdIds.filter(function (id) { return id !== mainId; });
      const mainCandidates = [];
      for (let first = 0; first < others.length - 2; first += 1) {
        for (let second = first + 1; second < others.length - 1; second += 1) {
          for (let third = second + 1; third < others.length; third += 1) {
            const candidate = composeCandidate(mainId, others[first], others[second], others[third], pairMap, classMap, skillMetadata, false);
            candidates.push(candidate);
            mainCandidates.push(candidate);
          }
        }
      }
      byMain.set(mainId, mainCandidates);
      process.stdout.write('Principal ' + mainId + ': ' + mainCandidates.length + ' candidatos\n');
    });
    if (candidates.length !== EXPECTED_CANDIDATES) throw new Error('Se esperaban 125860 candidatos y se calcularon ' + candidates.length + '.');

    const selected = selectCandidates(byMain, thirdIds);
    if (selected.length !== EXPECTED_SELECTED) throw new Error('Se esperaban 155 seleccionados y se obtuvieron ' + selected.length + '.');
    selected.forEach(function (candidate) {
      const exact = composeCandidate(candidate.mainId, candidate.subA, candidate.subB, candidate.subC, pairMap, classMap, skillMetadata, true);
      if (exact.skillHash !== candidate.skillHash || exact.skillCount !== candidate.skillCount) throw new Error('La recomputación no coincide para ' + candidate.key + '.');
      candidate.skillKey = exact.skillKey;
    });

    await connection.query('DROP TABLE IF EXISTS lab_four_class_candidates_stage');
    await connection.query(
      "CREATE TABLE lab_four_class_candidates_stage (" +
      "main_class_id INT NOT NULL,sub1_class_id INT NOT NULL,sub2_class_id INT NOT NULL,sub3_class_id INT NOT NULL," +
      "generated_ms BIGINT UNSIGNED NOT NULL,skill_count SMALLINT NOT NULL,passive_skill_count SMALLINT NOT NULL,active_skill_count SMALLINT NOT NULL," +
      "pair_shared_score SMALLINT NOT NULL,mastery_collision_score SMALLINT NOT NULL,mage_class_count TINYINT NOT NULL," +
      "summoner_class_count TINYINT NOT NULL,race_count TINYINT NOT NULL,same_race_class_count TINYINT NOT NULL,same_archetype_count TINYINT NOT NULL," +
      "composition VARCHAR(12) NOT NULL,skill_hash CHAR(64) NOT NULL,skill_key MEDIUMTEXT NULL," +
      "selected TINYINT(1) NOT NULL DEFAULT 0,selection_bucket VARCHAR(16) NOT NULL DEFAULT '',selection_order SMALLINT NOT NULL DEFAULT 0," +
      "PRIMARY KEY (main_class_id,sub1_class_id,sub2_class_id,sub3_class_id)," +
      "KEY idx_lab_four_selected (selected,selection_bucket,selection_order),KEY idx_lab_four_main (main_class_id)," +
      "KEY idx_lab_four_skills (skill_count),KEY idx_lab_four_overlap (mastery_collision_score,pair_shared_score),KEY idx_lab_four_hash (skill_hash)" +
      ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );

    const columns = [
      'main_class_id','sub1_class_id','sub2_class_id','sub3_class_id','generated_ms','skill_count','passive_skill_count','active_skill_count',
      'pair_shared_score','mastery_collision_score','mage_class_count','summoner_class_count','race_count','same_race_class_count',
      'same_archetype_count','composition','skill_hash','skill_key','selected','selection_bucket','selection_order'
    ];
    const batchSize = 750;
    for (let offset = 0; offset < candidates.length; offset += batchSize) {
      const batch = candidates.slice(offset, offset + batchSize).map(function (candidate) {
        return [
          candidate.mainId,candidate.subA,candidate.subB,candidate.subC,generatedMs,candidate.skillCount,candidate.passiveCount,candidate.activeCount,
          candidate.sharedScore,candidate.masteryScore,candidate.mageCount,candidate.summonerCount,candidate.raceCount,candidate.sameRaceCount,
          candidate.sameArchetypeCount,candidate.composition,candidate.skillHash,candidate.skillKey,candidate.selected ? 1 : 0,candidate.bucket,candidate.selectionOrder
        ];
      });
      await connection.query('INSERT INTO lab_four_class_candidates_stage (' + columns.join(',') + ') VALUES ?', [batch]);
      if ((offset + batch.length) % 15000 < batchSize) process.stdout.write('Insertados ' + (offset + batch.length) + '/' + candidates.length + '\n');
    }

    const tables = (await connection.query("SHOW TABLES LIKE 'lab_four_class_candidates'"))[0];
    if (tables.length) {
      await connection.query('DROP TABLE IF EXISTS lab_four_class_candidates_old');
      await connection.query('RENAME TABLE lab_four_class_candidates TO lab_four_class_candidates_old, lab_four_class_candidates_stage TO lab_four_class_candidates');
      await connection.query('DROP TABLE lab_four_class_candidates_old');
    } else {
      await connection.query('RENAME TABLE lab_four_class_candidates_stage TO lab_four_class_candidates');
    }

    const audit = (await connection.query(
      'SELECT COUNT(*) total,SUM(selected) selected,COUNT(DISTINCT main_class_id) mains,COUNT(DISTINCT skill_hash) distinct_skill_sets,' +
      'MIN(skill_count) min_skills,MAX(skill_count) max_skills,ROUND(AVG(skill_count),2) avg_skills FROM lab_four_class_candidates'
    ))[0][0];
    process.stdout.write('FASE 4A COMPLETA ' + JSON.stringify(audit) + '\n');
  } finally {
    await connection.end();
  }
}

main().catch(function (error) {
  console.error(error && error.stack ? error.stack : error);
  process.exitCode = 1;
});
