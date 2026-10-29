'use strict';
// Recreate Kevin's giran1/cohete references as a separate visual project.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const catalog=path.resolve(__dirname,'../model-catalog'),assetDir=path.join(catalog,'exports/giranmodificado1');
const refine=process.argv.includes('--refine');
if(fs.existsSync(path.join(__dirname,'projects/giranmodificado1.json'))&&!refine)throw Error('giranmodificado1 already exists; do not overwrite.');
fs.mkdirSync(assetDir,{recursive:true});
const assetId='custom_giranmodificado1_garden';
const positions=[-10.36,0,-9.6,-10.36,0,9.6,10.36,0,9.6,10.36,0,-9.6];
const normals=[0,1,0,0,1,0,0,1,0,0,1,0],uv=[0,0,0,8,8,8,8,0],indices=[0,1,2,0,2,3];
const buffers=[],views=[],accessors=[];
function accessor(values,type,components,integer=false){
 const array=integer?new Uint16Array(values):new Float32Array(values);let offset=buffers.reduce((n,b)=>n+b.length,0);const padding=(4-offset%4)%4;if(padding){buffers.push(Buffer.alloc(padding));offset+=padding;}
 const data=Buffer.from(array.buffer);const vi=views.length;views.push({buffer:0,byteOffset:offset,byteLength:data.length});buffers.push(data);
 const a={bufferView:vi,componentType:integer?5123:5126,count:values.length/components,type};
 if(type==='VEC3'){a.min=Array.from({length:3},(_,k)=>Math.min(...values.filter((_,i)=>i%3===k)));a.max=Array.from({length:3},(_,k)=>Math.max(...values.filter((_,i)=>i%3===k)));}
 accessors.push(a);return accessors.length-1;
}
function plane(width,depth,repeat,material){return {primitives:[{attributes:{POSITION:accessor([-width/2,0,-depth/2,-width/2,0,depth/2,width/2,0,depth/2,width/2,0,-depth/2],'VEC3',3),NORMAL:accessor(normals,'VEC3',3),TEXCOORD_0:accessor([0,0,0,repeat,repeat,repeat,repeat,0],'VEC2',2)},indices:accessor(indices,'SCALAR',1,true),material}]};}
function grassRing(){
 const pos=[],norm=[],tex=[],ind=[];
 function polygon(points){const area=points.reduce((s,p,i)=>{const q=points[(i+1)%points.length];return s+p[0]*q[1]-q[0]*p[1];},0);if(area>0)points.reverse();const first=pos.length/3;for(const [x,z]of points){pos.push(x,0,z);norm.push(0,1,0);tex.push((x+10.36)/2.3,(z+9.6)/2.3);}for(let i=1;i<points.length-1;i++)ind.push(first,first+i,first+i+1);}
 function rect(x0,z0,x1,z1){polygon([[x0,z0],[x0,z1],[x1,z1],[x1,z0]]);}
 const cx=-.119,cz=-.005,r=4.735,d=1.96;
 rect(-10.36,-9.6,cx-r,9.6);rect(cx+r,-9.6,10.36,9.6);rect(cx-r,-9.6,cx+r,cz-r);rect(cx-r,cz+r,cx+r,9.6);
 for(const sx of [-1,1])for(const sz of [-1,1])polygon([[cx+sx*r,cz+sz*r],[cx+sx*d,cz+sz*r],[cx+sx*r,cz+sz*d]]);
 return {primitives:[{attributes:{POSITION:accessor(pos,'VEC3',3),NORMAL:accessor(norm,'VEC3',3),TEXCOORD_0:accessor(tex,'VEC2',2)},indices:accessor(ind,'SCALAR',1,true),material:0}]};
}
const meshes=[grassRing(),plane(2.08,2.08,1,1),plane(2.55,2.55,1,1)];
const nodes=[{name:'Césped de la plaza central',mesh:0}];
for(const z of [-6.7,6.7])for(let i=-3;i<=3;i++)nodes.push({name:'Losa del sendero '+nodes.length,mesh:1,translation:[i*2.47,.06,z]});
for(const x of [-7.41,7.41])for(let i=-2;i<=2;i++)nodes.push({name:'Losa del sendero '+nodes.length,mesh:1,translation:[x,.06,i*2.23]});
for(const x of [-9.08,9.08])for(const z of [-8.32,8.32])nodes.push({name:'Base de árbol '+nodes.length,mesh:2,translation:[x,.06,z]});
const binary=Buffer.concat(buffers);
const gltf={asset:{version:'2.0',generator:'L2 Lab - giranmodificado1 reference reconstruction'},scene:0,scenes:[{nodes:nodes.map((_,i)=>i)}],nodes,meshes,buffers:[{uri:'garden.bin',byteLength:binary.length}],bufferViews:views,accessors,
 images:[{uri:'grass.jpg'},{uri:'paving.png'}],textures:[{source:0,sampler:0},{source:1,sampler:0}],samplers:[{wrapS:10497,wrapT:10497,magFilter:9729,minFilter:9987}],
 materials:[{name:'Césped de Giran',doubleSided:true,pbrMetallicRoughness:{baseColorTexture:{index:0},baseColorFactor:[.30,.34,.26,1],metallicFactor:0,roughnessFactor:1}},{name:'Losas ornamentales de Giran',doubleSided:true,pbrMetallicRoughness:{baseColorTexture:{index:1},metallicFactor:0,roughnessFactor:.95}}]};
