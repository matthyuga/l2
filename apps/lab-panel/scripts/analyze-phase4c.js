'use strict';

const fs = require('fs');
const path = require('path');
const mysql = require('mysql2/promise');
const { createDataStore } = require('../lib/data');

const PANEL_ROOT = path.resolve(__dirname, '..');
const PROJECT_ROOT = path.resolve(PANEL_ROOT, '..');
const config = JSON.parse(fs.readFileSync(path.join(PANEL_ROOT, 'config.json'), 'utf8'));
config.paths.serverData = path.join(PROJECT_ROOT, 'server', 'game', 'data');
config.paths.sourceData = path.join(PROJECT_ROOT, 'source', 'L2J_Mobius_CT_0_Interlude', 'dist', 'game', 'data');
config.paths.backupRoot = path.join(PROJECT_ROOT, 'backups', 'lab-panel');
const data = createDataStore(config);

const PHYSICAL = new Set([88,89,92,93,101,102,107,108,109,113,114,117,118]);
const MAGIC_DAMAGE = new Set([94,95,103,110]);
const TANK = new Set([90,91,99,106]);
const SUPPORT = new Set([97,98,100,105,107,112,115,116]);
const SUMMONER = new Set([96,104,111]);
const CATEGORY_ORDER = ['física','mágica','tanque','soporte','summoner','híbrida'];
const EXPECTED_BUILDS = 155;
const EXPECTED_STATES = 620;
const EXPECTED_FINALISTS = 30;

function keyOf(row) {
  return [row.main_class_id,row.sub1_class_id,row.sub2_class_id,row.sub3_class_id].map(Number).join(':');
}

function idsOf(build) {
  return [build.mainId,build.sub1,build.sub2,build.sub3];
}

function groupKey(build) {
  return idsOf(build).slice().sort(function (a,b) { return a-b; }).join(':');
}

function mean(values) {
  return values.reduce(function (sum,value) { return sum+value; },0) / Math.max(1,values.length);
}

function logRatio(actual, baseline) {
  return Math.log(Math.max(Number(actual),0.000001) / Math.max(Number(baseline),0.000001));
}

function geometricPercent(logValues) {
  return (Math.exp(mean(logValues))-1)*100;
}

function zStats(builds, field) {
  const values=builds.map(function (build) { return Number(build[field]); });
  const average=mean(values);
  const deviation=Math.sqrt(mean(values.map(function (value) { return Math.pow(value-average,2); }))) || 1;
  builds.forEach(function (build) { build['z_'+field]=(Number(build[field])-average)/deviation; });
}

function countRole(ids, role) {
  return ids.filter(function (id) { return role.has(id); }).length;
}

function eligible(build, category) {
  if (category==='física') return build.physicalClasses>=2 && build.mageCount<=1;
  if (category==='mágica') return build.magicDamageClasses>=2 && build.mageCount>=2;
  if (category==='tanque') return build.tankClasses>=1;
  if (category==='soporte') return build.supportClasses>=1;
  if (category==='summoner') return build.summonerClasses>=1;
  return build.mageCount>=1 && build.mageCount<=3 && build.physicalClasses>=1 && (build.magicDamageClasses+build.supportClasses+build.summonerClasses)>=1;
}

function scoreField(category) {
  return {
    'física':'physicalScore','mágica':'magicalScore','tanque':'tankScore',
    'soporte':'supportScore','summoner':'summonerScore','híbrida':'hybridScore'
  }[category];
}

function choose(pool, usedGroups, mainCounts, compare, relaxMain) {
  const available=pool.filter(function (build) {
    return !usedGroups.has(build.groupKey) && (relaxMain || (mainCounts.get(build.mainId)||0)<2);
  }).sort(compare);
  if (available.length) return available[0];
  if (!relaxMain) return choose(pool,usedGroups,mainCounts,compare,true);
  throw new Error('No quedan candidatos diversos para la categoría.');
}

function reasonFor(category,type,build,missingCovered) {
  const label={
    'física':'potencial físico','mágica':'potencial mágico','tanque':'durabilidad',
    'soporte':'herramientas de soporte','summoner':'base para pruebas con invocación','híbrida':'equilibrio híbrido'
  }[category];
  if (type==='rendimiento') return 'Índice alto de '+label+' con stats reales y cuatro ranuras validadas.';
  if (type==='amplitud') return 'Mayor amplitud útil disponible en '+category+': '+build.skillCount+' skills.';
  if (type==='estrés') return 'Caso de estrés por solapamiento: '+build.overlap+' puntos y '+build.mastery+' colisiones pareadas.';
  return 'Control de contraste; añade cobertura de '+missingCovered+' clases poco representadas y conserva puntuación baja/media.';
}

