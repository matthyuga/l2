'use strict';
const fs=require('fs'),path=require('path');const {createDatabase}=require('../../lab-panel/lib/database');const root=path.resolve(__dirname,'../..');const db=createDatabase(JSON.parse(fs.readFileSync(path.join(root,'lab-panel/config.json'),'utf8')).database);
(async()=>{
 const result={};
 for(const [key,sql] of Object.entries({human:"SELECT * FROM characters WHERE char_name='Hellkevin'",inventory:"SELECT * FROM items WHERE owner_id=(SELECT charId FROM characters WHERE char_name='Hellkevin') ORDER BY object_id",clans:'SELECT * FROM clan_data ORDER BY clan_id',skills:'SELECT * FROM clan_skills ORDER BY clan_id,skill_id,sub_pledge_id',castle:'SELECT * FROM castle WHERE id=3',siege:'SELECT * FROM siege_clans WHERE castle_id=3 ORDER BY clan_id',guards:'SELECT * FROM castle_siege_guards WHERE castleId=3 ORDER BY npcId,x,y,z',pilots:"SELECT c.charId,c.char_name,c.level,c.exp,c.online,c.clanid,c.classid FROM characters c JOIN lab_normal_npc_profiles p ON p.char_id=c.charId WHERE p.recipe_version='normal-pvp-s4-hybrid-v2' ORDER BY c.charId"}))result[key]=await db.query(sql);
 const target=path.join(root,'backups/giran-siege-v3-2026-10-11',process.argv[2]+'.json');fs.writeFileSync(target,JSON.stringify(result,null,2));
 if(process.argv[2]==='after'){
  const before=JSON.parse(fs.readFileSync(path.join(path.dirname(target),'before.json'),'utf8'));
  for(const key of ['human','inventory','clans','skills','castle','guards'])if(JSON.stringify(before[key])!==JSON.stringify(result[key]))throw new Error('Unexpected persistent change: '+key);
  if(result.pilots.length!==19||result.pilots.some(p=>p.level!==80||p.online!==0))throw new Error('Pilot cleanup/level failed');
  const rivals=result.clans.filter(c=>['Holly','Sacred','Fury','Waves'].includes(c.clan_name)).map(c=>c.clan_id).sort((a,b)=>a-b);
  if(result.siege.length!==4||result.siege.some(r=>Number(r.type)!==1)||JSON.stringify(result.siege.map(r=>r.clan_id).sort((a,b)=>a-b))!==JSON.stringify(rivals))throw new Error('Expected four rival attackers');
  console.log('Persistent state PASS: human/inventory,clans/reputation/blood/skills,owned castle/schedule,382guards identical;four rivals registered;19pilots offline80.');
 }else console.log('Full human/clan/owned-castle state saved.');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>db.pool.end());