fs.writeFileSync(path.join(assetDir,'garden.bin'),binary);fs.writeFileSync(path.join(assetDir,'garden.gltf'),JSON.stringify(gltf));
fs.copyFileSync(path.join(catalog,'exports/cc0-textures/ambientcg/Grass005/Grass005_2K-JPG_Color.jpg'),path.join(assetDir,'grass.jpg'));
fs.copyFileSync(path.join(catalog,'exports/scene-giran-city/Giran_floor04a.png'),path.join(assetDir,'paving.png'));
const model={key:assetId,title:'Giran modificado 1 · jardín y sendero',mesh:'Jardín de la plaza central',package:'Proyecto personal Giran',category:'Objetos',gltf:'exports/giranmodificado1/garden.gltf',thumbnail:'thumbs/giranmodificado1-garden.png',status:'ready',native:false,batch:'Proyectos personales · Giran',names:[],types:['StaticMesh'],source:'Kevin: giran1.jpg y cohete.jpg; losas L2 existentes; césped ambientCG Grass005 CC0'};
const galleryPath=path.join(catalog,'gallery.json'),gallery=JSON.parse(fs.readFileSync(galleryPath));gallery.models=gallery.models.filter(m=>m.key!==assetId);gallery.models.push(model);fs.writeFileSync(galleryPath,JSON.stringify(gallery,null,2));
const dataPath=path.join(__dirname,'data.json'),data=JSON.parse(fs.readFileSync(dataPath));data.assets=data.assets.filter(a=>a.id!==assetId);data.assets.push({id:assetId,title:model.title,path:model.gltf,thumbnail:model.thumbnail,mesh:model.mesh,category:model.category,native:false,batch:model.batch});fs.writeFileSync(dataPath,JSON.stringify(data,null,2));
// Capture a pristine base in an isolated browser, never the user's draft.
(async()=>{
 if(refine){const file=path.join(__dirname,'projects/giranmodificado1.json');const project=JSON.parse(fs.readFileSync(file));for(const e of project.objects){if(e.asset===assetId)e.position[1]=-.92;if(e.name.startsWith('Árbol de Giran'))e.position[1]=-.913;}fs.writeFileSync(file,JSON.stringify(project,null,2));console.log('Refined lawn border, grass tone and tree level.');return;}
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({viewport:{width:1600,height:1000}});await page.goto('http://127.0.0.1:32290');await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:60000});await page.selectOption('#scene','giran_city');await page.waitForFunction(()=>window.editorState?.().scene==='giran_city'&&document.body.dataset.state==='ready',null,{timeout:180000});
 const project=await page.evaluate(()=>JSON.parse(localStorage.getItem('l2-scene-editor-draft')));
 for(const e of project.objects)if(['StaticMeshActor273_0','StaticMeshActor279_0'].includes(e.node)){e.visible=false;e.name='Estatua original conservada (oculta) · '+e.node;}
 function add(name,asset,node,position,scale,rotation=[0,0,0]){project.objects.push({id:crypto.randomUUID(),name,asset,node,base:false,locked:false,visible:true,position,rotation,scale,kind:'model',parent:null,surfaces:[],parts:[]});}
 add('Jardín · césped y losas',assetId,'',[-14.68,-.951,.08],[1,1,1]);
 let index=0;for(const x of [-23.76,-5.60])for(const z of [-8.24,8.40])add('Árbol de Giran · esquina '+(++index),'l2env_0c744cbb9cf1fc','',[x,-.944,z],[.76,.82,.76],[0,index*Math.PI/2,0]);
 // Two native Gothic pillar modules reproduce the slender two-stage spire.
 add('Cohete · columna inferior','scene_giran_city','StaticMeshActor125_0',[-14.76,1.94,.11],[1.05,1.30,1.05]);
 add('Cohete · aguja superior','scene_giran_city','StaticMeshActor125_0',[-14.76,7.70,.11],[.72,1.12,.72]);
 project.name='giranmodificado1';project.reference={...project.reference,designReferences:['giran1.jpg','cohete.jpg'],notes:'Reconstrucción visual: césped, sendero de losas, cuatro árboles y aguja central. Estatua original oculta; pedestal conservado.'};
 project.camera={position:[-40,24,27],target:[-14.7,2.6,.08],fov:42};project.cameras=Array(10).fill(null);project.cameras[0]=project.camera;project.cameras[1]={position:[-32,9,19],target:[-14.76,6,.11],fov:42};project.cameras[2]={position:[-14.68,36,.09],target:[-14.68,0,.08],fov:42};
 const target=path.join(__dirname,'projects/giranmodificado1.json');if(fs.existsSync(target))throw Error('Project already exists; refusing to overwrite '+target);fs.writeFileSync(target,JSON.stringify(project,null,2));console.log(JSON.stringify({project:target,objects:project.objects.length,added:7,hidden:2}));
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1;});
