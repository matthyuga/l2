'use strict';
const fs=require('fs'),path=require('path'),mysql=require('mysql2/promise');
const root=path.resolve(__dirname,'../..'),report=path.join(root,'reports/capacity-benchmark-2026-10-11');
const baseline=JSON.parse(fs.readFileSync(path.join(root,'backups/capacity-benchmark-2026-10-11/original-baseline.json'),'utf8'));
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'../config.json'),'utf8'));
const keys={characters:'charId',character_subclasses:'charId',character_skills:'charId',character_hennas:'charId',character_variables:'charId',items:'owner_id',clan_data:'clan_id',castle:'id',siege_clans:'castle_id'};
const norm=rows=>rows.map(row=>JSON.stringify(Object.fromEntries(Object.entries(row).sort(([a],[b])=>a.localeCompare(b)).map(([k,v])=>[k,v===null?null:String(v)])))).sort();
(async()=>{const db=await mysql.createConnection({...cfg.database,dateStrings:true,supportBigNumbers:true,bigNumberStrings:true});try{
 const result={tables:{},temporary:{},pass:true};
 for(const [table,expected] of Object.entries(baseline)){
  const ids=[...new Set(expected.map(r=>r[keys[table]]))];
  const [actual]=ids.length?await db.query('SELECT * FROM '+table+' WHERE '+keys[table]+' IN (?)',[ids]):await db.query('SELECT * FROM '+table+' WHERE '+keys[table]+'=3');
  const a=norm(actual),b=norm(expected),same=JSON.stringify(a)===JSON.stringify(b);
  result.tables[table]={before:expected.length,after:actual.length,identical:same};
  if(!same){result.pass=false;result.tables[table].missing=b.filter(r=>!a.includes(r));result.tables[table].changed=a.filter(r=>!b.includes(r));}
 }
 const created=[];for(const dir of [report,path.join(report,'protected')]){const lines=fs.readFileSync(path.join(dir,'created-ids.txt'),'utf8').split(/\r?\n/);created.push(...JSON.parse(lines[1].slice('characters='.length)));}
 for(const [table,key] of Object.entries({...keys,character_summons:'ownerId',lab_player_stats:'char_id',lab_player_stat_profiles:'char_id',lab_creature_stats:'object_id'})){
  if(['clan_data','castle','siege_clans'].includes(table))continue;
  const [rows]=await db.query('SELECT COUNT(*) AS n FROM '+table+' WHERE '+key+' IN (?)',[created]);result.temporary[table]=Number(rows[0].n);if(Number(rows[0].n)!==0)result.pass=false;
 }
 const prefixes=[report,path.join(report,'protected')].map(d=>fs.readFileSync(path.join(d,'created-ids.txt'),'utf8').split(/\r?\n/)[0]);
 const [clans]=await db.query('SELECT COUNT(*) n FROM clan_data WHERE clan_name LIKE ? OR clan_name LIKE ?',[prefixes[0]+'%',prefixes[1]+'%']);result.temporary.clans=Number(clans[0].n);if(Number(clans[0].n)!==0)result.pass=false;
 fs.writeFileSync(path.join(report,'cleanup-verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({pass:result.pass,tables:result.tables,temporary:result.temporary},null,2));if(!result.pass)process.exitCode=1;
}finally{await db.end();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
