const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const cp = require('child_process');

const root = path.resolve(__dirname, '../..');
const client = path.join(path.dirname(root), 'l2');
const dateParts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Argentina/Buenos_Aires', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date());
const date = ['year', 'month', 'day'].map(type => dateParts.find(part => part.type === type).value).join('-');
const backup = path.join(root, 'backups', `retorno-w10-${date}`);
const handoff = path.join(root, 'CONTINUIDAD-W10');
const config = JSON.parse(fs.readFileSync(path.join(root, 'lab-panel/config.json'), 'utf8')).database;
fs.mkdirSync(backup, { recursive: true });
fs.mkdirSync(handoff, { recursive: true });
const defaults = path.join(backup, 'dump-private.cnf');
const sql = path.join(backup, `l2jmobiusinterlude-${date}.sql`);
if (fs.existsSync(sql)) throw new Error('An SQL snapshot already exists; keep it and choose a separate backup directory.');
const quote = value => '"' + String(value).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\r/g, '\\r').replace(/\n/g, '\\n') + '"';
try {
  fs.writeFileSync(defaults, '[client]\n' + ['host', 'port', 'user', 'password'].map(key => `${key}=${quote(config[key])}`).join('\n') + '\n');
  const dump = cp.spawnSync(path.join(root, 'tools/mariadb-11.8.9-winx64/bin/mariadb-dump.exe'), [
    `--defaults-extra-file=${defaults}`, '--single-transaction', '--quick', '--skip-lock-tables',
    '--routines', '--events', '--hex-blob', '--default-character-set=utf8mb4',
    `--result-file=${sql}`, config.database,
  ], { windowsHide: true, encoding: 'utf8', timeout: 180000, maxBuffer: 1024 * 1024 });
  if (dump.error || dump.status !== 0) {
    if (fs.existsSync(sql)) fs.renameSync(sql, sql + '.incomplete');
    throw new Error('SQL export failed: ' + ((dump.error && dump.error.message) || dump.stderr));
  }
} finally {
  if (fs.existsSync(defaults)) fs.unlinkSync(defaults);
}
const files = [
  'server/libs/GameServer.jar', 'Start-L2Local.ps1', 'Stop-L2Local.ps1', '2-JUGAR.cmd',
  '5-DETENER-SERVIDOR.cmd', 'server/game/data/spawns/Others/SoloArena.xml',
  'server/game/data/stats/npcs/custom/amber_summon.xml',
  'server/game/data/stats/skills/custom/amber_contract.xml', 'server/game/data/PetSkillData.xml',
  'server/game/data/scripts/handlers/EffectMasterHandler.java',
  'server/game/data/scripts/handlers/items/BeastSoulShot.java',
  'server/game/data/scripts/handlers/skill/effects/AmberFireBuff.java',
  'server/game/data/scripts/handlers/skill/effects/AmberOrder.java',
  'server/game/data/scripts/custom/NormalNpcRoster/NormalNpcRoster.java',
  'server/game/data/scripts/custom/SoloArenaGauntlet/SoloArenaGauntlet.java',
  'reports/amber-combat-vfx-verification.json', 'reports/amber-native-controls-verification.json',
  'research/amber-l2/Install-AmberCombatVfx.ps1',
  'research/amber-l2/scripts/build_amber_vfx_v2.js',
  'research/amber-l2/scripts/build_amber_combat_catalogs.groovy',
  'research/amber-l2/scripts/verify_amber_combat_vfx.groovy',
];
for (const dir of ['server/game/data/scripts/custom/AmberContract', 'server/game/data/scripts/custom/GroupAgite']) {
  for (const file of fs.readdirSync(path.join(root, dir))) if (file.endsWith('.java')) files.push(`${dir}/${file}`);
}
const entries = [];
const digest = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
function preserve(base, relative, location) {
  const src = path.join(base, relative), dest = path.join(backup, 'files', location, relative);
  if (!fs.existsSync(src)) throw new Error('Required continuity file missing: ' + location + '/' + relative);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
  const sha256 = digest(src);
  if (digest(dest) !== sha256) throw new Error('Backup mismatch: ' + relative);
  entries.push({ location, relativePath: relative.replace(/\\/g, '/'), bytes: fs.statSync(src).size, sha256 });
}
for (const file of files) preserve(root, file, 'l2-local');
for (const dir of ['system-hud', 'system', 'animations', 'systextures']) {
  for (const file of fs.readdirSync(path.join(client, dir))) {
    if (/^(Amber|L2Amber)/i.test(file) || (dir === 'system-hud' && ['npcgrp.dat', 'skillgrp.dat', 'skillname-e.dat', 'actionname-e.dat', 'l2.ini'].includes(file))) {
      preserve(client, `${dir}/${file}`, 'l2');
    }
  }
}
const manifest = {
  createdAt: new Date().toISOString(), timeZone: 'America/Argentina/Buenos_Aires',
  portableFolders: ['l2-local', 'l2'], sourceRootAtCapture: root, clientRootAtCapture: client,
  backupRelativePath: path.relative(root, backup).replace(/\\/g, '/'),
  database: { name: config.database, file: path.basename(sql), bytes: fs.statSync(sql).size, sha256: digest(sql),
    consistency: 'single-transaction InnoDB snapshot; client online, later saves are outside this snapshot',
    restorePolicy: 'Do not restore over the existing portable database on return; preserve its later character saves.' },
  files: entries,
};
const serialized = JSON.stringify(manifest, null, 2) + '\n';
fs.writeFileSync(path.join(backup, 'manifest.json'), serialized);
fs.writeFileSync(path.join(handoff, `inventario-${date}.json`), serialized);
console.log(`Saved ${entries.length} verified file copies and SQL snapshot (${manifest.database.bytes} bytes).`);
console.log('Backup: ' + backup);
