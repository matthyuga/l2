'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const mysql = require('mysql2/promise');
const { createDataStore } = require('../lib/data');

const PANEL_ROOT = path.resolve(__dirname, '..');
const PROJECT_ROOT = path.resolve(PANEL_ROOT, '..');
const config = JSON.parse(fs.readFileSync(path.join(PANEL_ROOT, 'config.json'), 'utf8'));
config.paths.serverData = path.join(PROJECT_ROOT, 'server', 'game', 'data');
config.paths.sourceData = path.join(PROJECT_ROOT, 'source', 'L2J_Mobius_CT_0_Interlude', 'dist', 'game', 'data');
config.paths.backupRoot = path.join(PROJECT_ROOT, 'backups', 'lab-panel');
const data = createDataStore(config);

const SUPPORT = new Set([97,98,100,105,107,112,115,116]);
const SUMMONER = new Set([96,104,111]);
const ROBE = new Set([94,95,96,97,98,103,104,105,110,111,112,115,116]);
const LIGHT = new Set([92,93,101,102,108,109,114]);
const WEAPONS = new Map([
  [88,[6580,"Tallum Blade*Dark Legion's Edge"]],[89,[6370,'Saint Spear']],[90,[6364,'Forgotten Blade']],[91,[6364,'Forgotten Blade']],
  [92,[7575,'Draconic Bow']],[93,[6367,'Angel Slayer']],[94,[6579,'Arcana Mace']],[95,[6579,'Arcana Mace']],[96,[6579,'Arcana Mace']],
  [97,[6579,'Arcana Mace']],[98,[6579,'Arcana Mace']],[99,[6364,'Forgotten Blade']],[100,[6364,'Forgotten Blade']],[101,[6367,'Angel Slayer']],
  [102,[7575,'Draconic Bow']],[103,[6579,'Arcana Mace']],[104,[6579,'Arcana Mace']],[105,[6579,'Arcana Mace']],[106,[6364,'Forgotten Blade']],
  [107,[6580,"Tallum Blade*Dark Legion's Edge"]],[108,[6367,'Angel Slayer']],[109,[7575,'Draconic Bow']],[110,[6579,'Arcana Mace']],
  [111,[6579,'Arcana Mace']],[112,[6579,'Arcana Mace']],[113,[6372,"Heaven's Divider"]],[114,[6371,'Demon Splinter']],
  [115,[6579,'Arcana Mace']],[116,[6579,'Arcana Mace']],[117,[6365,'Basalt Battlehammer']],[118,[6365,'Basalt Battlehammer']]
]);
const EXPECTED_FINALISTS = 30;
const EXPECTED_CASES = 95;
const REPETITIONS = 3;

function buildKey(row) {
  return [row.main_class_id,row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number).join(':');
}

function classIds(row) {
  return [row.main_class_id,row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number);
}

function productLog() {
  return Array.prototype.slice.call(arguments).reduce(function (sum,value) {
    return sum + Math.log(Math.max(Number(value),0.000001));
  },0);
}

function physicalScore(state) {
  return productLog(state.p_atk,state.p_atk_speed,1+(Number(state.p_critical)/1000));
}

function magicalScore(state) {
  return productLog(state.m_atk,state.m_atk_speed,1+(Number(state.m_critical)/1000));
}

function physicalSurvivalScore(state) {
  return productLog(Number(state.max_hp)+Number(state.max_cp),state.p_def);
}

function magicalSurvivalScore(state) {
  return productLog(Number(state.max_hp)+Number(state.max_cp),state.m_def);
}

function supportScore(state) {
  return productLog(state.max_mp,state.m_atk_speed,Math.sqrt(Math.max(Number(state.m_atk),1)));
}

function bestState(states, scorer, allowed) {
  const filtered=allowed ? states.filter(function (state) { return allowed.has(Number(state.active_class_id)); }) : states;
  const pool=filtered.length ? filtered : states;
  return pool.slice().sort(function (a,b) {
    return scorer(b)-scorer(a) || Number(a.active_class_index)-Number(b.active_class_index);
  })[0];
}

function equipmentFor(classId) {
  const id=Number(classId);
  const weapon=WEAPONS.get(id);
  if (!weapon) throw new Error('No hay arma normalizada para la clase '+id+'.');
  return {kit:ROBE.has(id)?'S_ROBE':(LIGHT.has(id)?'S_LIGHT':'S_HEAVY'),weaponId:weapon[0],weaponName:weapon[1]};
}

