'use strict';
const fs=require('fs'),path=require('path');
const {createDatabase}=require('../../lab-panel/lib/database');
const root=path.resolve(__dirname,'../..');
const db=createDatabase(JSON.parse(fs.readFileSync(path.join(root,'lab-panel/config.json'),'utf8')).database);
(async()=>{
 const result={};
 for(const [key,sql] of Object.entries({clans:'SELECT * FROM clan_data ORDER BY clan_id',skills:'SELECT * FROM clan_skills ORDER BY clan_id,skill_id,sub_pledge_id',members:'SELECT charId,char_name,clanid,online,classid,base_class,level,x,y,z FROM characters ORDER BY charId',castle:'SELECT * FROM castle WHERE id=3',siege:'SELECT * FROM siege_clans WHERE castle_id=3 ORDER BY clan_id',guards:'SELECT * FROM castle_siege_guards WHERE castleId=3 ORDER BY npcId,x,y,z'}))result[key]=await db.query(sql);
 fs.writeFileSync(path.resolve(process.argv[2]),JSON.stringify(result,null,2));console.log('Giran/clan/character snapshot saved.');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>db.pool.end());
