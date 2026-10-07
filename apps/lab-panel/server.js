'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const net = require('net');
const childProcess = require('child_process');
const { URL } = require('url');
const { createDatabase } = require('./lib/database');
const { createDataStore, httpError } = require('./lib/data');

const ROOT = __dirname;
const PUBLIC = path.join(ROOT, 'public');
const STATE_FILE = path.join(ROOT, 'state.json');
const config = JSON.parse(fs.readFileSync(path.join(ROOT, 'config.json'), 'utf8'));
const officeMode = process.env.L2_LAB_OFFICE === '1';
const portableRoot = process.env.L2_LOCAL_ROOT ? path.resolve(process.env.L2_LOCAL_ROOT) : path.dirname(ROOT);
config.paths.serverData = path.join(portableRoot, 'server', 'game', 'data');
config.paths.sourceData = path.join(portableRoot, 'source', 'L2J_Mobius_CT_0_Interlude', 'dist', 'game', 'data');
config.paths.backupRoot = path.join(portableRoot, 'backups', 'lab-panel');
config.paths.restartScript = path.join(portableRoot, 'Reiniciar-Laboratorio-Sin-Cliente.ps1');
if (process.env.L2_LAB_PORT) config.port = Number(process.env.L2_LAB_PORT);
if (process.env.L2_DB_PORT) config.database.port = Number(process.env.L2_DB_PORT);
const database = createDatabase(config.database);
const data = createDataStore(config);

const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon'
};

function readState() {
  try { return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')); }
  catch (_) { return { requiresRestart: false, lastChange: null, lastBackup: null }; }
}

function writeState(patch) {
  const state = Object.assign(readState(), patch);
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
  return state;
}

function json(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload),
    'Cache-Control': 'no-store'
  });
  res.end(payload);
}

function body(req) {
  return new Promise(function (resolve, reject) {
    let raw = '';
    req.on('data', function (chunk) {
      raw += chunk;
      if (raw.length > 2 * 1024 * 1024) reject(httpError(413, 'La solicitud es demasiado grande.'));
    });
    req.on('end', function () {
      try { resolve(raw ? JSON.parse(raw) : {}); }
      catch (_) { reject(httpError(400, 'JSON inválido.')); }
    });
    req.on('error', reject);
  });
}

function portOpen(port) {
  return new Promise(function (resolve) {
    const socket = net.createConnection({ host: '127.0.0.1', port: port });
    let done = false;
    function finish(value) {
      if (done) return;
      done = true;
      socket.destroy();
      resolve(value);
    }
    socket.setTimeout(450);
    socket.once('connect', function () { finish(true); });
    socket.once('timeout', function () { finish(false); });
    socket.once('error', function () { finish(false); });
  });
}

function classInfo(id) {
  const info = data.classById(id);
  return info || { id: Number(id), name: 'Clase ' + id, race: 'Desconocida', path: 'Clase ' + id };
}

async function characters() {
  const rows = await database.query(
    'SELECT c.charId,c.char_name,c.account_name,c.level,c.classid,c.base_class,c.race,c.online,c.title,c.accesslevel,c.sp,' +
    '(SELECT COUNT(*) FROM character_subclasses s WHERE s.charId=c.charId) AS subclass_count,' +
    '(SELECT COUNT(*) FROM character_skills sk WHERE sk.charId=c.charId) AS skill_count,' +
    '(SELECT COALESCE(SUM(i.count),0) FROM items i WHERE i.owner_id=c.charId AND i.item_id=57) AS adena ' +
    'FROM characters c ORDER BY c.online DESC,c.char_name');
  return rows.map(function (row) {
    row.classInfo = classInfo(row.classid);
    row.baseClassInfo = classInfo(row.base_class);
    row.online = Boolean(row.online);
    return row;
  });
}

async function characterDetail(charId) {
  const baseRows = await database.query(
    'SELECT charId,char_name,account_name,level,classid,base_class,race,online,title,accesslevel,sp,curHp,maxHp,curCp,maxCp,curMp,maxMp,x,y,z FROM characters WHERE charId=?', [charId]);
  if (!baseRows.length) throw httpError(404, 'Personaje no encontrado.');
  const results = await Promise.all([
    database.query('SELECT class_id,level,class_index,exp,sp FROM character_subclasses WHERE charId=? ORDER BY class_index', [charId]),
    database.query('SELECT class_index,COUNT(*) AS total FROM character_skills WHERE charId=? GROUP BY class_index ORDER BY class_index', [charId]),
    database.query('SELECT item_id,count,enchant_level,loc,loc_data FROM items WHERE owner_id=? ORDER BY loc,loc_data,item_id LIMIT 300', [charId])
  ]);
  const character = baseRows[0];
  character.online = Boolean(character.online);
  character.classInfo = classInfo(character.classid);
  character.baseClassInfo = classInfo(character.base_class);
  character.configuredStats = data.playerBaseStats(character.classid, character.level);
  character.subclasses = results[0].map(function (sub) {
    sub.classInfo = classInfo(sub.class_id);
    return sub;
  });
  character.skillCounts = results[1];
  character.items = results[2];
  character.adena = results[2].filter(function (item) { return item.item_id === 57; }).reduce(function (sum, item) { return sum + Number(item.count); }, 0);
  try {
    const statsRows = await database.query('SELECT * FROM lab_player_stats WHERE char_id=?', [charId]);
    character.liveStats = statsRows.length ? statsRows[0] : null;
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') character.liveStats = null;
    else throw error;
  }
  return character;
}

function expForLevel(level) {
  const file = path.join(config.paths.serverData, 'stats', 'players', 'experience.xml');
  const xml = fs.readFileSync(file, 'utf8');
  const match = xml.match(new RegExp('<experience\\s+level="' + level + '"\\s+tolevel="(\\d+)"'));
  if (!match) throw httpError(400, 'No se encontró la experiencia de ese nivel.');
  return match[1];
}

async function updateCharacter(charId, payload) {
  return database.transaction(async function (connection) {
    const selected = await connection.execute('SELECT online FROM characters WHERE charId=? FOR UPDATE', [charId]);
    if (!selected[0].length) throw httpError(404, 'Personaje no encontrado.');
    if (selected[0][0].online) throw httpError(409, 'Cierra el personaje en el juego antes de editarlo.');
    const fields = [];
    const params = [];
    if (payload.title !== undefined) {
      const title = String(payload.title).trim().slice(0, 21);
      fields.push('title=?'); params.push(title);
    }
    if (payload.accesslevel !== undefined) {
      const access = Number(payload.accesslevel);
      if (!Number.isInteger(access) || access < 0 || access > 100) throw httpError(400, 'Access level debe estar entre 0 y 100.');
      fields.push('accesslevel=?'); params.push(access);
    }
    if (payload.sp !== undefined) {
      const sp = Number(payload.sp);
      if (!Number.isSafeInteger(sp) || sp < 0) throw httpError(400, 'SP inválido.');
      fields.push('sp=?'); params.push(sp);
    }
    if (payload.level !== undefined) {
      const level = Number(payload.level);
      if (!Number.isInteger(level) || level < 1 || level > 80) throw httpError(400, 'El nivel debe estar entre 1 y 80.');
      fields.push('level=?'); params.push(level);
      fields.push('exp=?'); params.push(expForLevel(level));
    }
    if (fields.length) {
      params.push(charId);
      await connection.execute('UPDATE characters SET ' + fields.join(',') + ' WHERE charId=?', params);
    }
    if (payload.adena !== undefined) {
      const adena = Number(payload.adena);
      if (!Number.isSafeInteger(adena) || adena < 0) throw httpError(400, 'Cantidad de Adena inválida.');
      const update = await connection.execute('UPDATE items SET count=? WHERE owner_id=? AND item_id=57', [adena, charId]);
      if (!update[0].affectedRows) {
        await connection.execute(
          "INSERT INTO items (owner_id,object_id,item_id,count,enchant_level,loc,loc_data,time_of_use,custom_type1,custom_type2,mana_left,time) " +
          "SELECT ?,COALESCE(MAX(object_id),0)+1,57,?,0,'INVENTORY',0,-1,0,0,-1,0 FROM items", [charId, adena]);
      }
    }
    return { saved: true };
  });
}

