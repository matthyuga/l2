const fs=require('fs'),path=require('path'),crypto=require('crypto');
const source=path.join(__dirname,'projects/gludiobrisas1.json'),target=path.join(__dirname,'projects/gludiobrisas1-animado.json');
if(fs.existsSync(target)&&!process.argv.includes('--rebuild'))throw Error('The animated project exists; rebuild only before user edits.');
const project=JSON.parse(fs.readFileSync(source)),asset='custom_gludio_brisas_decor',group=crypto.randomUUID();
function entry(name,position,scale,kind='effect',parent=group){return {id:crypto.randomUUID(),name,asset,node:'',base:false,kind,parent,locked:false,visible:true,position,rotation:[0,0,0],scale,surfaces:[],parts:[]};}
const zone=entry('07 · Viento, hojas y agua',[0,0,0],[1,1,1],'group',null);zone.id=group;project.objects.push(zone);
function add(name,position,scale,effect){project.objects.push({...entry(name,position,scale),effect});}
let seed=173;
for(const x of [-6.05,6.05])for(const z of [-6.52,6.52])add('Viento ascendente · rejilla '+(x<0?'oeste':'este')+' '+(z<0?'norte':'sur'),[x,.485,z],[1,1,1],{type:'wind',seed:seed++,count:20,color:'#c8e5e8',radius:.80,height:2.5,speed:.85});
for(const tree of project.objects.filter(o=>['m0561','b2_95d6af336577db0a6d'].includes(o.asset))){const pink=tree.asset!=='m0561';add(pink?'Hojas rosas · árbol central':'Hojas verdes · árbol central',[...tree.position],[1,1,1],{type:'leaves',seed:seed++,count:96,color:pink?'#f6a3c9':'#83b64a',radius:2.9,height:4.5,speed:.90});}
for(const f of project.objects.filter(o=>o.node==='Fuente'))add('Agua viva · fuente '+(f.position[0]<0?'oeste':'este'),[...f.position],[...f.scale],{type:'fountain',seed:seed++,count:180,color:'#329fae',radius:1.86,height:2.6,speed:1});
project.name='gludiobrisas1-animado';project.reference={...project.reference,effects:'Cuatro corrientes ascendentes, hojas rosas y verdes, dos fuentes con caída de agua, ondas, gotas, espuma y burbujas.'};
project.cameras[2]={position:[-11,8,12],target:[0,2.7,0],fov:42};
project.cameras[7]={position:[-14.4,3.1,-11.8],target:[-11,.95,-7.7],fov:38};
project.cameras[8]={position:[11.3,5.5,-12.5],target:[6.05,1.5,-6.52],fov:38};
fs.writeFileSync(target,JSON.stringify(project,null,2));const folder=path.resolve(__dirname,'../../mapas editados/gludiobrisas1-animado');fs.mkdirSync(folder,{recursive:true});fs.copyFileSync(target,path.join(folder,path.basename(target)));console.log({project:target,objects:project.objects.length,emitters:project.objects.filter(o=>o.kind==='effect').length});
