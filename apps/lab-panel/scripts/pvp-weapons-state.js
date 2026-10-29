'use strict';
const fs=require('fs'),path=require('path'),mysql=require('mysql2/promise');
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'../config.json'),'utf8'));
(async()=>{const db=await mysql.createConnection(cfg.database);try{
 const [rows]=await db.query("SELECT c.charId,c.char_name,c.clanid,c.classid,c.level,c.online,i.object_id,i.item_id,i.enchant_level,i.loc,i.loc_data FROM characters c JOIN lab_normal_npc_profiles p ON p.char_id=c.charId JOIN items i ON i.owner_id=c.charId WHERE i.loc='PAPERDOLL' OR (c.char_name='ArenaDarius' AND i.item_id IN (6370,6607)) ORDER BY c.char_name,i.loc_data");
 const out=path.resolve(__dirname,'../../backups/pvp-weapons-2026-10-11',process.argv[2]==='before'?'equipment-before.json':'equipment-after.json');fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(rows,null,2));
 if(process.argv[2]!=='before'){const d=rows.filter(r=>r.char_name==='ArenaDarius');if(!d.some(r=>r.item_id===6607&&r.enchant_level===4&&r.loc==='PAPERDOLL')||d.some(r=>r.item_id===6370&&r.loc==='PAPERDOLL'))throw Error('Darius weapon not changed');console.log('PASS: Darius Heaven’s Divider Focus +4 equipped;Saint Spear unequipped');}
 else console.log('Private equipment snapshot saved');
}finally{await db.end();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