async function updateCharacterBaseStats(charId, payload) {
  const rows = await database.query('SELECT online,classid FROM characters WHERE charId=?', [charId]);
  if (!rows.length) throw httpError(404, 'Personaje no encontrado.');
  if (rows[0].online) throw httpError(409, 'Cierra el personaje en el juego antes de editar sus atributos.');
  const fieldMap = {
    str: 'baseSTR', dex: 'baseDEX', con: 'baseCON',
    int: 'baseINT', wit: 'baseWIT', men: 'baseMEN'
  };
  const staticStats = {};
  Object.keys(fieldMap).forEach(function (field) {
    if (payload[field] !== undefined) staticStats[fieldMap[field]] = payload[field];
  });
  if (!Object.keys(staticStats).length) throw httpError(400, 'No se recibieron atributos para guardar.');
  const result = data.updateTemplate(rows[0].classid, { staticStats: staticStats });
  result.classId = Number(rows[0].classid);
  return result;
}

async function opponentDetail(id) {
  const opponent = data.opponent(id);
  opponent.configuredStats = {
    pAtk: opponent.attack.physical, mAtk: opponent.attack.magical,
    pDef: opponent.defence.physical, mDef: opponent.defence.magical,
    accuracy: opponent.attack.accuracy, evasion: opponent.defence.evasion,
    pCritical: opponent.attack.critical, pAtkSpeed: opponent.attack.attackSpeed,
    mAtkSpeed: opponent.attack.magicSpeed === undefined ? 333 : opponent.attack.magicSpeed,
    runSpeed: opponent.movement.run, walkSpeed: opponent.movement.walk,
    attackRange: opponent.attack.range,
    maxHp: opponent.vitals.hp, maxMp: opponent.vitals.mp, maxCp: opponent.vitals.cp,
    str: opponent.stats.str, dex: opponent.stats.dex, con: opponent.stats.con,
    int: opponent.stats.int, wit: opponent.stats.wit, men: opponent.stats.men
  };
  try {
    const rows = await database.query('SELECT * FROM lab_creature_stats WHERE template_id=?', [id]);
    opponent.liveStats = rows.length ? rows[0] : null;
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') opponent.liveStats = null;
    else throw error;
  }
  return opponent;
}

function normalizeEvent(row) {
  ['critical', 'damage_over_time', 'target_dead'].forEach(function (key) { row[key] = Boolean(row[key]); });
  return row;
}

function eventPlayer(row) {
  if (row.attacker_kind === 'PLAYER') return { id: row.attacker_object_id, name: row.attacker_name, side: 'attacker' };
  if (row.target_kind === 'PLAYER') return { id: row.target_object_id, name: row.target_name, side: 'target' };
  return null;
}

function opponentFor(row, player) {
  if (!player) return null;
  if (row.attacker_object_id === player.id) return { id: row.target_object_id, name: row.target_name, templateId: row.target_template_id, kind: row.target_kind };
  return { id: row.attacker_object_id, name: row.attacker_name, templateId: row.attacker_template_id, kind: row.attacker_kind };
}

function participantKey(player, opponent) {
  const opponentKey = opponent.templateId || opponent.id || opponent.name;
  return player.id + ':' + opponentKey;
}

function groupFights(rows) {
  const groups = [];
  const active = {};
  const skillEvents = [];
  rows.map(normalizeEvent).forEach(function (event) {
    if (event.event_type === 'SKILL') { skillEvents.push(event); return; }
    const player = eventPlayer(event);
    const opponent = opponentFor(event, player);
    if (!player || !opponent || !opponent.name || opponent.id === player.id) return;
    const key = participantKey(player, opponent);
    let fight = active[key];
    if (!fight || event.occurred_ms - fight.end > 15000) {
      fight = { id: String(event.event_id), key: key, player: player, opponent: opponent, start: event.occurred_ms, end: event.occurred_ms, events: [] };
      active[key] = fight;
      groups.push(fight);
    }
    fight.events.push(event);
    fight.end = event.occurred_ms;
  });
  skillEvents.forEach(function (event) {
    const player = eventPlayer(event);
    if (!player) return;
    let best = null;
    let distance = Infinity;
    groups.forEach(function (fight) {
      if (fight.player.id !== player.id) return;
      if (event.occurred_ms < fight.start - 30000 || event.occurred_ms > fight.end + 5000) return;
      const d = event.occurred_ms < fight.start ? fight.start - event.occurred_ms : Math.abs(event.occurred_ms - fight.end);
      if (d < distance) { distance = d; best = fight; }
    });
    if (best) best.events.push(event);
  });
  return groups.map(analyzeFight).sort(function (a, b) { return b.start - a.start; });
}

