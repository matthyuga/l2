const fs=require('fs'),path=require('path'),crypto=require('crypto'),{pathToFileURL}=require('url');
const root=path.resolve(__dirname,'../..'),editor=path.join(root,'research/scene-editor'),catalog=path.join(root,'research/model-catalog'),folder=path.join(catalog,'exports/aurelia-vip1'),projectFile=path.join(editor,'projects/aureliavip1.json');
if(fs.existsSync(projectFile)&&!process.argv.includes('--rebuild'))throw Error('Project exists: use --rebuild only before user edits.');
(async()=>{const T=await import(pathToFileURL(path.join(catalog,'vendor/three.module.js')).href),g=JSON.parse(fs.readFileSync(path.join(folder,'aurelia.gltf'))),manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'design-manifest.json'))),id='custom_aurelia_vip1';
const camera=(position,target,fov=48)=>({position,target,fov}),cameras=[
 camera([-89,85,94],[0,16,0],42),camera([-29,27,11],[4,18.7,0],54),camera([21,23.6,0],[36,19.5,0],56),
 camera([-34,13,7.2],[-25,11.8,13],64),camera([-8,13,6.6],[2,11.8,12.7],68),camera([-32,13,-6.5],[-25,11.8,-13],65),
 camera([-9.9,8,-7],[-13,6.7,-10],70),camera([8.8,7.8,-8.0],[14,6.7,-12.3],65),camera([5,8.8,1],[16.5,6.4,0],62),camera([-10,9,1],[0,5.5,0],62)
];
function bounds(index,parent=new T.Matrix4()){
 const n=g.nodes[index],local=n.matrix?new T.Matrix4().fromArray(n.matrix):new T.Matrix4().compose(new T.Vector3(...n.translation||[0,0,0]),new T.Quaternion(...n.rotation||[0,0,0,1]),new T.Vector3(...n.scale||[1,1,1])),world=parent.clone().multiply(local),box=new T.Box3();
 if(n.mesh!==undefined)for(const p of g.meshes[n.mesh].primitives){const a=g.accessors[p.attributes.POSITION];box.union(new T.Box3(new T.Vector3(...a.min),new T.Vector3(...a.max)).applyMatrix4(world));}
 for(const child of n.children||[])box.union(bounds(child,world));return box;
}
const asset={id,title:'Aurelia · Aeronave VIP con interiores',path:'exports/aurelia-vip1/aurelia.gltf',thumbnail:'thumbs/aurelia-vip1.png',mesh:'Aurelia.VIP1',category:'Escenarios',native:false,batch:'Proyectos personales · Aurelia'};
const dataPath=path.join(editor,'data.json'),data=JSON.parse(fs.readFileSync(dataPath));data.assets=data.assets.filter(a=>a.id!==id);data.assets.push(asset);data.scenes=data.scenes.filter(s=>s.id!=='aurelia_vip');data.scenes.push({id:'aurelia_vip',title:'Aurelia · Club VIP',asset:id,source:'Diseño VIP de Aurelia: cubierta de eventos, dos pisos interiores y mirador de cristal.',initialCamera:cameras[0]});fs.writeFileSync(dataPath,JSON.stringify(data,null,2));
const galleryPath=path.join(catalog,'gallery.json'),gallery=JSON.parse(fs.readFileSync(galleryPath));gallery.models=gallery.models.filter(a=>a.key!==id);gallery.models.push({key:id,title:asset.title,gltf:asset.path,thumbnail:asset.thumbnail,mesh:asset.mesh,package:'Aurelia VIP1',category:'Escenarios',native:false,batch:asset.batch,status:'ready',names:[],types:['StaticMesh']});fs.writeFileSync(galleryPath,JSON.stringify(gallery,null,2));
const project={format:'l2-scene-editor-v1',name:'aureliavip1',scene:'aurelia_vip',reference:{...data.reference,design:'Aurelia · Private Club',source:'research/aurelia-vip1/Aurelia-VIP1.blend'},objects:[],camera:cameras[0],cameras};
const parentIds={},entries=[];
function meta(name,kind,position,parent=null){return {id:crypto.randomUUID(),name,asset:id,node:'',base:kind==='model',kind,parent,locked:false,visible:true,position,rotation:[0,0,0],scale:[1,1,1],surfaces:[],parts:[]};}
for(const [deck,name]of Object.entries({exterior:'01 · Casco, arco y motores',superior:'02 · Piscina, fiestas y Sky Bar',conexion:'03 · Conexiones entre cubiertas',A:'04 · Cubierta A · Club privado',B:'05 · Cubierta B · Invitados y deportes'})){const e=meta(name,'group',[0,0,0]);parentIds[deck]=e.id;project.objects.push(e);}
for(const item of manifest.zones){const index=g.nodes.findIndex(n=>n.name===item.node);if(index<0)throw Error('Missing zone '+item.node);const box=bounds(index),e=meta(item.title,'model',box.getCenter(new T.Vector3()).toArray(),parentIds[item.deck]);e.node=item.node;project.objects.push(e);entries.push({id:e.id,node:e.node,deck:item.deck,bounds:{min:box.min.toArray(),max:box.max.toArray()}});}
const pool=meta('Piscina · ondas, cascadas y espuma','effect',[0,17.72,0],parentIds.superior);pool.base=false;pool.effect={type:'pool',seed:614,count:120,color:'#147f91',radius:18.8,height:1.5,speed:.8};project.objects.push(pool);
function write(name,p){const text=JSON.stringify(p,null,2),target=path.join(editor,'projects',name+'.json'),delivery=path.join(root,'mapas editados',name);fs.mkdirSync(delivery,{recursive:true});fs.writeFileSync(target,text);fs.writeFileSync(path.join(delivery,name+'.json'),text);}
write('aureliavip1',project);
for(const [deck,name]of [['A','aureliavip1-social'],['B','aureliavip1-invitados']]){const copy=structuredClone(project);copy.name=name;for(const e of copy.objects){const info=entries.find(a=>a.id===e.id);if(info&&(!([deck,'conexion'].includes(info.deck))||info.node.includes('Techos')))e.visible=false;if(e.kind==='effect')e.visible=false;}copy.camera=camera([0,deck==='A'?77:65,45],[0,deck==='A'?10.5:5.5,0],46);copy.cameras[0]=copy.camera;copy.cameras[1]=camera([0,deck==='A'?105:88,.01],[0,deck==='A'?10.5:5.5,0],42);write(name,copy);}
fs.writeFileSync(path.join(__dirname,'project-manifest.json'),JSON.stringify({asset:id,objects:project.objects.length,entries},null,2));console.log({objects:project.objects.length,zones:entries.length,projects:['aureliavip1','aureliavip1-social','aureliavip1-invitados']});
})().catch(e=>{console.error(e);process.exitCode=1});
