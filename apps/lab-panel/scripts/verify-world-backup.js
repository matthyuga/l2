'use strict';
const fs=require('fs'),path=require('path'),mysql=require('mysql2/promise'),cp=require('child_process');
const root=path.resolve(__dirname,'../..'),backup=path.resolve(process.argv[2]);
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'../config.json'),'utf8')).database;
const schema='l2_backup_verify_'+Date.now(),option=path.join(backup,'.verify-client.cnf');
const quote=s=>'"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"')+'"';
(async()=>{let db,created=false;try{
 const testConfig={host:'127.0.0.1',port:33307,user:'root',password:''};
 db=await mysql.createConnection(testConfig);await db.query('CREATE DATABASE `'+schema+'` CHARACTER SET utf8mb4');created=true;
 fs.writeFileSync(option,'[client]\n'+['host','port','user','password'].map(k=>k+'='+quote(testConfig[k])).join('\n')+'\ndefault-character-set=utf8mb4\n');
 const input=fs.openSync(path.join(backup,'database.sql'),'r'),error=fs.openSync(path.join(backup,'restore-test.stderr.txt'),'w');
 const child=cp.spawn(path.join(root,'tools/mariadb-11.8.9-winx64/bin/mariadb.exe'),['--defaults-extra-file='+option,'--binary-mode',schema],{stdio:[input,'ignore',error],windowsHide:true});fs.closeSync(input);fs.closeSync(error);
 console.log('Importing backup into isolated verification schema');
 const exit=await new Promise((resolve,reject)=>{child.on('error',reject);child.on('exit',resolve)});if(exit!==0)throw Error('Isolated restore failed: '+exit);
 const [tables]=await db.query('SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=? ORDER BY TABLE_NAME',[schema]);
 const counts={};for(const row of tables){const table=row.TABLE_NAME;const [r]=await db.query('SELECT COUNT(*) n FROM `'+schema+'`.`'+table+'`');counts[table]=Number(r[0].n);}
 const [profiles]=await db.query('SELECT COUNT(*) n FROM `'+schema+'`.lab_normal_npc_profiles');if(Number(profiles[0].n)!==39)throw Error('Original 39 profiles missing');
 const [integrity]=await db.query('CHECK TABLE '+tables.map(r=>'`'+schema+'`.`'+r.TABLE_NAME+'`').join(','));if(integrity.some(r=>r.Msg_type==='error'||r.Msg_type==='warning'))throw Error('Restored table integrity check failed');
 const [equipment]=await db.query('SELECT COUNT(*) n FROM `'+schema+'`.items i JOIN `'+schema+'`.characters c ON c.charId=i.owner_id WHERE c.char_name=\'ArenaDarius\' AND i.item_id=6607 AND i.enchant_level=4 AND i.loc=\'PAPERDOLL\'');if(Number(equipment[0].n)!==1)throw Error('Latest PvP weapon missing');
 fs.writeFileSync(path.join(backup,'restore-verification.json'),JSON.stringify({pass:true,schema,tables:tables.length,row_counts:counts,profiles:39,darius_weapon:6607,completed_utc:new Date().toISOString()},null,2));
 console.log('PASS: SQL imported; '+tables.length+' tables checked;39 original profiles and current PvP equipment present');
}finally{
 if(fs.existsSync(option))fs.unlinkSync(option);if(db){try{if(created)await db.query('DROP DATABASE `'+schema+'`');}finally{await db.end();}}
}})().catch(e=>{console.error(e.message);process.exitCode=1});
