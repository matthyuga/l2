const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../atmosphere-library'),file=path.join(root,'preview-catalog.json');
function catalog(){try{return JSON.parse(fs.readFileSync(file,'utf8'));}catch{return {items:[],errors:[],audioNote:'Preparar biblioteca con build-preview.py.'};}}
catalog.root=root;module.exports=catalog;