function analyzeFight(fight) {
  fight.events.sort(function (a, b) { return a.occurred_ms - b.occurred_ms; });
  const playerId = fight.player.id;
  let dealt = 0, received = 0, hits = 0, receivedHits = 0, misses = 0, crits = 0, casts = 0;
  let result = 'Sin terminar';
  let lastPlayer = null;
  const skillMap = {};
  const timeline = [];
  fight.events.forEach(function (event) {
    const outgoing = event.attacker_object_id === playerId;
    if (event.event_type === 'DAMAGE') {
      if (outgoing) { dealt += event.damage; hits += 1; if (event.critical) crits += 1; }
      else { received += event.damage; receivedHits += 1; }
      const key = outgoing ? String(event.skill_id || 0) : null;
      if (key !== null) {
        if (!skillMap[key]) skillMap[key] = { id: event.skill_id, name: event.skill_name || 'Ataque básico', casts: 0, hits: 0, damage: 0, criticals: 0 };
        skillMap[key].hits += 1; skillMap[key].damage += event.damage; if (event.critical) skillMap[key].criticals += 1;
      }
    } else if (event.event_type === 'MISS' && outgoing) misses += 1;
    else if (event.event_type === 'SKILL' && outgoing) {
      casts += 1;
      const key = String(event.skill_id || 0);
      if (!skillMap[key]) skillMap[key] = { id: event.skill_id, name: event.skill_name || ('Skill ' + event.skill_id), casts: 0, hits: 0, damage: 0, criticals: 0 };
      skillMap[key].casts += 1;
    } else if (event.event_type === 'DEATH') {
      result = event.target_object_id === playerId ? 'Derrota' : 'Victoria';
    }
    if (event.attacker_object_id === playerId) {
      lastPlayer = { cp: event.attacker_cp, maxCp: event.attacker_max_cp, hp: event.attacker_hp, maxHp: event.attacker_max_hp, mp: event.attacker_mp, maxMp: event.attacker_max_mp };
    } else if (event.target_object_id === playerId) {
      lastPlayer = { cp: event.target_cp, maxCp: event.target_max_cp, hp: event.target_hp, maxHp: event.target_max_hp, mp: event.target_mp, maxMp: event.target_max_mp };
    }
    timeline.push({ time: event.occurred_ms, type: event.event_type, outgoing: outgoing, skill: event.skill_name, damage: event.damage, player: lastPlayer });
  });
  const duration = Math.max(1, (fight.end - fight.start) / 1000);
  const skills = Object.keys(skillMap).map(function (key) { return skillMap[key]; }).sort(function (a, b) { return b.damage - a.damage; });
  skills.forEach(function (skill) { skill.iconUrl = data.iconUrlForSkill(skill.id); });
  const auto = skillMap['0'] ? skillMap['0'].damage : 0;
  const advice = [];
  if (casts < 3) advice.push('Usaste muy pocas habilidades activas. Prepara una barra corta de 5–7 skills y repite la prueba.');
  if (dealt > 0 && auto / dealt > 0.55) advice.push('Más de la mitad de tu daño fue ataque básico; hay skills ofensivos sin aprovechar.');
  if (lastPlayer && lastPlayer.maxMp > 0 && lastPlayer.mp / lastPlayer.maxMp > 0.65 && result === 'Derrota') advice.push('Terminaste con mucho MP: faltó convertir recursos en daño, control o defensa.');
  if ((hits + misses) > 0 && misses / (hits + misses) > 0.18) advice.push('Tu tasa de fallo físico fue alta; revisa Accuracy, DEX, nivel y buffs.');
  if (received > dealt * 1.5 && received > 0) advice.push('Recibiste mucho más daño del que devolviste; revisa defensa, resistencias y ventanas de control.');
  if (!advice.length) advice.push('La ejecución fue consistente. Compara esta pelea con otra cambiando una sola variable.');
  return {
    id: fight.id, player: fight.player, opponent: fight.opponent, start: fight.start, end: fight.end,
    duration: duration, result: result, dealt: dealt, received: received,
    dps: dealt / duration, incomingDps: received / duration,
    hits: hits, receivedHits: receivedHits, misses: misses, crits: crits, casts: casts,
    lastPlayer: lastPlayer, skills: skills, advice: advice, timeline: timeline, eventCount: fight.events.length
  };
}

async function telemetryFights() {
  try {
    const rows = await database.query('SELECT * FROM lab_combat_events ORDER BY event_id DESC LIMIT 8000');
    rows.reverse();
    return groupFights(rows);
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return [];
    throw error;
  }
}

async function telemetryCatalog() {
  try {
    const rows = await database.query('SELECT * FROM lab_player_stat_profiles ORDER BY observed_ms DESC LIMIT 2000');
    return rows.map(function (row) {
      row.classInfo = classInfo(row.class_id);
      row.baseClassInfo = classInfo(row.base_class_id);
      row.subclasses = [row.sub1_class_id, row.sub2_class_id, row.sub3_class_id].map(function (id) {
        return Number(id) >= 0 ? classInfo(id) : null;
      });
      row.slotName = Number(row.class_index) === 0 ? 'Principal' : 'Sub ' + row.class_index;
      return row;
    });
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return [];
    throw error;
  }
}

async function telemetryCoverage() {
  const classes = data.classes();
  let rows = [];
  let anchorRows = [];
  let pairRows = [];
  let buildSummary = null;
  let buildProfileSummary = null;
  let completeBuilds = 0;
  try {
    const results = await Promise.all([
      database.query('SELECT class_id,base_class_id,class_index,sub1_class_id,sub2_class_id,sub3_class_id,level,equipped_count,effect_count FROM lab_player_stat_profiles'),
      database.query("SELECT char_name,classid,race FROM characters WHERE account_name IN ('telemetryf','telemetrym')")
    ]);
    rows = results[0];
    anchorRows = results[1];
  } catch (error) {
    if (!error || error.code !== 'ER_NO_SUCH_TABLE') throw error;
  }
  try {
    pairRows = await database.query('SELECT pair_a_id,pair_b_id,active_class_id,active_class_index,level,equipped_count,effect_count,skill_count,expected_skill_count FROM lab_class_pair_profiles');
  } catch (error) {
    if (!error || error.code !== 'ER_NO_SUCH_TABLE') throw error;
  }
  try {
    const buildRows = await database.query('SELECT COUNT(*) total,SUM(selected) selected,COUNT(DISTINCT main_class_id) mains,COUNT(DISTINCT skill_hash) skillSets,MIN(skill_count) minSkills,MAX(skill_count) maxSkills,ROUND(AVG(skill_count),2) avgSkills FROM lab_four_class_candidates');
    buildSummary = buildRows[0] || null;
  } catch (error) {
    if (!error || error.code !== 'ER_NO_SUCH_TABLE') throw error;
  }
  try {
    const results = await Promise.all([
      database.query('SELECT COUNT(*) states,SUM(skill_count<>expected_skill_count) skillMismatches FROM lab_four_class_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0'),
      database.query('SELECT COUNT(*) complete FROM (SELECT main_class_id,sub1_class_id,sub2_class_id,sub3_class_id FROM lab_four_class_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0 AND skill_count=expected_skill_count GROUP BY main_class_id,sub1_class_id,sub2_class_id,sub3_class_id HAVING COUNT(*)=4 AND COUNT(DISTINCT active_class_id)=4) complete_builds')
    ]);
    buildProfileSummary = results[0][0] || null;
    completeBuilds = Number((results[1][0] || {}).complete || 0);
  } catch (error) {
    if (!error || error.code !== 'ER_NO_SUCH_TABLE') throw error;
  }
  const measured = {};
  rows.forEach(function (row) {
    const cleanSingleClass = Number(row.level) === 80 && Number(row.class_index) === 0 &&
      Number(row.equipped_count) === 0 && Number(row.effect_count) === 0 &&
      Number(row.sub1_class_id) < 0 && Number(row.sub2_class_id) < 0 && Number(row.sub3_class_id) < 0 &&
      Number(row.base_class_id) === Number(row.class_id);
    if (cleanSingleClass) measured[Number(row.class_id)] = true;
  });
  function group(items, key, order) {
    const buckets = {};
    items.forEach(function (item) {
      const value = item[key];
      if (!buckets[value]) buckets[value] = { name: value, total: 0, measured: 0 };
      buckets[value].total += 1;
      if (measured[item.id]) buckets[value].measured += 1;
    });
    return Object.keys(buckets).map(function (name) { return buckets[name]; }).sort(function (a, b) {
      if (order) return order.indexOf(a.name) - order.indexOf(b.name);
      return String(a.name).localeCompare(String(b.name), 'es');
    });
  }
  const stageOrder = ['Inicial', 'Primera profesión', 'Segunda profesión', 'Tercera profesión'];
  const raceOrder = ['Humano', 'Elfo', 'Elfo Oscuro', 'Orco', 'Enano'];
  const roots = classes.filter(function (item) { return item.stage === 0; }).map(function (root) {
    const branch = classes.filter(function (item) { return item.rootId === root.id; });
    return {
      id: root.id, name: root.name, race: root.race,
      total: branch.length,
      measured: branch.filter(function (item) { return measured[item.id]; }).length
    };
  });
  const missing = classes.filter(function (item) { return !measured[item.id]; }).map(function (item) {
    return { id: item.id, name: item.name, race: item.race, stage: item.stage, stageName: item.stageName, rootId: item.rootId };
  });
  const pairBuckets = {};
  let validPairStates = 0;
  let skillMismatches = 0;
  pairRows.forEach(function (row) {
    const valid = Number(row.level) === 80 && Number(row.equipped_count) === 0 && Number(row.effect_count) === 0 && Number(row.skill_count) > 0;
    if (!valid) return;
    validPairStates += 1;
    if (Number(row.skill_count) !== Number(row.expected_skill_count)) skillMismatches += 1;
    const key = Number(row.pair_a_id) + ':' + Number(row.pair_b_id);
    if (!pairBuckets[key]) pairBuckets[key] = {};
    pairBuckets[key][Number(row.active_class_index)] = Number(row.active_class_id);
  });
  const measuredPairs = Object.keys(pairBuckets).filter(function (key) {
    const parts = key.split(':').map(Number);
    return pairBuckets[key][0] === parts[0] && pairBuckets[key][1] === parts[1];
  }).length;
  return {
    criteria: 'Nivel 80, sin equipo, sin efectos, sin subclases y con la principal activa',
    roster: { measured: anchorRows.length, total: 9 },
    total: classes.length,
    measured: classes.length - missing.length,
    stages: group(classes, 'stageName', stageOrder),
    races: group(classes, 'race', raceOrder),
    roots: roots,
    missing: missing,
    pairs: { measured: measuredPairs, total: 465, states: validPairStates, totalStates: 930, skillMismatches: skillMismatches },
    builds: buildSummary ? {
      generated: Number(buildSummary.total), total: 125860, selected: Number(buildSummary.selected), targetSelected: 155,
      mains: Number(buildSummary.mains), skillSets: Number(buildSummary.skillSets),
      minSkills: Number(buildSummary.minSkills), maxSkills: Number(buildSummary.maxSkills), avgSkills: Number(buildSummary.avgSkills),
      measured: completeBuilds, states: Number((buildProfileSummary || {}).states || 0), totalStates: 620,
      skillMismatches: Number((buildProfileSummary || {}).skillMismatches || 0)
    } : { generated: 0, total: 125860, selected: 0, targetSelected: 155, mains: 0, skillSets: 0, measured: 0, states: 0, totalStates: 620, skillMismatches: 0 }
  };
}