function protocols(category, states) {
  const physical=bestState(states,physicalScore);
  const magical=bestState(states,magicalScore);
  const versusAres=bestState(states,physicalSurvivalScore);
  const versusNyx=bestState(states,magicalSurvivalScore);
  const support=bestState(states,supportScore,SUPPORT);
  const summon=bestState(states,magicalScore,SUMMONER);
  const common={
    salida_fisica:{state:physical,opponentId:900202,opponent:'Atlas',seconds:60,metrics:'damage_total,dps,hits,critical_rate,mp_used',reason:'Mayor salida física estimada entre las cuatro clases activas.'},
    salida_magica:{state:magical,opponentId:900202,opponent:'Atlas',seconds:60,metrics:'damage_total,dps,casts,magic_critical_rate,mp_used',reason:'Mayor salida mágica estimada entre las cuatro clases activas.'},
    resistencia_ares:{state:versusAres,opponentId:900200,opponent:'Ares',seconds:45,metrics:'time_alive,damage_received,hp_cp_remaining,control_time',reason:'Mayor resistencia física estimada frente a Ares.'},
    resistencia_nyx:{state:versusNyx,opponentId:900201,opponent:'Nyx',seconds:45,metrics:'time_alive,damage_received,hp_cp_remaining,control_time',reason:'Mayor resistencia mágica estimada frente a Nyx.'},
    soporte_sostenido:{state:support,opponentId:0,opponent:'Aliado controlado',seconds:60,metrics:'effective_heal,hps,mp_efficiency,overheal',reason:'Clase de soporte de la build con mejor capacidad sostenida estimada.'},
    salida_invocacion:{state:summon,opponentId:900202,opponent:'Atlas',seconds:60,metrics:'owner_damage,summon_damage,total_dps,summon_uptime,mp_used',reason:'Profesión invocadora activa para separar daño del dueño y de la invocación.'}
  };
  const names={
    'física':['salida_fisica','resistencia_ares','resistencia_nyx'],
    'mágica':['salida_magica','resistencia_ares','resistencia_nyx'],
    'tanque':['resistencia_ares','resistencia_nyx','salida_fisica'],
    'soporte':['soporte_sostenido','resistencia_ares','resistencia_nyx'],
    'summoner':['salida_invocacion','resistencia_ares','resistencia_nyx'],
    'híbrida':['salida_fisica','salida_magica','resistencia_ares','resistencia_nyx']
  }[category];
  if (!names) throw new Error('Categoría 4C desconocida: '+category);
  return names.map(function (name,index) {
    return Object.assign({code:name,priority:index+1},common[name]);
  });
}