async function main() {
  const connection=await mysql.createConnection(Object.assign({},config.database,{charset:'utf8mb4',decimalNumbers:true}));
  try {
    const candidateRows=(await connection.query(
      'SELECT main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,skill_count,passive_skill_count,active_skill_count,'+
      'pair_shared_score,mastery_collision_score,mage_class_count,summoner_class_count,race_count,composition,skill_hash,selection_bucket '+
      'FROM lab_four_class_candidates WHERE selected=1'
    ))[0];
    const profileRows=(await connection.query('SELECT * FROM lab_four_class_profiles ORDER BY main_class_id,sub1_class_id,sub2_class_id,sub3_class_id,active_class_index'))[0];
    const cleanRows=(await connection.query(
      "SELECT p.* FROM lab_player_stat_profiles p JOIN characters c ON c.charId=p.char_id WHERE c.account_name IN ('telemetryf','telemetrym') "+
      'AND p.level=80 AND p.base_class_id=p.class_id AND p.class_index=0 AND p.sub1_class_id=-1 AND p.sub2_class_id=-1 AND p.sub3_class_id=-1 '+
      'AND p.equipped_count=0 AND p.effect_count=0'
    ))[0];
    if (candidateRows.length!==EXPECTED_BUILDS || profileRows.length!==EXPECTED_STATES) {
      throw new Error('Fase 4B incompleta: candidatos='+candidateRows.length+', estados='+profileRows.length+'.');
    }

    const clean=new Map(cleanRows.map(function (row) { return [Number(row.class_id),row]; }));
    const profiles=new Map();
    profileRows.forEach(function (row) {
      const key=keyOf(row);
      if (!profiles.has(key)) profiles.set(key,[]);
      profiles.get(key).push(row);
    });
    const classes=new Map(data.classes().map(function (item) { return [item.id,item]; }));
    const builds=candidateRows.map(function (row) {
      const key=keyOf(row);
      const states=profiles.get(key)||[];
      if (states.length!==4) throw new Error('La build '+key+' no posee cuatro estados.');
      const ids=[Number(row.main_class_id),Number(row.sub1_class_id),Number(row.sub2_class_id),Number(row.sub3_class_id)];
      const logs={pAtk:[],mAtk:[],pDef:[],mDef:[],hp:[],cp:[],mp:[],atkSpeed:[],castSpeed:[],pCritical:[],mCritical:[],evasion:[],run:[]};
      states.forEach(function (state) {
        const base=clean.get(Number(state.active_class_id));
        if (!base) throw new Error('Falta perfil limpio para clase '+state.active_class_id+'.');
        logs.pAtk.push(logRatio(state.p_atk,base.p_atk)); logs.mAtk.push(logRatio(state.m_atk,base.m_atk));
        logs.pDef.push(logRatio(state.p_def,base.p_def)); logs.mDef.push(logRatio(state.m_def,base.m_def));
        logs.hp.push(logRatio(state.max_hp,base.max_hp)); logs.cp.push(logRatio(state.max_cp,base.max_cp)); logs.mp.push(logRatio(state.max_mp,base.max_mp));
        logs.atkSpeed.push(logRatio(state.p_atk_speed,base.p_atk_speed)); logs.castSpeed.push(logRatio(state.m_atk_speed,base.m_atk_speed));
        logs.pCritical.push(logRatio(state.p_critical,base.p_critical)); logs.mCritical.push(logRatio(state.m_critical,base.m_critical));
        logs.evasion.push(logRatio(Math.max(1,state.evasion),Math.max(1,base.evasion))); logs.run.push(logRatio(state.run_speed,base.run_speed));
      });
      const build={
        key:key,mainId:ids[0],sub1:ids[1],sub2:ids[2],sub3:ids[3],groupKey:ids.slice().sort(function(a,b){return a-b;}).join(':'),
        skillCount:Number(row.skill_count),passiveCount:Number(row.passive_skill_count),activeCount:Number(row.active_skill_count),
        overlap:Number(row.pair_shared_score),mastery:Number(row.mastery_collision_score),mageCount:Number(row.mage_class_count),
        summonerCount:Number(row.summoner_class_count),raceCount:Number(row.race_count),composition:row.composition,skillHash:row.skill_hash,phase4aBucket:row.selection_bucket,
        physicalClasses:countRole(ids,PHYSICAL),magicDamageClasses:countRole(ids,MAGIC_DAMAGE),tankClasses:countRole(ids,TANK),
        supportClasses:countRole(ids,SUPPORT),summonerClasses:countRole(ids,SUMMONER),
        pAtkGain:geometricPercent(logs.pAtk),mAtkGain:geometricPercent(logs.mAtk),pDefGain:geometricPercent(logs.pDef),mDefGain:geometricPercent(logs.mDef),
        hpGain:geometricPercent(logs.hp),cpGain:geometricPercent(logs.cp),mpGain:geometricPercent(logs.mp),
        atkSpeedGain:geometricPercent(logs.atkSpeed),castSpeedGain:geometricPercent(logs.castSpeed),
        pCriticalGain:geometricPercent(logs.pCritical),mCriticalGain:geometricPercent(logs.mCritical),evasionGain:geometricPercent(logs.evasion),runGain:geometricPercent(logs.run)
      };
      build.physicalRaw=1.2*mean(logs.pAtk)+0.7*mean(logs.atkSpeed)+0.3*mean(logs.pCritical)+0.15*mean(logs.run);
      build.magicalRaw=1.2*mean(logs.mAtk)+0.7*mean(logs.castSpeed)+0.3*mean(logs.mCritical)+0.15*mean(logs.mp);
      build.tankRaw=0.7*mean(logs.hp)+0.5*mean(logs.cp)+0.8*mean(logs.pDef)+0.8*mean(logs.mDef)+0.25*mean(logs.evasion);
      build.supportRaw=0.7*mean(logs.mp)+0.6*mean(logs.castSpeed)+0.25*mean(logs.mDef);
      return build;
    });

    ['physicalRaw','magicalRaw','tankRaw','supportRaw','skillCount','activeCount','passiveCount','overlap','mastery','raceCount'].forEach(function (field) { zStats(builds,field); });
    builds.forEach(function (build) {
      build.physicalScore=build.z_physicalRaw+0.25*build.z_activeCount+0.15*build.z_skillCount-0.10*build.z_mastery;
      build.magicalScore=build.z_magicalRaw+0.25*build.z_activeCount+0.15*build.z_skillCount-0.10*build.z_mastery;
      build.tankScore=build.z_tankRaw+0.15*build.z_passiveCount+0.10*build.z_skillCount;
      build.supportScore=0.55*build.z_supportRaw+0.70*build.z_activeCount+0.25*build.z_skillCount-0.10*build.z_overlap;
      build.summonerScore=0.45*build.z_magicalRaw+0.35*build.z_tankRaw+0.25*build.z_supportRaw+0.20*build.z_skillCount;
      build.hybridScore=0.35*build.z_physicalRaw+0.35*build.z_magicalRaw+0.20*build.z_tankRaw+0.10*build.z_supportRaw+0.20*build.z_raceCount-0.10*build.z_mastery;
    });

    const selected=[];
    const usedGroups=new Set();
    const mainCounts=new Map();
    const appearances=new Map();
    function add(build,category,type,missingCovered) {
      selected.push({build:build,category:category,type:type,reason:reasonFor(category,type,build,missingCovered||0)});
      usedGroups.add(build.groupKey);
      mainCounts.set(build.mainId,(mainCounts.get(build.mainId)||0)+1);
      idsOf(build).forEach(function(id){appearances.set(id,(appearances.get(id)||0)+1);});
    }

    CATEGORY_ORDER.forEach(function (category) {
      const pool=builds.filter(function (build) { return eligible(build,category); });
      const score=scoreField(category);
      for (let index=0;index<2;index+=1) {
        add(choose(pool,usedGroups,mainCounts,function(a,b){return b[score]-a[score]||b.skillCount-a.skillCount||a.key.localeCompare(b.key);},false),category,'rendimiento');
      }
      add(choose(pool,usedGroups,mainCounts,function(a,b){return b.skillCount-a.skillCount||b[score]-a[score]||a.key.localeCompare(b.key);},false),category,'amplitud');
      add(choose(pool,usedGroups,mainCounts,function(a,b){return b.mastery-a.mastery||b.overlap-a.overlap||a.key.localeCompare(b.key);},false),category,'estrés');
    });

    CATEGORY_ORDER.forEach(function (category) {
      const pool=builds.filter(function (build) { return eligible(build,category); });
      const score=scoreField(category);
      const candidate=choose(pool,usedGroups,mainCounts,function(a,b){
        const aMissing=idsOf(a).filter(function(id){return !appearances.has(id);}).length;
        const bMissing=idsOf(b).filter(function(id){return !appearances.has(id);}).length;
        const aRarity=idsOf(a).reduce(function(sum,id){return sum+1/((appearances.get(id)||0)+1);},0);
        const bRarity=idsOf(b).reduce(function(sum,id){return sum+1/((appearances.get(id)||0)+1);},0);
        return bMissing-aMissing||bRarity-aRarity||a[score]-b[score]||a.key.localeCompare(b.key);
      },false);
      const missingCovered=idsOf(candidate).filter(function(id){return !appearances.has(id);}).length;
      add(candidate,category,'control',missingCovered);
    });

    if (selected.length!==EXPECTED_FINALISTS) throw new Error('Se esperaban 30 finalistas y se eligieron '+selected.length+'.');
    const generatedMs=Date.now();
    await connection.query('DROP TABLE IF EXISTS lab_build_finalists_stage');
    await connection.query(
      "CREATE TABLE lab_build_finalists_stage ("+
      "main_class_id INT NOT NULL,sub1_class_id INT NOT NULL,sub2_class_id INT NOT NULL,sub3_class_id INT NOT NULL,"+
      "category VARCHAR(16) NOT NULL,finalist_type VARCHAR(16) NOT NULL,finalist_rank SMALLINT NOT NULL,reason VARCHAR(255) NOT NULL,"+
      "generated_ms BIGINT UNSIGNED NOT NULL,skill_count SMALLINT NOT NULL,passive_skill_count SMALLINT NOT NULL,active_skill_count SMALLINT NOT NULL,"+
      "pair_shared_score SMALLINT NOT NULL,mastery_collision_score SMALLINT NOT NULL,skill_hash CHAR(64) NOT NULL,"+
      "physical_score DOUBLE NOT NULL,magical_score DOUBLE NOT NULL,tank_score DOUBLE NOT NULL,support_score DOUBLE NOT NULL,summoner_score DOUBLE NOT NULL,hybrid_score DOUBLE NOT NULL,"+
      "p_atk_gain_pct DOUBLE NOT NULL,m_atk_gain_pct DOUBLE NOT NULL,p_def_gain_pct DOUBLE NOT NULL,m_def_gain_pct DOUBLE NOT NULL,"+
      "hp_gain_pct DOUBLE NOT NULL,cp_gain_pct DOUBLE NOT NULL,mp_gain_pct DOUBLE NOT NULL,p_atk_speed_gain_pct DOUBLE NOT NULL,m_atk_speed_gain_pct DOUBLE NOT NULL,"+
      "p_critical_gain_pct DOUBLE NOT NULL,m_critical_gain_pct DOUBLE NOT NULL,evasion_gain_pct DOUBLE NOT NULL,run_gain_pct DOUBLE NOT NULL,"+
      "PRIMARY KEY(main_class_id,sub1_class_id,sub2_class_id,sub3_class_id),KEY idx_lab_finalist_category(category,finalist_type),KEY idx_lab_finalist_rank(finalist_rank)"+
      ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
    );
    const values=selected.map(function(item,index){
      const b=item.build;
      return [b.mainId,b.sub1,b.sub2,b.sub3,item.category,item.type,index+1,item.reason,generatedMs,b.skillCount,b.passiveCount,b.activeCount,b.overlap,b.mastery,b.skillHash,
        b.physicalScore,b.magicalScore,b.tankScore,b.supportScore,b.summonerScore,b.hybridScore,b.pAtkGain,b.mAtkGain,b.pDefGain,b.mDefGain,b.hpGain,b.cpGain,b.mpGain,
        b.atkSpeedGain,b.castSpeedGain,b.pCriticalGain,b.mCriticalGain,b.evasionGain,b.runGain];
    });
    await connection.query('INSERT INTO lab_build_finalists_stage VALUES ?', [values]);
    const existing=(await connection.query("SHOW TABLES LIKE 'lab_build_finalists'"))[0];
    if (existing.length) {
      await connection.query('DROP TABLE IF EXISTS lab_build_finalists_old');
      await connection.query('RENAME TABLE lab_build_finalists TO lab_build_finalists_old,lab_build_finalists_stage TO lab_build_finalists');
      await connection.query('DROP TABLE lab_build_finalists_old');
    } else {
      await connection.query('RENAME TABLE lab_build_finalists_stage TO lab_build_finalists');
    }

    const covered=new Set(); selected.forEach(function(item){idsOf(item.build).forEach(function(id){covered.add(id);});});
    const principals=new Set(selected.map(function(item){return item.build.mainId;}));
    const categoryCounts={}; selected.forEach(function(item){categoryCounts[item.category]=(categoryCounts[item.category]||0)+1;});
    process.stdout.write('FASE 4C COMPLETA '+JSON.stringify({finalists:selected.length,categories:categoryCounts,classesCovered:covered.size,principals:principals.size,groups:new Set(selected.map(function(item){return item.build.groupKey;})).size})+'\n');
    selected.forEach(function(item,index){
      const names=idsOf(item.build).map(function(id){return classes.get(id).name;});
      process.stdout.write(String(index+1).padStart(2,'0')+' '+item.category+'/'+item.type+' '+names.join(' + ')+'\n');
    });
  } finally {
    await connection.end();
  }
}

main().catch(function(error){console.error(error&&error.stack?error.stack:error);process.exitCode=1;});