async function telemetryPairs() {
  let rows = [];
  try {
    rows = await database.query('SELECT pair_a_id,pair_b_id,active_class_id,active_class_index,race_name,skill_count,passive_skill_count,active_skill_count,shared_skill_id_count,mastery_collision_count,expected_skill_count,max_cp,max_hp,max_mp,p_atk,m_atk,p_def,m_def,accuracy,evasion,p_critical,m_critical,p_atk_speed,m_atk_speed,run_speed,attack_range,observed_ms FROM lab_class_pair_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0 ORDER BY pair_a_id,pair_b_id,active_class_index');
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return [];
    throw error;
  }
  const grouped = {};
  rows.forEach(function (row) {
    const key = Number(row.pair_a_id) + ':' + Number(row.pair_b_id);
    if (!grouped[key]) {
      grouped[key] = {
        key: key,
        first: classInfo(row.pair_a_id),
        second: classInfo(row.pair_b_id),
        race: row.race_name,
        sharedSkills: Number(row.shared_skill_id_count),
        masteryCollisions: Number(row.mastery_collision_count),
        expectedSkills: Number(row.expected_skill_count),
        states: []
      };
    }
    grouped[key].states.push({
      active: classInfo(row.active_class_id), index: Number(row.active_class_index), skillCount: Number(row.skill_count),
      passiveSkills: Number(row.passive_skill_count), activeSkills: Number(row.active_skill_count),
      maxCp: Number(row.max_cp), maxHp: Number(row.max_hp), maxMp: Number(row.max_mp),
      pAtk: Number(row.p_atk), mAtk: Number(row.m_atk), pDef: Number(row.p_def), mDef: Number(row.m_def),
      accuracy: Number(row.accuracy), evasion: Number(row.evasion), pCritical: Number(row.p_critical), mCritical: Number(row.m_critical),
      pAtkSpeed: Number(row.p_atk_speed), mAtkSpeed: Number(row.m_atk_speed), runSpeed: Number(row.run_speed), attackRange: Number(row.attack_range),
      observedMs: Number(row.observed_ms)
    });
  });
  return Object.keys(grouped).map(function (key) { return grouped[key]; }).sort(function (a, b) {
    return b.masteryCollisions - a.masteryCollisions || b.sharedSkills - a.sharedSkills || a.first.id - b.first.id || a.second.id - b.second.id;
  });
}

async function telemetryBuildCandidates() {
  let rows = [];
  let profileRows = [];
  try {
    const results = await Promise.all([
      database.query(
        "SELECT main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,skill_count,passive_skill_count,active_skill_count," +
        "pair_shared_score,mastery_collision_score,mage_class_count,summoner_class_count,race_count,same_race_class_count," +
        "same_archetype_count,composition,skill_hash,selection_bucket,selection_order " +
        "FROM lab_four_class_candidates WHERE selected=1 ORDER BY selection_order"
      ),
      database.query(
        'SELECT main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,active_class_id,active_class_index,race_name,skill_count,' +
        'max_cp,max_hp,max_mp,p_atk,m_atk,p_def,m_def,accuracy,evasion,p_critical,m_critical,p_atk_speed,m_atk_speed,run_speed,observed_ms ' +
        'FROM lab_four_class_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0 ORDER BY main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,active_class_index'
      )
    ]);
    rows = results[0];
    profileRows = results[1];
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return [];
    throw error;
  }
  const profiles = {};
  profileRows.forEach(function (row) {
    const key = [row.main_class_id,row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number).join(':');
    if (!profiles[key]) profiles[key] = [];
    profiles[key].push({
      active: classInfo(row.active_class_id), index: Number(row.active_class_index), race: row.race_name,
      skillCount: Number(row.skill_count), maxCp: Number(row.max_cp), maxHp: Number(row.max_hp), maxMp: Number(row.max_mp),
      pAtk: Number(row.p_atk), mAtk: Number(row.m_atk), pDef: Number(row.p_def), mDef: Number(row.m_def),
      accuracy: Number(row.accuracy), evasion: Number(row.evasion), pCritical: Number(row.p_critical), mCritical: Number(row.m_critical),
      pAtkSpeed: Number(row.p_atk_speed), mAtkSpeed: Number(row.m_atk_speed), runSpeed: Number(row.run_speed), observedMs: Number(row.observed_ms)
    });
  });
  return rows.map(function (row) {
    const key = [row.main_class_id,row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number).join(':');
    return {
      main: classInfo(row.main_class_id),
      subclasses: [classInfo(row.sub1_class_id), classInfo(row.sub2_class_id), classInfo(row.sub3_class_id)],
      skillCount: Number(row.skill_count), passiveSkills: Number(row.passive_skill_count), activeSkills: Number(row.active_skill_count),
      sharedScore: Number(row.pair_shared_score), masteryScore: Number(row.mastery_collision_score),
      mageClasses: Number(row.mage_class_count), summoners: Number(row.summoner_class_count), races: Number(row.race_count),
      sameRaceClasses: Number(row.same_race_class_count), sameArchetype: Number(row.same_archetype_count),
      composition: row.composition, skillHash: row.skill_hash, bucket: row.selection_bucket, order: Number(row.selection_order),
      states: profiles[key] || []
    };
  });
}

