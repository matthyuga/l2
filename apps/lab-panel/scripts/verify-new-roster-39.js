'use strict';
// Read-only persistence/equipment check for the twenty approved additions.
const fs=require('fs'),path=require('path'),mysql=require('mysql2/promise');
const config=JSON.parse(fs.readFileSync(path.join(__dirname,'../config.json'),'utf8'));
const names=['Darion','Valerian','Malrik','Lucien','Seraphine','Darius','Thalion','Elowen','Faelith','Nerys','Draven','Nysera','Veyron','Zareth','Saevra','Rhogar','Mazhura','Urkan','Dagna','Borin'];
const races=[0,0,0,0,0,0,1,1,1,1,2,2,2,2,2,3,3,3,4,4];
const mains=[88,90,91,96,98,89,99,100,104,105,106,107,109,111,112,114,116,88,117,90];
const weapons=[6580,6364,6364,6608,6608,6607,6364,6364,6608,6608,6364,6580,7577,6608,6608,6371,6608,6580,6365,6364];
const mage=[3,4,8,9,13,14,16],female=[4,7,8,9,11,14,16,18],light=[12,15];
function check(ok,msg){if(!ok)throw Error(msg);}
(async()=>{
 const con=await mysql.createConnection(config.database);
 try {
  const [profiles]=await con.query('SELECT p.*,c.race,c.sex,c.level,c.classid,c.base_class,c.online FROM lab_normal_npc_profiles p JOIN characters c ON c.charId=p.char_id WHERE p.npc_template_id BETWEEN 901119 AND 901138 ORDER BY p.npc_template_id');
  check(profiles.length===20,'Faltan perfiles nuevos');
  for(let i=0;i<20;i++){
   const p=profiles[i],isMage=mage.includes(i);
   check(p.npc_template_id===901119+i&&p.char_name==='Arena'+names[i],'ID/nombre '+names[i]);
   check(Number(p.race)===races[i]&&Number(p.sex)===(female.includes(i)?1:0),'Raza/sexo '+names[i]);
   check(Number(p.level)===80&&Number(p.base_class)===mains[i]&&Number(p.classid)===mains[i],'Nivel/principal '+names[i]);
   check(Number(p.online)===0,'Perfil sigue conectado '+names[i]);
   const [vars]=await con.execute('SELECT var,val FROM character_variables WHERE charId=? AND var IN (\'RACIAL_PROFILE\',\'RACIAL_STAT_RACE\')',[p.char_id]);
   const v=Object.fromEntries(vars.map(x=>[x.var,x.val]));
   check(v.RACIAL_PROFILE===(isMage?'MYSTIC':'FIGHTER')&&Number(v.RACIAL_STAT_RACE)===races[i],'Origen racial '+names[i]);
   const [items]=await con.execute("SELECT item_id,enchant_level FROM items WHERE owner_id=? AND loc='PAPERDOLL'",[p.char_id]);
   const armor=isMage?[6383,6384,6385,6386,6377]:light.includes(i)?[6379,6380,6381,6382]:[6373,6374,6375,6376,6378];
   const required=[...armor,weapons[i],858,858,889,889,920];
   if(!isMage&&[90,91,99,100,106].includes(mains[i]))required.push(6377);
   for(const id of new Set(required))check(items.filter(x=>Number(x.item_id)===id&&Number(x.enchant_level)===4).length===required.filter(x=>x===id).length,'Equipo +4 '+names[i]+' item='+id);
   console.log('PASS '+names[i]+': persistencia, origen racial, sexo, nivel80, equipo/joyas+4 y offline');
  }
  console.log('SUCCESS nuevos20/20');
 }finally{await con.end();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
