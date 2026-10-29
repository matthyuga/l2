'use strict';
const fs=require('fs'),path=require('path'),mysql=require('mysql2/promise');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'reports/world-empty-2026-10-11');
const baseline=JSON.parse(fs.readFileSync(path.join(dir,'original-baseline.json'),'utf8'));
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'../config.json'),'utf8')).database;
const key={characters:'charId',character_subclasses:'charId',character_skills:'charId',character_hennas:'charId',character_variables:'charId',items:'owner_id',clan_data:'clan_id',castle:'id',siege_clans:'castle_id'};
const transient=new Set(['curHp','curMp','curCp','maxHp','maxMp','maxCp','lastAccess','onlinetime','z']);
function normalized(rows,table){return rows.map(row=>JSON.stringify(Object.fromEntries(Object.entries(row).filter(([k])=>table!=='characters'||!transient.has(k)).sort(([a],[b])=>a.localeCompare(b)).map(([k,v])=>[k,v===null?null:String(v)])))).sort();}
(async()=>{const db=await mysql.createConnection({...cfg,dateStrings:true,supportBigNumbers:true,bigNumberStrings:true});try{
 const out={pass:true,tables:{},character_fields_excluded_as_rebuilt_cache:[...transient]};
 for(const [table,expected] of Object.entries(baseline)){
  const ids=[...new Set(expected.map(v=>v[key[table]]))];
  const [actual]=ids.length?await db.query('SELECT * FROM '+table+' WHERE '+key[table]+' IN (?)',[ids]):await db.query('SELECT * FROM '+table+' WHERE '+key[table]+'=3');
  const identical=JSON.stringify(normalized(expected,table))===JSON.stringify(normalized(actual,table));out.tables[table]={before:expected.length,after:actual.length,identical};if(!identical)out.pass=false;
 }
 fs.writeFileSync(path.join(dir,'preservation-verification.json'),JSON.stringify(out,null,2));console.log(JSON.stringify(out,null,2));if(!out.pass)process.exitCode=1;
}finally{await db.end();}})().catch(e=>{console.error(e.message);process.exitCode=1});