async function telemetryFinalists() {
  let rows = [];
  try {
    rows = await database.query(
      'SELECT main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,category,finalist_type,finalist_rank,reason,' +
      'skill_count,passive_skill_count,active_skill_count,pair_shared_score,mastery_collision_score,skill_hash,' +
      'physical_score,magical_score,tank_score,support_score,summoner_score,hybrid_score,' +
      'p_atk_gain_pct,m_atk_gain_pct,p_def_gain_pct,m_def_gain_pct,hp_gain_pct,cp_gain_pct,mp_gain_pct,' +
      'p_atk_speed_gain_pct,m_atk_speed_gain_pct,p_critical_gain_pct,m_critical_gain_pct,evasion_gain_pct,run_gain_pct ' +
      'FROM lab_build_finalists ORDER BY finalist_rank'
    );
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return [];
    throw error;
  }
  return rows.map(function (row) {
    return {
      rank: Number(row.finalist_rank), category: row.category, type: row.finalist_type, reason: row.reason,
      main: classInfo(row.main_class_id),
      subclasses: [classInfo(row.sub1_class_id), classInfo(row.sub2_class_id), classInfo(row.sub3_class_id)],
      skillCount: Number(row.skill_count), passiveSkills: Number(row.passive_skill_count), activeSkills: Number(row.active_skill_count),
      sharedScore: Number(row.pair_shared_score), masteryScore: Number(row.mastery_collision_score), skillHash: row.skill_hash,
      scores: {
        physical: Number(row.physical_score), magical: Number(row.magical_score), tank: Number(row.tank_score),
        support: Number(row.support_score), summoner: Number(row.summoner_score), hybrid: Number(row.hybrid_score)
      },
      gains: {
        pAtk: Number(row.p_atk_gain_pct), mAtk: Number(row.m_atk_gain_pct), pDef: Number(row.p_def_gain_pct), mDef: Number(row.m_def_gain_pct),
        hp: Number(row.hp_gain_pct), cp: Number(row.cp_gain_pct), mp: Number(row.mp_gain_pct),
        pAtkSpeed: Number(row.p_atk_speed_gain_pct), mAtkSpeed: Number(row.m_atk_speed_gain_pct),
        pCritical: Number(row.p_critical_gain_pct), mCritical: Number(row.m_critical_gain_pct),
        evasion: Number(row.evasion_gain_pct), run: Number(row.run_gain_pct)
      }
    };
  });
}

async function telemetryBenchmarks() {
  let rows = [];
  try {
    rows = await database.query(
      'SELECT p.*,a.measured_runs,a.engine_mode,a.avg_actions,a.avg_hits,a.avg_casts,a.avg_critical_rate,a.avg_miss_rate,'+
      'a.avg_dps,a.avg_owner_dps,a.avg_summon_dps,a.avg_damage_received,a.avg_hps,a.avg_overheal,a.avg_mp_used,'+
      'a.avg_time_alive,a.avg_hp_cp_remaining,a.avg_control_time,a.avg_summon_uptime FROM lab_combat_benchmark_plan p LEFT JOIN ('+
      'SELECT case_id,COUNT(*) measured_runs,MIN(engine_mode) engine_mode,AVG(actions) avg_actions,AVG(hits) avg_hits,AVG(casts) avg_casts,'+
      'AVG(critical_count/NULLIF(actions,0))*100 avg_critical_rate,AVG(miss_count/NULLIF(actions,0))*100 avg_miss_rate,'+
      'AVG(damage_dealt/NULLIF(duration_seconds,0)) avg_dps,AVG(owner_damage/NULLIF(duration_seconds,0)) avg_owner_dps,'+
      'AVG(summon_damage/NULLIF(duration_seconds,0)) avg_summon_dps,AVG(damage_received) avg_damage_received,'+
      'AVG(effective_heal/NULLIF(duration_seconds,0)) avg_hps,AVG(overheal) avg_overheal,AVG(mp_used) avg_mp_used,'+
      'AVG(time_alive) avg_time_alive,AVG(hp_cp_remaining) avg_hp_cp_remaining,AVG(control_time) avg_control_time,'+
      'AVG(summon_uptime) avg_summon_uptime FROM lab_combat_benchmark_runs GROUP BY case_id) a ON a.case_id=p.case_id '+
      'ORDER BY p.finalist_rank,p.priority'
    );
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return [];
    throw error;
  }
  return rows.map(function (row) {
    return {
      id: row.case_id, rank: Number(row.finalist_rank), category: row.category, type: row.finalist_type,
      main: classInfo(row.main_class_id),
      subclasses: [classInfo(row.sub1_class_id),classInfo(row.sub2_class_id),classInfo(row.sub3_class_id)],
      active: classInfo(row.active_class_id), activeIndex: Number(row.active_class_index),
      code: row.benchmark_code, priority: Number(row.priority), opponentId: Number(row.opponent_id), opponent: row.opponent_name,
      equipmentKit: row.equipment_kit, weaponId: Number(row.weapon_id), weaponName: row.weapon_name,
      buffKit: row.buff_kit, duration: Number(row.duration_seconds),
      repetitions: Number(row.repetitions), completedRuns: Number(row.completed_runs), status: row.status,
      metrics: String(row.metrics || '').split(',').filter(Boolean), reason: row.selection_reason,
      result: {
        runs: Number(row.measured_runs || 0), mode: row.engine_mode || '', actions: Number(row.avg_actions || 0),
        hits: Number(row.avg_hits || 0), casts: Number(row.avg_casts || 0), criticalRate: Number(row.avg_critical_rate || 0),
        missRate: Number(row.avg_miss_rate || 0), dps: Number(row.avg_dps || 0), ownerDps: Number(row.avg_owner_dps || 0),
        summonDps: Number(row.avg_summon_dps || 0), damageReceived: Number(row.avg_damage_received || 0),
        hps: Number(row.avg_hps || 0), overheal: Number(row.avg_overheal || 0), mpUsed: Number(row.avg_mp_used || 0),
        timeAlive: Number(row.avg_time_alive || 0), hpCpRemaining: Number(row.avg_hp_cp_remaining || 0),
        controlTime: Number(row.avg_control_time || 0), summonUptime: Number(row.avg_summon_uptime || 0)
      }
    };
  });
}


