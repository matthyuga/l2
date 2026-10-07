'use strict';

const fs = require('fs');
const path = require('path');

const TEMPLATE_FIELDS = [
  'baseINT', 'baseSTR', 'baseCON', 'baseMEN', 'baseDEX', 'baseWIT',
  'basePAtk', 'baseCritRate', 'basePAtkSpd', 'baseMAtk', 'baseAtkRange', 'baseRndDam'
];
const LEVEL_FIELDS = ['hp', 'mp', 'cp', 'hpRegen', 'mpRegen', 'cpRegen'];
const DIRECT_SKILL_FIELDS = [
  'power', 'mpConsume', 'mpInitialConsume', 'hpConsume', 'hitTime',
  'reuseDelay', 'castRange', 'effectRange', 'magicLevel'
];
const RACES = {
  0: 'Humano', 10: 'Humano', 18: 'Elfo', 25: 'Elfo',
  31: 'Elfo Oscuro', 38: 'Elfo Oscuro', 44: 'Orco', 49: 'Orco', 53: 'Enano'
};

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function attrs(source) {
  const result = {};
  String(source).replace(/([\w:-]+)="([^"]*)"/g, function (_, key, value) {
    result[key] = value;
    return _;
  });
  return result;
}

function getTag(xml, tag) {
  const match = String(xml).match(new RegExp('<' + escapeRegExp(tag) + '>([^<]*)</' + escapeRegExp(tag) + '>', 'i'));
  return match ? match[1].trim() : null;
}

function numberOrText(value) {
  if (value === null || value === '') return value;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : value;
}

function stageName(stage) {
  return ['Inicial', 'Primera profesión', 'Segunda profesión', 'Tercera profesión'][stage] || 'Especial';
}

