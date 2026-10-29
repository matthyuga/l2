'use strict';
// Read-only post-event persistence check. Credentials stay in the local panel config.
const fs=require('fs'),path=require('path'),mysql=require('mysql2/promise');
const config=JSON.parse(fs.readFileSync(path.join(__dirname,'../config.json'),'utf8'));
function check(ok,label){if(!ok)throw Error(label);}
(async()=>{const db=await mysql.createConnection(config.database);try{
 const [clans]=await db.query("SELECT clan_id,clan_name,clan_level,crest_id,ally_crest_id,ally_id,hasCastle FROM clan_data WHERE clan_name IN ('Hellsing','Holly','Sacred','Fury','Waves','Raiders')");
 check(clans.length===6,'Six scenario clans');const raid=clans.find(c=>c.clan_name==='Raiders');
 for(const [name,crest] of Object.entries({Hellsing:7,Holly:9,Sacred:11,Fury:13,Waves:15})){const c=clans.find(c=>c.clan_name===name);check(c.crest_id===crest&&c.ally_crest_id===crest+1,'Existing logos preserved '+name);}
 check(raid.clan_level===5&&!raid.crest_id&&!raid.ally_crest_id&&!raid.ally_id,'Raiders level5 crestless');
 const [members]=await db.execute('SELECT char_name,online,level FROM characters WHERE clanid=?',[raid.clan_id]);
 check(members.length===20&&members.every(c=>c.char_name.startsWith('Arena')&&!c.online&&c.level===80),'20 reserved level80 attackers offline');
 const [registration]=await db.query('SELECT s.type,c.clan_name FROM siege_clans s JOIN clan_data c ON c.clan_id=s.clan_id WHERE s.castle_id=3');
 check(registration.some(r=>r.clan_name==='Raiders'&&r.type===1),'Native attacker registration');
 for(const n of ['Holly','Sacred','Fury','Waves'])check(registration.some(r=>r.clan_name===n&&r.type===0),'Native defender '+n);
 check(clans.find(c=>c.clan_name==='Hellsing').hasCastle===3,'Hellsing owner preserved');
 const [online]=await db.query('SELECT COUNT(*) AS n FROM characters c JOIN lab_normal_npc_profiles p ON p.char_id=c.charId WHERE c.online<>0');check(online[0].n===0,'All39 profiles offline');
 console.log(JSON.stringify({result:'PASS',clans:clans.map(c=>({name:c.clan_name,crest:c.crest_id,allyCrest:c.ally_crest_id})),attackers:members.length,registrations:registration,profilesOnline:0},null,2));
}finally{await db.end();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
