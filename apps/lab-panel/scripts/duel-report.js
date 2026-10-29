'use strict';

// Read-only report. No inference that a missing effect was resisted or cancelled.
const fs = require('fs');
const path = require('path');
const { createDatabase } = require('../lib/database');
const config = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'config.json'), 'utf8'));
if (process.env.L2_DB_PORT) config.database.port = Number(process.env.L2_DB_PORT);
const db = createDatabase(config.database);

(async () => {
  const argument = process.argv[2];
  if (argument && !/^\d+$/.test(argument)) throw Error('Uso: duel-report.js [run_id]');
  const runs = argument
    ? await db.query('SELECT * FROM lab_ai_runs WHERE run_id=?', [Number(argument)])
    : await db.query("SELECT * FROM lab_ai_runs WHERE test_mode='MANUAL' ORDER BY run_id DESC LIMIT 1");
  if (!runs.length) throw Error('No hay duelo para analizar');
  const run = runs[0];
  const decisions = await db.query('SELECT action_name,reference_id,result_name,COUNT(*) AS count FROM lab_ai_actions WHERE run_id=? GROUP BY action_name,reference_id,result_name ORDER BY count DESC', [run.run_id]);
  const combat = await db.query('SELECT event_type,attacker_name,target_name,skill_id,skill_name,COUNT(*) AS count,SUM(damage) AS damage FROM lab_combat_events WHERE occurred_ms BETWEEN ? AND ? AND (attacker_object_id IN (?,?) OR target_object_id IN (?,?)) GROUP BY event_type,attacker_name,target_name,skill_id,skill_name ORDER BY event_type,damage DESC', [run.started_ms, run.ended_ms || Date.now(), run.controller_id, run.pilot_id, run.controller_id, run.pilot_id]);
  let observations = [], changes = [], observationError = null;
  try {
    observations = await db.query('SELECT actor_id,MAX(actor_name) AS actor_name,owner_id,COUNT(*) AS samples,MIN(hp) AS min_hp,MIN(cp) AS min_cp,MIN(mp) AS min_mp,SUM(is_casting) AS casting_samples FROM lab_duel_observations WHERE run_id=? AND event_name=\'STATE\' GROUP BY actor_id,owner_id', [run.run_id]);
    changes = await db.query("SELECT observed_ms,actor_id,actor_name,event_name,detail_text FROM lab_duel_observations WHERE run_id=? AND event_name<>'STATE' ORDER BY observed_ms,observation_id", [run.run_id]);
  } catch (error) { observationError = error.code || error.message; }
  console.log(JSON.stringify({run,combatSeconds: run.combat_ms && run.ended_ms ? (run.ended_ms-run.combat_ms)/1000 : null,decisions,combat,observations,effectAndActorChanges: changes,observationError,
    limits: ['Observaciones cada 500 ms: pueden perder efectos mas breves o reaplicaciones del mismo efecto.', 'EFFECT_DISAPPEARED no demuestra Cancellation: tambien puede ser expiracion, muerte o retirada.', 'Sin evento exacto del motor, ausencia de efecto no demuestra resistencia.', 'Los duelos anteriores a esta version no tienen observaciones retroactivas.', 'La seleccion de combate por participantes no incluye todos los eventos summon contra summon.', 'Colas/errores SQL pueden dejar evidencia incompleta; revisar log.']}, null, 2));
})().catch(error => {console.error(error.message);process.exitCode=1;}).finally(() => db.pool.end());
