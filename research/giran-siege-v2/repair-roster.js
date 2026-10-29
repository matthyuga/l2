'use strict';
const fs=require('fs'),path=require('path');const {createDatabase}=require('../../lab-panel/lib/database');const root=path.resolve(__dirname,'../..');const db=createDatabase(JSON.parse(fs.readFileSync(path.join(root,'lab-panel/config.json'),'utf8')).database);
(async()=>{
 const rows=await db.query("SELECT c.* FROM characters c JOIN lab_normal_npc_profiles p ON p.char_id=c.charId WHERE c.account_name IN ('telemetryarena1','telemetryarena2','telemetryarena3') AND p.recipe_version='normal-pvp-s4-hybrid-v2' ORDER BY c.charId");
 const before=JSON.parse(fs.readFileSync(path.join(root,'backups/giran-siege-v2-2026-10-11/state-before.json'),'utf8')).pilots;
 if(rows.length!==19||before.length!==19)throw new Error('Reserved roster mismatch');
 const backup=path.join(root,'backups/giran-siege-v2-2026-10-11/roster-recovery-before.json');if(!fs.existsSync(backup))fs.writeFileSync(backup,JSON.stringify(rows,null,2));
 for(const row of rows){
  const expected=before.find(p=>p.charId===row.charId);if(!expected||expected.char_name!==row.char_name||expected.classid!==row.classid||row.classid!==row.base_class)throw new Error('Reserved identity mismatch: '+row.char_name);
  if(row.level===79&&row.exp===4179000000){await db.query('UPDATE characters SET level=80,exp=4200000000,expBeforeDeath=0 WHERE charId=? AND level=79 AND exp=4179000000',[row.charId]);console.log('Recovered native siege death: '+row.char_name+' to original lab80');}
  else if(row.level!==80||row.exp<4200000000)throw new Error('Unexpected reserved profile state: '+row.char_name);
 }
 console.log('All19 reserved profiles80; human untouched.');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>db.pool.end());
