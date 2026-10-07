'use strict';

const fs = require('fs');
const path = require('path');
const config = require('../config.json');
const { createDatabase } = require('../lib/database');

async function main() {
  const javaFile = path.join(config.paths.serverData, 'scripts', 'custom', 'LabTelemetry', 'LabTelemetry.java');
  const source = fs.readFileSync(javaFile, 'utf8');
  function extract(name) {
    const assignment = source.match(new RegExp('private static final String ' + name + '\\s*=([\\s\\S]*?);\\r?\\n'));
    if (!assignment) throw new Error('No se encontró ' + name + ' en LabTelemetry.java');
    const parts = [];
    const strings = /"((?:\\.|[^"\\])*)"/g;
    let match;
    while ((match = strings.exec(assignment[1])) !== null) parts.push(JSON.parse('"' + match[1] + '"'));
    return parts.join('');
  }
  const database = createDatabase(config.database);
  await database.query(extract('CREATE_TABLE'));
  await database.query(extract('CREATE_STATS_TABLE'));
  await database.query(extract('CREATE_PLAYER_STATS_TABLE'));
  await database.pool.end();
  console.log('Tablas de telemetría listas.');
}

main().catch(function (error) {
  console.error(error);
  process.exitCode = 1;
});
