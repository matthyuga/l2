'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../model-catalog');
const gallery=JSON.parse(fs.readFileSync(path.join(root,'gallery.json'),'utf8'));
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'data.json'),'utf8'));
const models=gallery.models.filter(m=>m.native===true||m.key?.startsWith('web_'));
const problems=[],files=new Map(),counts={};
function check(file,key){
 if(files.has(file))return;
 try{const buffer=fs.readFileSync(file);if(!buffer.length)throw Error('empty file');files.set(file,{path:path.relative(root,file).replaceAll('\\','/'),bytes:buffer.length,sha256:crypto.createHash('sha256').update(buffer).digest('hex')});return buffer;}
 catch(error){problems.push({key,file,error:error.message});}
}
for(const model of models){
 counts[model.batch]=(counts[model.batch]||0)+1;
 const entry=data.assets.find(a=>a.id===model.key);
 if(!entry||entry.path!==model.gltf)problems.push({key:model.key,error:'Missing or mismatched editor entry'});
 if(model.native&&!entry?.native)problems.push({key:model.key,error:'Native library flag lost'});
 if(!model.thumbnail)problems.push({key:model.key,error:'Missing thumbnail registration'});
 else check(path.join(root,model.thumbnail),model.key);
 const file=path.join(root,model.gltf),buffer=check(file,model.key);if(!buffer)continue;
 try{
  let json;
  if(path.extname(file)==='.glb'){
   if(buffer.toString('ascii',0,4)!=='glTF'||buffer.readUInt32LE(4)!==2||buffer.readUInt32LE(8)!==buffer.length)throw Error('Invalid GLB header');
   json=JSON.parse(buffer.toString('utf8',20,20+buffer.readUInt32LE(12)));
  }else json=JSON.parse(buffer.toString('utf8'));
  for(const ref of [...json.buffers||[],...json.images||[]])if(ref.uri&&!ref.uri.startsWith('data:'))check(path.resolve(path.dirname(file),decodeURIComponent(ref.uri)),model.key);
 }catch(error){problems.push({key:model.key,error:error.message});}
}
function walk(dir,extension){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name),extension):e.name.toLowerCase().endsWith(extension)?[path.join(dir,e.name)]:[]);}
const source=path.resolve(__dirname,'../web-assets/sources');
const kenney=walk(path.join(source,'kenney_nature-kit/Models/GLTF format'),'.glb');
const ruins=walk(path.join(source,'3td_fantasy-ruins'),'.dae').filter(p=>!p.endsWith('.l2lab.dae'));
if(kenney.length!==counts['Web CC0 · Kenney Nature Kit'])problems.push({error:'Kenney source/import count mismatch',source:kenney.length});
if(ruins.length!==counts['Web CC0 · 3TD Fantasy Ruins'])problems.push({error:'Fantasy Ruins source/import count mismatch',source:ruins.length});
const report={date:new Date().toISOString(),passed:!problems.length,total:models.length,counts,sourceModels:{kenney:kenney.length,ruins:ruins.length},verifiedFiles:files.size,problems,files:[...files.values()]};
fs.writeFileSync(path.join(__dirname,'environment-assets-audit.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,files:undefined},null,2));
if(!report.passed)process.exitCode=1;