async function main() {
  const connection=await mysql.createConnection(Object.assign({},config.database,{charset:'utf8mb4',decimalNumbers:true}));
  try {
    const finalists=(await connection.query('SELECT * FROM lab_build_finalists ORDER BY finalist_rank'))[0];
    if (finalists.length!==EXPECTED_FINALISTS) throw new Error('Se esperaban 30 finalistas y se encontraron '+finalists.length+'.');
    const profiles=(await connection.query('SELECT * FROM lab_four_class_profiles WHERE level=80 AND equipped_count=0 AND effect_count=0 ORDER BY active_class_index'))[0];
    const profileMap=new Map();
    profiles.forEach(function (row) {
      const key=buildKey(row);
      if (!profileMap.has(key)) profileMap.set(key,[]);
      profileMap.get(key).push(row);
    });
    const classes=new Map(data.classes().map(function (item) { return [Number(item.id),item]; }));
    const now=Date.now();
    const cases=[];
    finalists.forEach(function (finalist) {
      const states=profileMap.get(buildKey(finalist))||[];
      if (states.length!==4) throw new Error('El finalista '+finalist.finalist_rank+' no tiene cuatro estados reales.');
      protocols(finalist.category,states).forEach(function (protocol) {
        const activeId=Number(protocol.state.active_class_id);
        const active=classes.get(activeId);
        const equipment=equipmentFor(activeId);
        cases.push({
          caseId:String(finalist.finalist_rank).padStart(2,'0')+'-'+protocol.code,
          rank:Number(finalist.finalist_rank),category:finalist.category,type:finalist.finalist_type,
          ids:classIds(finalist),activeId:activeId,activeIndex:Number(protocol.state.active_class_index),
          activeName:active ? active.name : ('Clase '+activeId),code:protocol.code,priority:protocol.priority,
          opponentId:protocol.opponentId,opponent:protocol.opponent,kit:equipment.kit,weaponId:equipment.weaponId,weaponName:equipment.weaponName,buffs:'SIN_BUFFS_EXTERNOS',
          seconds:protocol.seconds,repetitions:REPETITIONS,metrics:protocol.metrics,reason:protocol.reason,created:now
        });
      });
    });
    if (cases.length!==EXPECTED_CASES) throw new Error('Se esperaban 95 casos y se generaron '+cases.length+'.');

    await connection.query(
      "CREATE TABLE IF NOT EXISTS lab_combat_benchmark_plan ("+
      "case_id VARCHAR(48) NOT NULL,finalist_rank SMALLINT NOT NULL,category VARCHAR(16) NOT NULL,finalist_type VARCHAR(16) NOT NULL,"+
      "main_class_id INT NOT NULL,sub1_class_id INT NOT NULL,sub2_class_id INT NOT NULL,sub3_class_id INT NOT NULL,"+
      "active_class_id INT NOT NULL,active_class_index SMALLINT NOT NULL,active_class_name VARCHAR(45) NOT NULL,"+
      "benchmark_code VARCHAR(32) NOT NULL,priority SMALLINT NOT NULL,opponent_id INT NOT NULL,opponent_name VARCHAR(45) NOT NULL,"+
      "equipment_kit VARCHAR(32) NOT NULL,weapon_id INT NOT NULL,weapon_name VARCHAR(80) NOT NULL,buff_kit VARCHAR(32) NOT NULL,duration_seconds SMALLINT NOT NULL,repetitions SMALLINT NOT NULL,"+
      "metrics VARCHAR(255) NOT NULL,selection_reason VARCHAR(255) NOT NULL,status VARCHAR(16) NOT NULL DEFAULT 'PENDING',completed_runs SMALLINT NOT NULL DEFAULT 0,created_ms BIGINT UNSIGNED NOT NULL,"+
      "PRIMARY KEY(case_id),KEY idx_lab_benchmark_rank(finalist_rank,priority),KEY idx_lab_benchmark_status(status),KEY idx_lab_benchmark_code(benchmark_code)"+
      ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
    await connection.query("ALTER TABLE lab_combat_benchmark_plan ADD COLUMN IF NOT EXISTS weapon_id INT NOT NULL DEFAULT 0 AFTER equipment_kit, ADD COLUMN IF NOT EXISTS weapon_name VARCHAR(80) NOT NULL DEFAULT '' AFTER weapon_id");
    const active=(await connection.query("SELECT COUNT(*) n FROM lab_combat_benchmark_plan WHERE status<>'PENDING' OR completed_runs>0"))[0][0].n;
    if (Number(active)===0) await connection.query('TRUNCATE TABLE lab_combat_benchmark_plan');
    const sql="INSERT INTO lab_combat_benchmark_plan (case_id,finalist_rank,category,finalist_type,main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,active_class_id,active_class_index,active_class_name,benchmark_code,priority,opponent_id,opponent_name,equipment_kit,weapon_id,weapon_name,buff_kit,duration_seconds,repetitions,metrics,selection_reason,status,completed_runs,created_ms) VALUES ? "+
      "ON DUPLICATE KEY UPDATE finalist_rank=VALUES(finalist_rank),category=VALUES(category),finalist_type=VALUES(finalist_type),main_class_id=VALUES(main_class_id),sub1_class_id=VALUES(sub1_class_id),sub2_class_id=VALUES(sub2_class_id),sub3_class_id=VALUES(sub3_class_id),active_class_id=VALUES(active_class_id),active_class_index=VALUES(active_class_index),active_class_name=VALUES(active_class_name),benchmark_code=VALUES(benchmark_code),priority=VALUES(priority),opponent_id=VALUES(opponent_id),opponent_name=VALUES(opponent_name),equipment_kit=VALUES(equipment_kit),weapon_id=VALUES(weapon_id),weapon_name=VALUES(weapon_name),buff_kit=VALUES(buff_kit),duration_seconds=VALUES(duration_seconds),repetitions=VALUES(repetitions),metrics=VALUES(metrics),selection_reason=VALUES(selection_reason),created_ms=VALUES(created_ms)";
    const values=cases.map(function (item) {
      return [item.caseId,item.rank,item.category,item.type,item.ids[0],item.ids[1],item.ids[2],item.ids[3],item.activeId,item.activeIndex,item.activeName,item.code,item.priority,item.opponentId,item.opponent,item.kit,item.weaponId,item.weaponName,item.buffs,item.seconds,item.repetitions,item.metrics,item.reason,'PENDING',0,item.created];
    });
    await connection.query(sql,[values]);
    const rows=(await connection.query('SELECT case_id,finalist_rank,category,benchmark_code,active_class_id,opponent_id,equipment_kit,weapon_id,buff_kit,duration_seconds,repetitions FROM lab_combat_benchmark_plan ORDER BY finalist_rank,priority'))[0];
    const signature=crypto.createHash('sha256').update(rows.map(function (row) { return Object.values(row).join('|'); }).join('\n')).digest('hex');
    const byCode={};
    rows.forEach(function (row) { byCode[row.benchmark_code]=(byCode[row.benchmark_code]||0)+1; });
    process.stdout.write('FASE 4D PREPARADA '+JSON.stringify({finalists:EXPECTED_FINALISTS,cases:rows.length,plannedRuns:rows.reduce(function (sum,row) { return sum+Number(row.repetitions); },0),byCode:byCode,signature:signature})+'\n');
  } finally {
    await connection.end();
  }
}

main().catch(function (error) {
  process.stderr.write((error&&error.stack)||String(error));
  process.stderr.write('\n');
  process.exitCode=1;
});
