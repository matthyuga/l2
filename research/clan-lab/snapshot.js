'use strict';
const fs=require('fs'),path=require('path');
const {createDatabase}=require('../../lab-panel/lib/database');
const root=path.resolve(__dirname,'../..');
const db=createDatabase(JSON.parse(fs.readFileSync(path.join(root,'lab-panel/config.json'),'utf8')).database);
(async()=>{
 const result={clans:await db.query('SELECT * FROM clan_data ORDER BY clan_id'),skills:await db.query('SELECT * FROM clan_skills ORDER BY clan_id,skill_id,sub_pledge_id'),members:await db.query('SELECT charId,char_name,clanid FROM characters WHERE clanid<>0 ORDER BY charId'),probe:await db.query("SELECT charId,char_name,account_name,clanid,online FROM characters WHERE char_name='AmberOwnerProbe'")};
 fs.writeFileSync(path.resolve(process.argv[2]),JSON.stringify(result,null,2));
 console.log('Clan/probe snapshot saved.');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>db.pool.end());