function createDataStore(config) {
  const serverData = config.paths.serverData;
  const sourceData = config.paths.sourceData;
  const classListFile = path.join(serverData, 'stats', 'players', 'classList.xml');
  const templateRoot = path.join(serverData, 'stats', 'players', 'templates');
  const skillRoot = path.join(serverData, 'stats', 'skills');
  const arenaNpcFile = path.join(serverData, 'stats', 'npcs', 'custom', 'solo_arena.xml');
  const arenaSpawnFile = path.join(serverData, 'spawns', 'Others', 'SoloArena.xml');
  const classSkillRoot = path.join(serverData, 'stats', 'players', 'skillTrees');
  const skillIconRoot = path.join(__dirname, '..', 'public', 'assets', 'skill-icons');
  let classesCache = null;
  let templateFiles = null;
  let skillsCache = null;
  let classSkillFiles = null;

  function walk(dir, test, output) {
    const target = output || [];
    fs.readdirSync(dir, { withFileTypes: true }).forEach(function (entry) {
      const file = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(file, test, target);
      else if (!test || test(file)) target.push(file);
    });
    return target;
  }

  function classes() {
    if (classesCache) return classesCache;
    const xml = fs.readFileSync(classListFile, 'utf8');
    const list = [];
    const byId = {};
    xml.replace(/<class\s+([^>]*?)\/>/g, function (_, raw) {
      const a = attrs(raw);
      const item = {
        id: Number(a.classId),
        name: a.name,
        parentId: a.parentClassId === undefined ? null : Number(a.parentClassId)
      };
      list.push(item);
      byId[item.id] = item;
      return _;
    });
    list.forEach(function (item) {
      let current = item;
      let depth = 0;
      while (current.parentId !== null && byId[current.parentId]) {
        current = byId[current.parentId];
        depth += 1;
      }
      item.rootId = current.id;
      item.race = RACES[current.id] || 'Desconocida';
      item.stage = depth;
      item.stageName = stageName(depth);
      const chain = [];
      let cursor = item;
      while (cursor) {
        chain.unshift(cursor.name);
        cursor = cursor.parentId !== null ? byId[cursor.parentId] : null;
      }
      item.path = chain.join(' › ');
    });
    classesCache = { list: list, byId: byId };
    return classesCache;
  }

  function buildTemplateMap() {
    const map = {};
    walk(templateRoot, function (file) { return /\.xml$/i.test(file); }).forEach(function (file) {
      const xml = fs.readFileSync(file, 'utf8');
      const id = Number(getTag(xml, 'classId'));
      if (Number.isFinite(id)) map[id] = file;
    });
    templateFiles = map;
    return map;
  }

  function template(classId) {
    const classInfo = classes().byId[Number(classId)];
    const files = templateFiles || buildTemplateMap();
    const file = files[Number(classId)];
    if (!classInfo || !file) throw httpError(404, 'No se encontró la plantilla de esa clase.');
    const xml = fs.readFileSync(file, 'utf8');
    const staticStats = {};
    TEMPLATE_FIELDS.forEach(function (field) { staticStats[field] = numberOrText(getTag(xml, field)); });
    const moveBlock = (xml.match(/<baseMoveSpd>([\s\S]*?)<\/baseMoveSpd>/i) || [null, ''])[1];
    staticStats.walk = numberOrText(getTag(moveBlock, 'walk'));
    staticStats.run = numberOrText(getTag(moveBlock, 'run'));
    const levelBlock = (xml.match(/<level\s+val="80">([\s\S]*?)<\/level>/i) || [null, ''])[1];
    const level80 = {};
    LEVEL_FIELDS.forEach(function (field) { level80[field] = numberOrText(getTag(levelBlock, field)); });
    return {
      classInfo: classInfo,
      staticStats: staticStats,
      level80: level80,
      file: path.relative(serverData, file)
    };
  }

  function playerBaseStats(classId, level) {
    const files = templateFiles || buildTemplateMap();
    const file = files[Number(classId)];
    if (!file) throw httpError(404, 'No se encontró la plantilla base de esa clase.');
    const xml = fs.readFileSync(file, 'utf8');
    const staticBlock = (xml.match(/<staticData>([\s\S]*?)<\/staticData>/i) || [null, ''])[1];
    const pDefBlock = (staticBlock.match(/<basePDef>([\s\S]*?)<\/basePDef>/i) || [null, ''])[1];
    const mDefBlock = (staticBlock.match(/<baseMDef>([\s\S]*?)<\/baseMDef>/i) || [null, ''])[1];
    const moveBlock = (staticBlock.match(/<baseMoveSpd>([\s\S]*?)<\/baseMoveSpd>/i) || [null, ''])[1];
    const safeLevel = Math.max(1, Math.min(80, Number(level) || 1));
    const levelPattern = new RegExp('<level\\s+val="' + safeLevel + '">([\\s\\S]*?)<\\/level>', 'i');
    const levelBlock = (xml.match(levelPattern) || [null, ''])[1];
    function numeric(source, tag, fallback) {
      const value = numberOrText(getTag(source, tag));
      return typeof value === 'number' ? value : fallback;
    }
    function total(source, fields) {
      return fields.reduce(function (sum, field) { return sum + numeric(source, field, 0); }, 0);
    }
    const dex = numeric(staticBlock, 'baseDEX', 0);
    let accuracy = (Math.sqrt(dex) * 6) + safeLevel;
    if (safeLevel > 77) accuracy += safeLevel - 76;
    if (safeLevel > 69) accuracy += safeLevel - 69;
    let evasion = (Math.sqrt(dex) * 6) + safeLevel;
    if (safeLevel >= 70) evasion += (safeLevel - 69) * (safeLevel >= 78 ? 1.2 : 1);
    return {
      pAtk: numeric(staticBlock, 'basePAtk', 0),
      mAtk: numeric(staticBlock, 'baseMAtk', 0),
      pDef: total(pDefBlock, ['chest', 'legs', 'head', 'feet', 'gloves', 'underwear', 'cloak']),
      mDef: total(mDefBlock, ['rear', 'lear', 'rfinger', 'rfinger', 'neck']),
      pAtkSpeed: numeric(staticBlock, 'basePAtkSpd', 300),
      mAtkSpeed: numeric(staticBlock, 'baseMAtkSpd', 333),
      runSpeed: numeric(moveBlock, 'run', 120),
      walkSpeed: numeric(moveBlock, 'walk', 50),
      pCritical: numeric(staticBlock, 'baseCritRate', 4),
      accuracy: Math.round(accuracy),
      evasion: Math.round(evasion),
      attackRange: numeric(staticBlock, 'baseAtkRange', 40),
      maxHp: numeric(levelBlock, 'hp', 0),
      maxMp: numeric(levelBlock, 'mp', 0),
      maxCp: numeric(levelBlock, 'cp', 0),
      str: numeric(staticBlock, 'baseSTR', 0),
      dex: dex,
      con: numeric(staticBlock, 'baseCON', 0),
      int: numeric(staticBlock, 'baseINT', 0),
      wit: numeric(staticBlock, 'baseWIT', 0),
      men: numeric(staticBlock, 'baseMEN', 0)
    };
  }

  function validateNumber(value, label, min, max) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
      throw httpError(400, label + ' debe estar entre ' + min + ' y ' + max + '.');
    }
    return String(parsed);
  }

  function replaceTag(xml, tag, value) {
    const regex = new RegExp('(<'+ escapeRegExp(tag) + '>)[^<]*(</' + escapeRegExp(tag) + '>)', 'i');
    if (!regex.test(xml)) throw httpError(400, 'La plantilla no contiene ' + tag + '.');
    return xml.replace(regex, '$1' + value + '$2');
  }

  function replaceTagInBlock(xml, blockRegex, tag, value) {
    return xml.replace(blockRegex, function (whole, body) {
      const updated = replaceTag(body, tag, value);
      return whole.replace(body, updated);
    });
  }

  function timestamp() {
    return new Date().toISOString().replace(/[:.]/g, '-');
  }

  function backupAndWrite(serverFile, content, reason) {
    const relative = path.relative(serverData, serverFile);
    const sourceFile = path.join(sourceData, relative);
    const backupDir = path.join(config.paths.backupRoot, timestamp() + '-' + reason);
    [serverFile, sourceFile].forEach(function (file) {
      if (!fs.existsSync(file)) return;
      const backupFile = path.join(backupDir, path.relative(path.parse(file).root, file));
      fs.mkdirSync(path.dirname(backupFile), { recursive: true });
      fs.copyFileSync(file, backupFile);
      const temp = file + '.lab-panel.tmp';
      fs.writeFileSync(temp, content, 'utf8');
      fs.renameSync(temp, file);
    });
    return backupDir;
  }

  function updateTemplate(classId, payload) {
    const files = templateFiles || buildTemplateMap();
    const file = files[Number(classId)];
    if (!file) throw httpError(404, 'No se encontró la plantilla.');
    let xml = fs.readFileSync(file, 'utf8');
    const stats = payload.staticStats || {};
    TEMPLATE_FIELDS.forEach(function (field) {
      if (stats[field] !== undefined) xml = replaceTag(xml, field, validateNumber(stats[field], field, 0, 10000000));
    });
    if (stats.walk !== undefined) {
      xml = replaceTagInBlock(xml, /<baseMoveSpd>([\s\S]*?)<\/baseMoveSpd>/i, 'walk', validateNumber(stats.walk, 'walk', 0, 1000));
    }
    if (stats.run !== undefined) {
      xml = replaceTagInBlock(xml, /<baseMoveSpd>([\s\S]*?)<\/baseMoveSpd>/i, 'run', validateNumber(stats.run, 'run', 0, 1000));
    }
    const level80 = payload.level80 || {};
    LEVEL_FIELDS.forEach(function (field) {
      if (level80[field] !== undefined) {
        xml = replaceTagInBlock(xml, /<level\s+val="80">([\s\S]*?)<\/level>/i, field, validateNumber(level80[field], field + ' nivel 80', 0, 10000000));
      }
    });
    const backup = backupAndWrite(file, xml, 'clase-' + classId);
    return { saved: true, backup: backup, requiresRestart: true };
  }

  function buildSkills() {
    const list = [];
    const byId = {};
    walk(skillRoot, function (file) { return /\.xml$/i.test(file); }).forEach(function (file) {
      const xml = fs.readFileSync(file, 'utf8');
      const regex = /<skill\s+([^>]*\bid="\d+"[^>]*)>[\s\S]*?<\/skill>/g;
      let match;
      while ((match = regex.exec(xml)) !== null) {
        const a = attrs(match[1]);
        const item = {
          id: Number(a.id), name: a.name || ('Skill ' + a.id), levels: Number(a.levels || 1),
          icon: getTag(match[0], 'icon'),
          file: file, relativeFile: path.relative(serverData, file)
        };
        list.push(item);
        if (!byId[item.id]) byId[item.id] = item;
      }
    });
    list.sort(function (a, b) { return a.id - b.id; });
    skillsCache = { list: list, byId: byId };
    return skillsCache;
  }

  function skills(query, limit) {
    const cache = skillsCache || buildSkills();
    const term = String(query || '').trim().toLowerCase();
    const max = Math.min(Number(limit) || 80, 200);
    if (!term) return cache.list.slice(0, max).map(skillSummary);
    return cache.list.filter(function (skill) {
      return String(skill.id) === term || skill.name.toLowerCase().indexOf(term) !== -1;
    }).slice(0, max).map(skillSummary);
  }

  function skillSummary(skill) {
    return { id: skill.id, name: skill.name, levels: skill.levels, icon: skill.icon, iconUrl: iconUrl(skill.icon, skill.id), file: skill.relativeFile };
  }

  function iconUrl(icon, skillId) {
    const raw = String(icon || '').trim().toLowerCase();
    const candidates = [];
    if (raw) candidates.push(raw.substring(raw.lastIndexOf('.') + 1));
    if (skillId !== undefined && skillId !== null) candidates.push('skill' + String(Number(skillId)).padStart(4, '0'));
    for (let index = 0; index < candidates.length; index += 1) {
      const name = candidates[index].replace(/[^a-z0-9_-]/g, '');
      if (name && fs.existsSync(path.join(skillIconRoot, name + '.png'))) return '/assets/skill-icons/' + name + '.png';
    }
    return null;
  }

  function locateSkill(skillId) {
    const cache = skillsCache || buildSkills();
    const item = cache.byId[Number(skillId)];
    if (!item) throw httpError(404, 'No se encontró el skill ' + skillId + '.');
    const xml = fs.readFileSync(item.file, 'utf8');
    const regex = new RegExp('<skill\\s+([^>]*\\bid="' + Number(skillId) + '"[^>]*)>([\\s\\S]*?)<\\/skill>');
    const match = xml.match(regex);
    if (!match) throw httpError(404, 'No se pudo abrir el bloque del skill.');
    return { item: item, xml: xml, regex: regex, attrs: attrs(match[1]), body: match[2], whole: match[0] };
  }

  function skill(skillId) {
    const located = locateSkill(skillId);
    const tables = {};
    located.body.replace(/<table\s+name="#([^"]+)">([^<]*)<\/table>/g, function (_, name, values) {
      tables[name] = values.trim();
      return _;
    });
    const values = {};
    DIRECT_SKILL_FIELDS.forEach(function (field) {
      const value = getTag(located.body, field);
      // References such as #power and #mpConsume are edited in their tables.
      // Keep this section for literal numeric values only.
      if ((value !== null) && /^-?\d/.test(value)) values[field] = value;
    });
    return Object.assign(skillSummary(located.item), {
      icon: getTag(located.body, 'icon'),
      iconUrl: iconUrl(getTag(located.body, 'icon'), skillId),
      operateType: getTag(located.body, 'operateType'),
      targetType: getTag(located.body, 'targetType'),
      tables: tables,
      values: values
    });
  }

  function validateNumericList(value, label) {
    const normalized = String(value).trim().replace(/\s+/g, ' ');
    if (!normalized || !/^-?\d+(?:\.\d+)?(?:\s+-?\d+(?:\.\d+)?)*$/.test(normalized)) {
      throw httpError(400, label + ' debe contener solamente números separados por espacios.');
    }
    return normalized;
  }

  function updateSkill(skillId, payload) {
    const located = locateSkill(skillId);
    let body = located.body;
    const tables = payload.tables || {};
    Object.keys(tables).forEach(function (name) {
      const clean = validateNumericList(tables[name], '#' + name);
      const regex = new RegExp('(<table\\s+name="#' + escapeRegExp(name) + '">)[^<]*(<\\/table>)');
      if (!regex.test(body)) throw httpError(400, 'El skill no contiene la tabla #' + name + '.');
      body = body.replace(regex, '$1' + clean + '$2');
    });
    const values = payload.values || {};
    Object.keys(values).forEach(function (name) {
      if (DIRECT_SKILL_FIELDS.indexOf(name) === -1) throw httpError(400, 'Campo no editable: ' + name);
      const clean = validateNumericList(values[name], name);
      body = replaceTag(body, name, clean);
    });
    const updatedBlock = located.whole.replace(located.body, body);
    const updatedXml = located.xml.replace(located.whole, updatedBlock);
    const backup = backupAndWrite(located.item.file, updatedXml, 'skill-' + skillId);
    skillsCache = null;
    return { saved: true, backup: backup, requiresRestart: true };
  }

  function updateElementAttr(xml, tag, key, value) {
    const regex = new RegExp('<' + escapeRegExp(tag) + '\\b([^>]*)>', 'i');
    if (!regex.test(xml)) throw httpError(400, 'El rival no contiene <' + tag + '>.');
    return xml.replace(regex, function (whole, raw) {
      const attribute = new RegExp('(\\s' + escapeRegExp(key) + '=\")[^\"]*(\")', 'i');
      if (attribute.test(raw)) return '<' + tag + raw.replace(attribute, '$1' + value + '$2') + '>';
      return '<' + tag + raw.replace(/\\s*\/$/, '') + ' ' + key + '=\"' + value + '\"' + (/\/$/.test(raw.trim()) ? ' /' : '') + '>';
    });
  }

  function arenaXml() {
    if (!fs.existsSync(arenaNpcFile)) throw httpError(404, 'No se encontró solo_arena.xml.');
    return fs.readFileSync(arenaNpcFile, 'utf8');
  }

  function locateOpponent(id) {
    const xml = arenaXml();
    const regex = new RegExp('<npc\\s+([^>]*\\bid=\"' + Number(id) + '\"[^>]*)>[\\s\\S]*?<\\/npc>', 'i');
    const match = xml.match(regex);
    if (!match) throw httpError(404, 'No se encontró el rival ' + id + '.');
    return { xml: xml, whole: match[0], opening: attrs(match[1]) };
  }

  function parsedElement(block, tag) {
    const match = block.match(new RegExp('<' + escapeRegExp(tag) + '\\b([^>]*)>', 'i'));
    return match ? attrs(match[1]) : {};
  }

  function numericAttrs(object) {
    const result = {};
    Object.keys(object).forEach(function (key) { result[key] = numberOrText(object[key]); });
    return result;
  }

  function skillInfo(id, level, role) {
    const cache = skillsCache || buildSkills();
    const found = cache.byId[Number(id)];
    return {
      id: Number(id), level: Number(level), role: role || '',
      name: found ? found.name : ('Skill ' + id),
      icon: found ? found.icon : null,
      iconUrl: iconUrl(found && found.icon, id)
    };
  }

  function parseSkillTags(block, includeRole) {
    const result = [];
    String(block || '').replace(/<skill\s+([^>]*?)\/>/gi, function (_, raw) {
      const a = attrs(raw);
      if (a.id !== undefined) result.push(skillInfo(a.id, a.level || 1, includeRole ? a.name : ''));
      return _;
    });
    return result;
  }

  function opponent(id) {
    const located = locateOpponent(id);
    const block = located.whole;
    const stats = numericAttrs(parsedElement(block, 'stats'));
    const vitals = numericAttrs(parsedElement(block, 'vitals'));
    const attack = numericAttrs(parsedElement(block, 'attack'));
    const defence = numericAttrs(parsedElement(block, 'defence'));
    const fakePlayer = numericAttrs(parsedElement(block, 'fakePlayer'));
    const ai = parsedElement(block, 'ai');
    const parametersBlock = (block.match(/<parameters>([\s\S]*?)<\/parameters>/i) || [null, ''])[1];
    const skillListBlock = (block.match(/<skillList>([\s\S]*?)<\/skillList>/i) || [null, ''])[1];
    const buildParams = {};
    String(parametersBlock).replace(/<param\s+([^>]*?)\/>/gi, function (_, raw) {
      const a = attrs(raw); buildParams[a.name] = a.value; return _;
    });
    const buildIds = [buildParams.LabPrimaryClass, buildParams.LabSub1, buildParams.LabSub2, buildParams.LabSub3].map(function (value) { return value === undefined || value === '' ? null : Number(value); });
    return {
      id: Number(located.opening.id), name: located.opening.name, title: located.opening.title,
      level: Number(located.opening.level), race: getTag(block, 'race'), sex: getTag(block, 'sex'),
      stats: stats, vitals: vitals, attack: attack, defence: defence,
      movement: {
        walk: numberOrText(parsedElement(block, 'walk').ground),
        run: numberOrText(parsedElement(block, 'run').ground),
        hitTime: numberOrText(getTag(block, 'hitTime'))
      },
      appearance: fakePlayer,
      ai: { type: ai.type || '', aggroRange: numberOrText(ai.aggroRange), isAggressive: ai.isAggressive !== 'false' },
      strategy: parseSkillTags(parametersBlock, true),
      skills: parseSkillTags(skillListBlock, false),
      build: {
        primary: buildIds[0] !== null ? classes().byId[buildIds[0]] || null : classes().byId[Number(fakePlayer.classId)] || null,
        subclasses: buildIds.slice(1).map(function (classId) { return classId === null ? null : classes().byId[classId] || null; })
      },
      file: path.relative(serverData, arenaNpcFile)
    };
  }

  function opponents() {
    const xml = arenaXml();
    const ids = [];
    xml.replace(/<npc\s+([^>]*?)>/g, function (_, raw) {
      const a = attrs(raw);
      if (a.id) ids.push(Number(a.id));
      return _;
    });
    return ids.map(function (id) {
      const item = opponent(id);
      return { id: item.id, name: item.name, title: item.title, level: item.level, race: item.race, sex: item.sex, appearance: item.appearance, ai: item.ai, skills: item.skills };
    });
  }

  function validText(value, label, max) {
    const clean = String(value === undefined ? '' : value).trim();
    if (!clean || clean.length > max || /[<>&\"]/g.test(clean)) throw httpError(400, label + ' no es válido.');
    return clean;
  }

  function setNumericGroup(block, tag, payload, fields, max) {
    const source = payload || {};
    fields.forEach(function (field) {
      if (source[field] !== undefined && source[field] !== '') block = updateElementAttr(block, tag, field, validateNumber(source[field], field, 0, max));
    });
    return block;
  }

  function renderSkillList(skills, indent) {
    return skills.map(function (item) {
      const id = validateNumber(item.id, 'Skill ID', 1, 100000);
      const level = validateNumber(item.level, 'Nivel del skill', 1, 10000);
      return indent + '<skill id="' + id + '" level="' + level + '" />';
    }).join('\n');
  }

  function buildClassSkillFileMap() {
    const map = {};
    walk(classSkillRoot, function (file) { return /\.xml$/i.test(file); }).forEach(function (file) {
      const head = fs.readFileSync(file, 'utf8').slice(0, 1200);
      const match = head.match(/<skillTree\s+([^>]*)>/i);
      if (!match) return;
      const a = attrs(match[1]);
      if (a.classId !== undefined) map[Number(a.classId)] = file;
    });
    classSkillFiles = map;
    return map;
  }

  function classLineage(classId) {
    const result = [];
    let item = classes().byId[Number(classId)];
    while (item) {
      result.unshift(item.id);
      item = item.parentId !== null ? classes().byId[item.parentId] : null;
    }
    return result;
  }

  function skillsForBuild(classIds, level) {
    const files = classSkillFiles || buildClassSkillFileMap();
    const lineageIds = [];
    classIds.filter(function (id) { return id !== null && id !== undefined; }).forEach(function (id) {
      classLineage(id).forEach(function (lineageId) { if (lineageIds.indexOf(lineageId) === -1) lineageIds.push(lineageId); });
    });
    const selected = {};
    lineageIds.forEach(function (classId) {
      const file = files[classId];
      if (!file) return;
      const xml = fs.readFileSync(file, 'utf8');
      xml.replace(/<skill\s+([^>]*\bskillId="\d+"[^>]*)>/gi, function (_, raw) {
        const a = attrs(raw);
        const getLevel = Number(a.getLevel || 1);
        const skillId = Number(a.skillId);
        const skillLevel = Number(a.skillLevel || 1);
        if (getLevel <= level && (!selected[skillId] || selected[skillId].level < skillLevel)) selected[skillId] = { id: skillId, level: skillLevel };
        return _;
      });
    });
    return Object.keys(selected).map(function (id) { return selected[id]; }).sort(function (a, b) { return a.id - b.id; });
  }

  function raceCode(race) {
    return { 'Humano': 'HUMAN', 'Elfo': 'ELF', 'Elfo Oscuro': 'DARK_ELF', 'Orco': 'ORC', 'Enano': 'DWARF' }[race] || 'HUMAN';
  }

  function profileStats(profile) {
    if (profile === 'magic') return { pAtk: 280, mAtk: 1850, pDef: 780, mDef: 1150, critical: 45, accuracy: 100, attackSpeed: 350, magicSpeed: 900, hp: 15000, mp: 18000, cp: 10000, walk: 75, run: 165, ai: 'MAGE', attackType: 'BLUNT' };
    if (profile === 'hybrid') return { pAtk: 650, mAtk: 1100, pDef: 900, mDef: 1000, critical: 65, accuracy: 105, attackSpeed: 420, magicSpeed: 650, hp: 17000, mp: 12000, cp: 11000, walk: 80, run: 160, ai: 'MAGE', attackType: 'SWORD' };
    return { pAtk: 850, mAtk: 500, pDef: 1000, mDef: 850, critical: 80, accuracy: 100, attackSpeed: 480, magicSpeed: 333, hp: 18000, mp: 6000, cp: 12000, walk: 80, run: 150, ai: 'FIGHTER', attackType: 'DUAL' };
  }

  function nextOpponentId(xml) {
    const used = {};
    xml.replace(/<npc\s+([^>]*?)>/g, function (_, raw) { const a = attrs(raw); used[Number(a.id)] = true; return _; });
    for (let id = 900202; id <= 900299; id += 1) if (!used[id]) return id;
    throw httpError(409, 'No quedan IDs libres en el rango del laboratorio.');
  }

  function createOpponent(payload) {
    const name = validText(payload.name, 'Nombre', 40);
    const title = validText(payload.title || 'Rival de Laboratorio', 'Título', 60);
    const primaryId = Number(payload.primaryClassId);
    const primary = classes().byId[primaryId];
    if (!primary || primary.stage !== 3) throw httpError(400, 'La clase principal debe ser una tercera profesión.');
    const subclasses = (payload.subclasses || []).slice(0, 3).map(function (value) {
      if (value === null || value === undefined || value === '') return null;
      const found = classes().byId[Number(value)];
      if (!found || found.stage !== 3) throw httpError(400, 'Cada subclase debe ser una tercera profesión.');
      return found.id;
    });
    while (subclasses.length < 3) subclasses.push(null);
    const level = Number(payload.level || 80);
    if (!Number.isInteger(level) || level < 1 || level > 80) throw httpError(400, 'El nivel debe estar entre 1 y 80.');
    const sex = payload.sex === 'FEMALE' ? 'FEMALE' : 'MALE';
    const profileName = ['physical', 'magic', 'hybrid'].indexOf(payload.profile) !== -1 ? payload.profile : 'physical';
    const preset = profileStats(profileName);
    const mainTemplate = template(primaryId);
    const s = mainTemplate.staticStats;
    const npcXml = arenaXml();
    if (opponents().some(function (item) { return item.name.toLowerCase() === name.toLowerCase(); })) throw httpError(409, 'Ya existe un rival con ese nombre.');
    const id = nextOpponentId(npcXml);
    const classIds = [primaryId].concat(subclasses);
    const buildSkills = payload.accumulateSkills === false ? skillsForBuild([primaryId], level) : skillsForBuild(classIds, level);
    const skillLines = renderSkillList(buildSkills, '\t\t\t');
    const buildParams = [
      '\t\t\t<param name="LabPrimaryClass" value="' + primaryId + '" />',
      '\t\t\t<param name="LabSub1" value="' + (subclasses[0] === null ? '' : subclasses[0]) + '" />',
      '\t\t\t<param name="LabSub2" value="' + (subclasses[1] === null ? '' : subclasses[1]) + '" />',
      '\t\t\t<param name="LabSub3" value="' + (subclasses[2] === null ? '' : subclasses[2]) + '" />',
      '\t\t\t<param name="LabProfile" value="' + profileName + '" />'
    ].join('\n');
    const block = '\n\t<!-- Rival generated by Laboratorio L2. -->\n' +
      '\t<npc id="' + id + '" level="' + level + '" type="Monster" name="' + name + '" title="' + title + '">\n' +
      '\t\t<parameters>\n' + buildParams + '\n\t\t</parameters>\n' +
      '\t\t<race>' + raceCode(primary.race) + '</race>\n\t\t<sex>' + sex + '</sex>\n' +
      '\t\t<acquire exp="500000" sp="50000" />\n' +
      '\t\t<stats str="' + s.baseSTR + '" int="' + s.baseINT + '" dex="' + s.baseDEX + '" wit="' + s.baseWIT + '" con="' + s.baseCON + '" men="' + s.baseMEN + '">\n' +
      '\t\t\t<vitals hp="' + preset.hp + '" hpRegen="30" mp="' + preset.mp + '" mpRegen="30" cp="' + preset.cp + '" />\n' +
      '\t\t\t<attack physical="' + preset.pAtk + '" magical="' + preset.mAtk + '" random="10" critical="' + preset.critical + '" accuracy="' + preset.accuracy + '" attackSpeed="' + preset.attackSpeed + '" magicSpeed="' + preset.magicSpeed + '" reuseDelay="800" type="' + preset.attackType + '" range="40" distance="80" width="120" />\n' +
      '\t\t\t<defence physical="' + preset.pDef + '" magical="' + preset.mDef + '" evasion="8" />\n' +
      '\t\t\t<speed><walk ground="' + preset.walk + '" /><run ground="' + preset.run + '" /></speed>\n' +
      '\t\t\t<hitTime>350</hitTime>\n\t\t</stats>\n' +
      '\t\t<status talkable="false" attackable="true" undying="false" canBeSown="false" noSleepMode="true" randomWalk="false" />\n' +
      '\t\t<fakePlayer classId="' + primaryId + '" hair="0" hairColor="0" face="0" nameColor="16777215" titleColor="15530402" equipHead="0" equipRHand="0" equipGloves="0" equipChest="0" equipLegs="0" equipFeet="0" weaponEnchantLevel="0" armorEnchantLevel="0" recommends="255" nobleLevel="1" fakePlayerTalkable="false" />\n' +
      '\t\t<skillList>\n' + skillLines + '\n\t\t</skillList>\n' +
      '\t\t<corpseTime>10</corpseTime><exCrtEffect>true</exCrtEffect>\n' +
      '\t\t<ai type="' + preset.ai + '" aggroRange="450" clanHelpRange="0" isAggressive="true"><clanList><clan>LAB_RIVAL</clan></clanList></ai>\n' +
      '\t\t<collision><radius normal="9" /><height normal="23" /></collision>\n' +
      '\t</npc>\n';
    const updatedNpcXml = npcXml.replace(/\s*<\/list>\s*$/i, block + '</list>\n');
    const backupNpc = backupAndWrite(arenaNpcFile, updatedNpcXml, 'crear-rival-' + id);

    const spawnXml = fs.readFileSync(arenaSpawnFile, 'utf8');
    const index = id - 900202;
    const x = 148000 + ((index % 4) * 600);
    const y = 45400 - (Math.floor(index / 4) * 450);
    const spawnLine = '\n\t\t<npc id="' + id + '" x="' + x + '" y="' + y + '" z="-3400" heading="16384" respawnDelay="60" chaseRange="1500" />';
    const updatedSpawnXml = spawnXml.replace(/\s*<\/spawn>/i, spawnLine + '\n\t</spawn>');
    const backupSpawn = backupAndWrite(arenaSpawnFile, updatedSpawnXml, 'spawn-rival-' + id);
    return { saved: true, id: id, name: name, skillCount: buildSkills.length, backup: backupNpc, spawnBackup: backupSpawn, requiresRestart: true };
  }

  function updateOpponent(id, payload) {
    const located = locateOpponent(id);
    let block = located.whole;
    if (payload.name !== undefined) block = updateElementAttr(block, 'npc', 'name', validText(payload.name, 'Nombre', 40));
    if (payload.title !== undefined) block = updateElementAttr(block, 'npc', 'title', validText(payload.title, 'Título', 60));
    if (payload.level !== undefined) block = updateElementAttr(block, 'npc', 'level', validateNumber(payload.level, 'Nivel', 1, 100));
    if (payload.race !== undefined) {
      const race = String(payload.race);
      if (['HUMAN', 'ELF', 'DARK_ELF', 'ORC', 'DWARF'].indexOf(race) === -1) throw httpError(400, 'Raza no válida.');
      block = replaceTag(block, 'race', race);
    }
    if (payload.sex !== undefined) {
      const sex = String(payload.sex);
      if (['MALE', 'FEMALE'].indexOf(sex) === -1) throw httpError(400, 'Sexo no válido.');
      block = replaceTag(block, 'sex', sex);
    }
    block = setNumericGroup(block, 'stats', payload.stats, ['str', 'int', 'dex', 'wit', 'con', 'men'], 10000);
    block = setNumericGroup(block, 'vitals', payload.vitals, ['hp', 'hpRegen', 'mp', 'mpRegen', 'cp'], 100000000);
    block = setNumericGroup(block, 'attack', payload.attack, ['physical', 'magical', 'random', 'critical', 'accuracy', 'attackSpeed', 'magicSpeed', 'reuseDelay', 'range'], 10000000);
    block = setNumericGroup(block, 'defence', payload.defence, ['physical', 'magical', 'evasion'], 10000000);
    const movement = payload.movement || {};
    if (movement.walk !== undefined) block = updateElementAttr(block, 'walk', 'ground', validateNumber(movement.walk, 'Velocidad caminando', 0, 2000));
    if (movement.run !== undefined) block = updateElementAttr(block, 'run', 'ground', validateNumber(movement.run, 'Velocidad corriendo', 0, 2000));
    if (movement.hitTime !== undefined) block = replaceTag(block, 'hitTime', validateNumber(movement.hitTime, 'Hit time', 0, 100000));
    block = setNumericGroup(block, 'fakePlayer', payload.appearance, ['classId', 'hair', 'hairColor', 'face', 'equipHead', 'equipRHand', 'equipGloves', 'equipChest', 'equipLegs', 'equipFeet', 'weaponEnchantLevel', 'armorEnchantLevel'], 1000000);
    const ai = payload.ai || {};
    if (ai.type !== undefined) {
      const type = validText(ai.type, 'Tipo de IA', 30).toUpperCase();
      block = updateElementAttr(block, 'ai', 'type', type);
    }
    if (ai.aggroRange !== undefined) block = updateElementAttr(block, 'ai', 'aggroRange', validateNumber(ai.aggroRange, 'Rango de agresión', 0, 10000));
    if (ai.isAggressive !== undefined) block = updateElementAttr(block, 'ai', 'isAggressive', ai.isAggressive ? 'true' : 'false');
    if (Array.isArray(payload.skills)) {
      const rendered = renderSkillList(payload.skills, '\t\t\t');
      block = block.replace(/(<skillList>)[\s\S]*?(<\/skillList>)/i, '$1\n' + rendered + '\n\t\t$2');
    }
    if (Array.isArray(payload.strategy)) {
      const byRole = {};
      payload.strategy.forEach(function (item) { byRole[String(item.role)] = item; });
      block = block.replace(/<skill\s+([^>]*\bname="([^"]+)"[^>]*)\/>/gi, function (whole, raw, role) {
        const item = byRole[role];
        if (!item) return whole;
        let updated = whole;
        updated = updateElementAttr(updated, 'skill', 'id', validateNumber(item.id, 'Skill ID de estrategia', 1, 100000));
        updated = updateElementAttr(updated, 'skill', 'level', validateNumber(item.level, 'Nivel de estrategia', 1, 10000));
        return updated;
      });
    }
    const updatedXml = located.xml.replace(located.whole, block);
    const backup = backupAndWrite(arenaNpcFile, updatedXml, 'rival-' + id);
    return { saved: true, backup: backup, requiresRestart: true };
  }

  return {
    classes: function () { return classes().list; },
    classById: function (id) { return classes().byId[Number(id)] || null; },
    template: template,
    playerBaseStats: playerBaseStats,
    updateTemplate: updateTemplate,
    skills: skills,
    skill: skill,
    updateSkill: updateSkill,
    iconUrlForSkill: function (id) {
      const cache = skillsCache || buildSkills();
      const found = cache.byId[Number(id)];
      return iconUrl(found && found.icon, id);
    },
    opponents: opponents,
    opponent: opponent,
    updateOpponent: updateOpponent,
    createOpponent: createOpponent
  };
}

function httpError(status, message) {
  const error = new Error(message);
  error.status = status;
  return error;
}

module.exports = { createDataStore, httpError };
