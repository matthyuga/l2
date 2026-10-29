'use strict';
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../texture-library');
module.exports=function textureCatalog(){
 return ['catalog.json','polyhaven/catalog.json','sharetextures/catalog.json','l2/catalog.json'].flatMap(name=>{
 try{return JSON.parse(fs.readFileSync(path.join(root,name),'utf8')).filter(t=>t&&/^(acg|ph|st|l2)_[A-Za-z0-9_-]+$/.test(t.id)&&/^exports\/[A-Za-z0-9_./ -]+\.(jpg|jpeg|png)$/i.test(t.path)&&!t.path.includes('..'));}
 catch{return [];}
 });
};
module.exports.progress=function(){
 const providers=[['ambientcg','ambientCG','progress.json'],['polyhaven','Poly Haven','polyhaven/progress.json'],['sharetextures','ShareTextures','sharetextures/progress.json']].map(([id,title,file])=>{
  try{const p=JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));return {id,title,complete:p.complete,total:p.total,failed:p.failed?.length||0,finished:p.finished};}
  catch{return {id,title,complete:0,total:0,failed:0,finished:false};}
 });
 let run={state:'not-started'};try{run=JSON.parse(fs.readFileSync(path.join(root,'run.json'),'utf8'));}catch{}
 return {providers,complete:providers.reduce((n,p)=>n+p.complete,0),total:providers.reduce((n,p)=>n+p.total,0),state:run.state};
};
