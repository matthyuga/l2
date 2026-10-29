'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../model-catalog/exports'),output=path.join(__dirname,'l2/catalog.json');
const image=/\.(png|jpe?g)$/i,skipRoot=new Set(['cc0-textures','thumbs','vendor']);
const auxiliary=/(^|[_-])(normal|norm|nrm|rough|roughness|spec|specular|height|displace|displacement|ao|ambientocclusion|metallic|opacity|mask)([_-]|$)/i;
const categories=[
 ['Centros y medallones',/center|centre|medal|rosett|mosaic|seal|symbol|emblem|crest|circle|round|mandala|maincenter/],
 ['Escaleras',/stair|step|escal/],['Pisos y caminos',/floor|ground|walk|road|pave|street|tile|court|plaza|land/],
 ['Paredes y fachadas',/wall|brick|facade|building|house|castle|temple|hall/],['Ornamentos',/ornament|deco|trim|frame|pillar|column|arch|statue|relief/],
 ['Techos',/roof|ceiling|tejado/],['Madera',/wood|timber|plank|parquet/],['Metal',/metal|steel|iron|bronze|gold|silver/],
 ['Roca y terreno',/rock|stone|cliff|soil|sand|grass|terrain|dirt|mud/],['Puertas y ventanas',/door|gate|window/],
 ['Agua y naturaleza',/water|river|sea|ocean|tree|leaf|plant|flower/],['Objetos y utilería',/box|crate|barrel|furniture|table|chair|lamp|candle|rope|weapon|shield/],
 ['Efectos y símbolos',/rune|magic|effect|glow|fire|smoke|cloud|light|fx/]
];
function walk(dir,out=[]){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const full=path.join(dir,e.name);if(e.isDirectory()){if(dir===root&&skipRoot.has(e.name))continue;walk(full,out);}else if(image.test(e.name)&&!auxiliary.test(path.parse(e.name).name))out.push(full);}return out;}
function clean(value){return value.replace(/[_-]+/g,' ').replace(/\s+/g,' ').trim();}
const files=walk(root),seen=new Map(),items=[];
for(let i=0;i<files.length;i++){
 const file=files[i],relative=path.relative(root,file).replaceAll('\\','/'),name=path.parse(file).name,hay=(name+' '+relative).toLowerCase();
 const hash=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');if(seen.has(hash))continue;seen.set(hash,relative);
 const category=(categories.find(([,re])=>re.test(hay))||['Otras texturas'])[0],parts=relative.split('/'),pack=parts[0],library=parts.find(v=>/_t\d?$|_tex$|texture/i.test(v))||pack;
 const tokens=[...new Set(clean(name).toLowerCase().split(' ').filter(v=>v.length>2))].slice(0,16);
 items.push({id:'l2_'+hash.slice(0,20),title:clean(name),original:name,category,path:'exports/'+relative,thumbnail:'exports/'+relative,provider:'Lineage II local',license:'Recurso local del proyecto',sourcePack:pack,sourceLibrary:library,tags:[category.toLowerCase(),clean(pack).toLowerCase(),...tokens],single:/center|centre|medal|rosett|mosaic|seal|symbol|emblem|crest|maincenter/.test(hay)});
 if(i&&i%2000===0)process.stdout.write(`Procesadas ${i}/${files.length}\n`);
}
items.sort((a,b)=>a.category.localeCompare(b.category,'es')||a.title.localeCompare(b.title,'es'));
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(items,null,2));
console.log(`Catálogo L2: ${items.length} texturas únicas de ${files.length} imágenes candidatas.`);
