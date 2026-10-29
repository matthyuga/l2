'use strict';
const fs=require('fs'),path=require('path'),mysql=require('mysql2/promise');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'reports/lazy-region-collections-2026-10-12');
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'../config.json'),'utf8')).database;
const key={characters:'charId',character_subclasses:'charId',character_skills:'charId',character_hennas:'charId',character_variables:'charId',items:'owner_id',clan_data:'clan_id',castle:'id',siege_clans:'castle_id'};
const excluded=new Set(['curHp','curMp','curCp','maxHp','maxMp','maxCp','lastAccess','onlinetime','z','online']);
function normalized(rows,table){return rows.map(row=>JSON.stringify(Object.fromEntries(Object.entries(row).filter(([k])=>table!=='characters'||!excluded.has(k)).sort(([a],[b])=>a.localeCompare(b)).map(([k,v])=>[k,v===null?null:String(v)])))).sort();}
(async()=>{const db=await mysql.createConnection({...cfg,dateStrings:true,supportBigNumbers:true,bigNumberStrings:true});try{
 const before=process.argv[2]==='before';
 const baseline=JSON.parse(fs.readFileSync(path.join(root,before?'reports/world-empty-2026-10-11/original-baseline.json':'reports/lazy-region-collections-2026-10-12/baseline-private.json'),'utf8'));
 const actual={},out={pass:true,tables:{},excluded_transient_character_fields:[...excluded]};
 for(const [table,expected] of Object.entries(baseline)){
  const ids=[...new Set(expected.map(v=>v[key[table]]))];
  const [rows]=ids.length?await db.query('SELECT * FROM '+table+' WHERE '+key[table]+' IN (?)',[ids]):await db.query('SELECT * FROM '+table+' WHERE '+key[table]+'=3');
  actual[table]=rows;const identical=JSON.stringify(normalized(expected,table))===JSON.stringify(normalized(rows,table));
  out.tables[table]={before:expected.length,after:rows.length,identical};if(!identical)out.pass=false;
 }
 if(before){fs.writeFileSync(path.join(dir,'baseline-private.json'),JSON.stringify(actual));fs.writeFileSync(path.join(dir,'reputation-before.tsv'),actual.clan_data.map(c=>[c.clan_id,c.clan_name,c.reputation_score].join('\t')).join('\n')+'\n');console.log('Current SQL reference saved');}
 else{fs.writeFileSync(path.join(dir,'preservation-verification.json'),JSON.stringify(out,null,2));console.log(JSON.stringify(out,null,2));if(!out.pass)process.exitCode=1;}
}finally{await db.end();}})().catch(e=>{console.error(e.message);process.exitCode=1});