function externalReferences() {
  const candidates = [
    path.join(portableRoot, 'research', 'external-servers'),
    path.resolve(ROOT, '..', '..', 'research', 'external-servers')
  ];
  const directory = candidates.find(function (candidate) { return fs.existsSync(candidate); });
  if (!directory) return [];
  return fs.readdirSync(directory)
    .filter(function (name) { return name.toLowerCase().endsWith('.json'); })
    .map(function (name) {
      try { return JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8')); }
      catch (error) { return { slug: name, name: name, status: 'invalid', error: error.message }; }
    })
    .sort(function (a, b) { return String(b.capturedAt || '').localeCompare(String(a.capturedAt || '')); });
}

async function telemetryNyxCalibration() {
  let summaryRows = [];
  let categoryRows = [];
  try {
    const results = await Promise.all([
      database.query(
        'SELECT scale_percent,COUNT(*) runs,COUNT(DISTINCT source_case_id) cases_count,'+
        'AVG(time_alive) avg_time_alive,MIN(time_alive) min_time_alive,MAX(time_alive) max_time_alive,'+
        'AVG(damage_received) avg_damage_received,AVG(hp_cp_remaining) avg_hp_cp_remaining,AVG(control_time) avg_control_time,'+
        'SUM(time_alive BETWEEN 10 AND 20) target_runs FROM lab_nyx_calibration_runs GROUP BY scale_percent ORDER BY scale_percent DESC'
      ),
      database.query(
        'SELECT scale_percent,category,COUNT(*) runs,AVG(time_alive) avg_time_alive,AVG(damage_received) avg_damage_received '+
        'FROM lab_nyx_calibration_runs GROUP BY scale_percent,category ORDER BY scale_percent DESC,category'
      )
    ]);
    summaryRows = results[0];
    categoryRows = results[1];
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return { expectedRuns: 360, totalRuns: 0, targetSeconds: { min: 10, max: 20 }, profiles: [] };
    throw error;
  }
  const categories = {};
  categoryRows.forEach(function (row) {
    const key = Number(row.scale_percent);
    if (!categories[key]) categories[key] = [];
    categories[key].push({
      name: row.category,
      runs: Number(row.runs),
      timeAlive: Number(row.avg_time_alive),
      damageReceived: Number(row.avg_damage_received)
    });
  });
  const profiles = summaryRows.map(function (row) {
    const scale = Number(row.scale_percent);
    return {
      scale: scale,
      label: 'Nyx ' + scale + '%',
      runs: Number(row.runs),
      cases: Number(row.cases_count),
      timeAlive: Number(row.avg_time_alive),
      minTimeAlive: Number(row.min_time_alive),
      maxTimeAlive: Number(row.max_time_alive),
      damageReceived: Number(row.avg_damage_received),
      hpCpRemaining: Number(row.avg_hp_cp_remaining),
      controlTime: Number(row.avg_control_time),
      targetRuns: Number(row.target_runs),
      categories: categories[scale] || []
    };
  });
  return {
    expectedRuns: 360,
    totalRuns: profiles.reduce(function (sum, item) { return sum + item.runs; }, 0),
    targetSeconds: { min: 10, max: 20 },
    profiles: profiles
  };
}


async function telemetryMagicProgression() {
  let rows = [];
  let eliteRows = [];
  try {
    const results = await Promise.all([
      database.query(
        'SELECT stage_index,MIN(stage_label) stage_label,MIN(main_class_id) main_class_id,MIN(sub1_class_id) sub1_class_id,'+
        'MIN(sub2_class_id) sub2_class_id,MIN(sub3_class_id) sub3_class_id,MIN(class_count) class_count,COUNT(*) runs,'+
        'AVG(skill_count) skill_count,AVG(passive_skill_count) passive_skill_count,AVG(active_skill_count) active_skill_count,'+
        'AVG(p_atk) p_atk,AVG(m_atk) m_atk,AVG(p_def) p_def,AVG(m_def) m_def,AVG(p_atk_speed) p_atk_speed,AVG(m_atk_speed) m_atk_speed,'+
        'AVG(max_hp) max_hp,AVG(max_cp) max_cp,AVG(max_mp) max_mp,AVG(damage_dealt) damage_dealt,AVG(dps) dps,'+
        'AVG(casts) casts,AVG(critical_count/NULLIF(casts,0))*100 critical_rate,AVG(mp_used) mp_used,MIN(rotation) rotation '+
        'FROM lab_magic_progression_runs GROUP BY stage_index ORDER BY stage_index'
      ),
      database.query('SELECT template_id,name,p_atk,m_atk,p_def,m_def,p_atk_speed,m_atk_speed,max_hp,max_cp,max_mp FROM lab_creature_stats WHERE template_id=900201')
    ]);
    rows = results[0];
    eliteRows = results[1];
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return { expectedRuns: 12, totalRuns: 0, stages: [], elite: null };
    throw error;
  }
  const base = rows.length ? rows[0] : null;
  function gain(value, baseValue) {
    value = Number(value || 0); baseValue = Number(baseValue || 0);
    return baseValue ? ((value / baseValue) - 1) * 100 : 0;
  }
  const stages = rows.map(function (row) {
    return {
      index: Number(row.stage_index), label: row.stage_label, runs: Number(row.runs), classCount: Number(row.class_count),
      main: classInfo(row.main_class_id),
      subclasses: [row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number).filter(function(id){return id >= 0;}).map(classInfo),
      skillCount: Number(row.skill_count), passiveSkills: Number(row.passive_skill_count), activeSkills: Number(row.active_skill_count),
      pAtk: Number(row.p_atk), mAtk: Number(row.m_atk), pDef: Number(row.p_def), mDef: Number(row.m_def),
      pAtkSpeed: Number(row.p_atk_speed), mAtkSpeed: Number(row.m_atk_speed),
      maxHp: Number(row.max_hp), maxCp: Number(row.max_cp), maxMp: Number(row.max_mp),
      damage: Number(row.damage_dealt), dps: Number(row.dps), casts: Number(row.casts),
      criticalRate: Number(row.critical_rate), mpUsed: Number(row.mp_used), rotation: row.rotation,
      gains: {
        mAtk: gain(row.m_atk, base && base.m_atk), mAtkSpeed: gain(row.m_atk_speed, base && base.m_atk_speed),
        dps: gain(row.dps, base && base.dps), skills: gain(row.skill_count, base && base.skill_count)
      }
    };
  });
  const elite = eliteRows.length ? {
    id: Number(eliteRows[0].template_id), name: eliteRows[0].name,
    pAtk: Number(eliteRows[0].p_atk), mAtk: Number(eliteRows[0].m_atk),
    pDef: Number(eliteRows[0].p_def), mDef: Number(eliteRows[0].m_def),
    pAtkSpeed: Number(eliteRows[0].p_atk_speed), mAtkSpeed: Number(eliteRows[0].m_atk_speed),
    maxHp: Number(eliteRows[0].max_hp), maxCp: Number(eliteRows[0].max_cp), maxMp: Number(eliteRows[0].max_mp)
  } : null;
  return { expectedRuns: 12, totalRuns: stages.reduce(function(sum,item){return sum+item.runs;},0), stages: stages, elite: elite };
}

async function telemetryMagicComparison() {
  let rows = [];
  try {
    rows = await database.query(
      'SELECT stage_index,protocol,MIN(stage_label) stage_label,MIN(main_class_id) main_class_id,'+
      'MIN(sub1_class_id) sub1_class_id,MIN(sub2_class_id) sub2_class_id,MIN(sub3_class_id) sub3_class_id,'+
      'MIN(class_count) class_count,COUNT(*) runs,AVG(skill_count) skill_count,AVG(passive_skill_count) passive_skill_count,'+
      'AVG(active_skill_count) active_skill_count,AVG(m_atk) m_atk,AVG(m_atk_speed) m_atk_speed,AVG(max_mp) max_mp,'+
      'MIN(selected_skill_id) selected_skill_id,MIN(selected_skill_level) selected_skill_level,'+
      'MIN(selected_skill_name) selected_skill_name,AVG(selected_skill_power) selected_skill_power,'+
      'AVG(selected_skill_cycle_ms) selected_skill_cycle_ms,AVG(damage_dealt) damage_dealt,AVG(dps) dps,'+
      'AVG(casts) casts,AVG(critical_count/NULLIF(casts,0))*100 critical_rate,AVG(mp_used) mp_used,MIN(rotation) rotation '+
      'FROM lab_magic_comparison_runs GROUP BY stage_index,protocol ORDER BY stage_index,protocol'
    );
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return { expectedRuns: 240, totalRuns: 0, stages: [] };
    throw error;
  }

  function percent(value, base) {
    value = Number(value || 0); base = Number(base || 0);
    return base ? ((value / base) - 1) * 100 : 0;
  }
  function profile(row) {
    if (!row) return null;
    const casts = Number(row.casts);
    const damage = Number(row.damage_dealt);
    return {
      protocol: row.protocol, runs: Number(row.runs),
      skill: {
        id: Number(row.selected_skill_id), level: Number(row.selected_skill_level), name: row.selected_skill_name,
        power: Number(row.selected_skill_power), cycleMs: Number(row.selected_skill_cycle_ms)
      },
      mAtk: Number(row.m_atk), mAtkSpeed: Number(row.m_atk_speed), maxMp: Number(row.max_mp),
      skillCount: Number(row.skill_count), passiveSkills: Number(row.passive_skill_count), activeSkills: Number(row.active_skill_count),
      damage: damage, dps: Number(row.dps), casts: casts, criticalRate: Number(row.critical_rate),
      mpUsed: Number(row.mp_used), damagePerCast: casts ? damage / casts : 0, rotation: row.rotation
    };
  }

  const grouped = {};
  rows.forEach(function (row) {
    const index = Number(row.stage_index);
    if (!grouped[index]) grouped[index] = { row: row, protocols: {} };
    grouped[index].protocols[row.protocol] = row;
  });
  const stages = Object.keys(grouped).map(Number).sort(function (a, b) { return a - b; }).map(function (index) {
    const group = grouped[index];
    const fixed = profile(group.protocols.FIXED_HURRICANE);
    const best = profile(group.protocols.BEST_AVAILABLE);
    const row = group.row;
    return {
      index: index, label: row.stage_label, classCount: Number(row.class_count),
      main: classInfo(row.main_class_id),
      subclasses: [row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number).filter(function(id){return id >= 0;}).map(classInfo),
      fixed: fixed, best: best,
      bestVsFixed: {
        dps: best && fixed ? percent(best.dps, fixed.dps) : 0,
        damagePerCast: best && fixed ? percent(best.damagePerCast, fixed.damagePerCast) : 0,
        casts: best && fixed ? percent(best.casts, fixed.casts) : 0
      }
    };
  });
  const baseFixed = stages.length ? stages[0].fixed : null;
  stages.forEach(function (stage) {
    stage.statEffect = {
      mAtk: stage.fixed && baseFixed ? percent(stage.fixed.mAtk, baseFixed.mAtk) : 0,
      expectedMagicDamage: stage.fixed && baseFixed && baseFixed.mAtk ? (Math.sqrt(stage.fixed.mAtk / baseFixed.mAtk) - 1) * 100 : 0,
      observedFixedDps: stage.fixed && baseFixed ? percent(stage.fixed.dps, baseFixed.dps) : 0
    };
  });
  return { expectedRuns: 240, totalRuns: rows.reduce(function(sum,row){return sum+Number(row.runs);},0), stages: stages };
}




async function telemetryPhysicalRaceBaseline() {
  let rows = [];
  try {
    rows = await database.query(
      'SELECT anchor_root_class_id,race_id,MIN(race_name) race_name,stage_index,protocol,MIN(stage_label) stage_label,'+
      'MIN(main_class_id) main_class_id,MIN(sub1_class_id) sub1_class_id,MIN(sub2_class_id) sub2_class_id,MIN(sub3_class_id) sub3_class_id,'+
      'MIN(class_count) class_count,COUNT(*) runs,AVG(skill_count) skill_count,AVG(passive_skill_count) passive_skill_count,'+
      'AVG(active_skill_count) active_skill_count,AVG(p_atk) p_atk,AVG(p_atk_speed) p_atk_speed,AVG(p_critical) p_critical,'+
      'AVG(accuracy) accuracy,AVG(max_hp) max_hp,AVG(max_cp) max_cp,AVG(max_mp) max_mp,AVG(stat_str) stat_str,AVG(stat_dex) stat_dex,AVG(stat_con) stat_con,'+
      'MIN(selected_skill_id) selected_skill_id,MIN(selected_skill_level) selected_skill_level,MIN(selected_skill_name) selected_skill_name,'+
      'AVG(selected_skill_power) selected_skill_power,AVG(selected_skill_cycle_ms) selected_skill_cycle_ms,'+
      'AVG(damage_dealt) damage_dealt,AVG(dps) dps,STDDEV_POP(dps) dps_sd,AVG(actions) actions,AVG(hits) hits,'+
      'AVG(critical_count/NULLIF(hits,0))*100 critical_rate,AVG(miss_count/NULLIF(actions,0))*100 miss_rate,AVG(mp_used) mp_used,MIN(rotation) rotation '+
      'FROM lab_physical_race_runs GROUP BY anchor_root_class_id,race_id,stage_index,protocol ORDER BY anchor_root_class_id,stage_index,protocol'
    );
  } catch (error) {
    if (error && error.code === 'ER_NO_SUCH_TABLE') return { expectedRuns: 240, totalRuns: 0, baselines: [] };
    throw error;
  }
  function percent(value, base) {
    value = Number(value || 0); base = Number(base || 0);
    return base ? ((value / base) - 1) * 100 : 0;
  }
  function profile(row) {
    if (!row) return null;
    const actions = Number(row.actions);
    const damage = Number(row.damage_dealt);
    return {
      protocol: row.protocol, runs: Number(row.runs),
      skill: { id: Number(row.selected_skill_id), level: Number(row.selected_skill_level), name: row.selected_skill_name, power: Number(row.selected_skill_power), cycleMs: Number(row.selected_skill_cycle_ms) },
      pAtk: Number(row.p_atk), pAtkSpeed: Number(row.p_atk_speed), pCritical: Number(row.p_critical), accuracy: Number(row.accuracy),
      maxHp: Number(row.max_hp), maxCp: Number(row.max_cp), maxMp: Number(row.max_mp),
      str: Number(row.stat_str), dex: Number(row.stat_dex), con: Number(row.stat_con),
      skillCount: Number(row.skill_count), passiveSkills: Number(row.passive_skill_count), activeSkills: Number(row.active_skill_count),
      damage: damage, dps: Number(row.dps), dpsSd: Number(row.dps_sd), actions: actions, hits: Number(row.hits),
      criticalRate: Number(row.critical_rate), missRate: Number(row.miss_rate), mpUsed: Number(row.mp_used),
      damagePerAction: actions ? damage / actions : 0, rotation: row.rotation
    };
  }
  const roots = {};
  rows.forEach(function(row) {
    const root = Number(row.anchor_root_class_id);
    const stage = Number(row.stage_index);
    if (!roots[root]) roots[root] = { rootId: root, raceId: Number(row.race_id), race: row.race_name, stages: {} };
    if (!roots[root].stages[stage]) roots[root].stages[stage] = { row: row, protocols: {} };
    roots[root].stages[stage].protocols[row.protocol] = row;
  });
  const baselines = Object.keys(roots).map(Number).sort(function(a,b){return a-b;}).map(function(rootId) {
    const root = roots[rootId];
    const stages = Object.keys(root.stages).map(Number).sort(function(a,b){return a-b;}).map(function(index) {
      const group = root.stages[index];
      const fixed = profile(group.protocols.FIXED_AUTOATTACK);
      const best = profile(group.protocols.BEST_COMPATIBLE);
      const row = group.row;
      return {
        index: index, label: row.stage_label, classCount: Number(row.class_count),
        main: classInfo(row.main_class_id),
        subclasses: [row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number).filter(function(id){return id >= 0;}).map(classInfo),
        fixed: fixed, best: best,
        bestVsFixedDps: fixed && best ? percent(best.dps, fixed.dps) : 0
      };
    });
    const baseFixed = stages.length ? stages[0].fixed : null;
    stages.forEach(function(stage) {
      stage.fixedVsBase = stage.fixed && baseFixed ? {
        pAtk: percent(stage.fixed.pAtk, baseFixed.pAtk),
        pAtkSpeed: percent(stage.fixed.pAtkSpeed, baseFixed.pAtkSpeed),
        dps: percent(stage.fixed.dps, baseFixed.dps)
      } : { pAtk: 0, pAtkSpeed: 0, dps: 0 };
    });
    return { rootClassId: root.rootId, raceId: root.raceId, race: root.race, racePreserved: new Set(rows.filter(function(row){return Number(row.anchor_root_class_id)===root.rootId;}).map(function(row){return row.race_name;})).size === 1, stages: stages };
  });
  return { expectedRuns: 240, totalRuns: rows.reduce(function(sum,row){return sum+Number(row.runs);},0), baselines: baselines };
}

async function api(req, res, url) {
  const route = url.pathname;
  if (req.method === 'GET' && route === '/api/status') {
    const statuses = await Promise.all([portOpen(2106), portOpen(7777), database.ping().catch(function () { return false; })]);
    let telemetryCount = 0;
    try { const count = await database.query('SELECT COUNT(*) AS total FROM lab_combat_events'); telemetryCount = count[0].total; } catch (_) {}
    return json(res, 200, { login: statuses[0], game: statuses[1], database: statuses[2], telemetryCount: telemetryCount, officeMode: officeMode, state: readState() });
  }
  if (req.method === 'GET' && route === '/api/classes') return json(res, 200, data.classes());
  let match = route.match(/^\/api\/classes\/(\d+)$/);
  if (match && req.method === 'GET') return json(res, 200, data.template(match[1]));
  if (match && req.method === 'PATCH') {
    const result = data.updateTemplate(match[1], await body(req));
    writeState({ requiresRestart: true, lastChange: Date.now(), lastBackup: result.backup });
    return json(res, 200, result);
  }
  if (req.method === 'GET' && route === '/api/skills') return json(res, 200, data.skills(url.searchParams.get('q'), url.searchParams.get('limit')));
  match = route.match(/^\/api\/skills\/(\d+)$/);
  if (match && req.method === 'GET') return json(res, 200, data.skill(match[1]));
  if (match && req.method === 'PATCH') {
    const result = data.updateSkill(match[1], await body(req));
    writeState({ requiresRestart: true, lastChange: Date.now(), lastBackup: result.backup });
    return json(res, 200, result);
  }
  if (req.method === 'GET' && route === '/api/characters') return json(res, 200, await characters());
  match = route.match(/^\/api\/characters\/(\d+)\/base-stats$/);
  if (match && req.method === 'PATCH') {
    const result = await updateCharacterBaseStats(match[1], await body(req));
    writeState({ requiresRestart: true, lastChange: Date.now(), lastBackup: result.backup });
    return json(res, 200, result);
  }
  match = route.match(/^\/api\/characters\/(\d+)$/);
  if (match && req.method === 'GET') return json(res, 200, await characterDetail(match[1]));
  if (match && req.method === 'PATCH') {
    await updateCharacter(match[1], await body(req));
    return json(res, 200, await characterDetail(match[1]));
  }
  if (req.method === 'GET' && route === '/api/opponents') return json(res, 200, data.opponents());
  if (req.method === 'POST' && route === '/api/opponents') {
    const result = data.createOpponent(await body(req));
    writeState({ requiresRestart: true, lastChange: Date.now(), lastBackup: result.backup });
    return json(res, 201, result);
  }
  match = route.match(/^\/api\/opponents\/(\d+)$/);
  if (match && req.method === 'GET') return json(res, 200, await opponentDetail(match[1]));
  if (match && req.method === 'PATCH') {
    const result = data.updateOpponent(match[1], await body(req));
    writeState({ requiresRestart: true, lastChange: Date.now(), lastBackup: result.backup });
    return json(res, 200, await opponentDetail(match[1]));
  }
  if (req.method === 'GET' && route === '/api/telemetry/fights') {
    const fights = await telemetryFights();
    return json(res, 200, fights.map(function (fight) {
      const copy = Object.assign({}, fight); delete copy.timeline; return copy;
    }));
  }
  if (req.method === 'GET' && route === '/api/telemetry/catalog') return json(res, 200, await telemetryCatalog());
  if (req.method === 'GET' && route === '/api/telemetry/coverage') return json(res, 200, await telemetryCoverage());
  if (req.method === 'GET' && route === '/api/telemetry/pairs') return json(res, 200, await telemetryPairs());
  if (req.method === 'GET' && route === '/api/telemetry/build-candidates') return json(res, 200, await telemetryBuildCandidates());
  if (req.method === 'GET' && route === '/api/telemetry/finalists') return json(res, 200, await telemetryFinalists());
	if (req.method === 'GET' && route === '/api/telemetry/benchmarks') return json(res, 200, await telemetryBenchmarks());
	if (req.method === 'GET' && route === '/api/telemetry/nyx-calibration') return json(res, 200, await telemetryNyxCalibration());
	if (req.method === 'GET' && route === '/api/telemetry/magic-progression') return json(res, 200, await telemetryMagicProgression());
	if (req.method === 'GET' && route === '/api/telemetry/magic-comparison') return json(res, 200, await telemetryMagicComparison());
	if (req.method === 'GET' && route === '/api/telemetry/physical-race-baseline') return json(res, 200, await telemetryPhysicalRaceBaseline());
	if (req.method === 'GET' && route === '/api/telemetry/external-references') return json(res, 200, externalReferences());
  match = route.match(/^\/api\/telemetry\/fights\/(\d+)$/);
  if (match && req.method === 'GET') {
    const fights = await telemetryFights();
    const fight = fights.find(function (item) { return item.id === match[1]; });
    if (!fight) throw httpError(404, 'Combate no encontrado.');
    return json(res, 200, fight);
  }
  if (req.method === 'POST' && route === '/api/restart') {
    if (officeMode) throw httpError(409, 'El reinicio está deshabilitado en modo oficina. Los cambios quedan guardados para aplicarlos en la PC principal.');
    if (!fs.existsSync(config.paths.restartScript)) throw httpError(404, 'No se encontró el script de reinicio.');
    const process = childProcess.spawn('powershell.exe', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', config.paths.restartScript], {
      detached: true, stdio: 'ignore', windowsHide: true
    });
    process.unref();
    writeState({ requiresRestart: false });
    return json(res, 202, { started: true, message: 'Reinicio solicitado. Si el cliente está conectado, el protector lo rechazará.' });
  }
  throw httpError(404, 'Ruta no encontrada.');
}

function staticFile(req, res, url) {
  const requested = url.pathname === '/' ? '/index.html' : url.pathname;
  const file = path.resolve(PUBLIC, '.' + requested);
  if (file.indexOf(PUBLIC) !== 0 || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end('No encontrado'); return;
  }
  const content = fs.readFileSync(file);
  res.writeHead(200, { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream', 'Content-Length': content.length });
  res.end(content);
}

const server = http.createServer(async function (req, res) {
  const url = new URL(req.url, 'http://' + config.host + ':' + config.port);
  try {
    if (url.pathname.indexOf('/api/') === 0) await api(req, res, url);
    else staticFile(req, res, url);
  } catch (error) {
    console.error(error);
    json(res, error.status || 500, { error: error.message || 'Error interno.' });
  }
});

server.listen(config.port, config.host, function () {
  console.log('Laboratorio L2 listo en http://' + config.host + ':' + config.port);
});
