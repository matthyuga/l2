const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const root=path.resolve(__dirname,'../..'),editor=path.join(root,'research/scene-editor'),cat=path.join(root,'research/model-catalog'),id='custom_vigilia_estructura';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>fs.writeFileSync(f,JSON.stringify(v,null,2));
(async()=>{const T=await import(pathToFileURL(path.join(cat,'vendor/three.module.js')).href),g=read(path.join(cat,'exports/vigilia-estructura/estructura.gltf'));
 const backup=path.join(root,'backups/vigilia-estructura-20261020');for(const file of [path.join(editor,'data.json'),path.join(editor,'custom-assets.json'),path.join(cat,'gallery.json')]){const target=path.join(backup,path.relative(root,file));fs.mkdirSync(path.dirname(target),{recursive:true});if(!fs.existsSync(target))fs.copyFileSync(file,target);}
 const asset={id,title:'Vigilia - casco y techo corregidos',path:'exports/vigilia-estructura/estructura.gltf',thumbnail:null,mesh:'Vigilia.Turbinas',category:'Escenarios',native:false,batch:'Proyectos personales - Vigilia'};
 for(const file of [path.join(editor,'data.json'),path.join(editor,'custom-assets.json')]){const v=read(file),list=Array.isArray(v)?v:v.assets,index=list.findIndex(a=>a.id===id);if(index>=0)list[index]=asset;else list.push(asset);write(file,v);}
 const galleryFile=path.join(cat,'gallery.json'),gallery=read(galleryFile);gallery.models=gallery.models.filter(a=>a.key!==id);gallery.models.push({key:id,title:asset.title,gltf:asset.path,thumbnail:null,mesh:asset.mesh,category:asset.category,batch:asset.batch,native:false,status:'ready',names:[],types:['StaticMesh']});write(galleryFile,gallery);
 function bounds(index,parent=new T.Matrix4()){const n=g.nodes[index],local=n.matrix?new T.Matrix4().fromArray(n.matrix):new T.Matrix4().compose(new T.Vector3(...n.translation||[0,0,0]),new T.Quaternion(...n.rotation||[0,0,0,1]),new T.Vector3(...n.scale||[1,1,1])),world=parent.clone().multiply(local),box=new T.Box3();if(n.mesh!==undefined)for(const p of g.meshes[n.mesh].primitives){const a=g.accessors[p.attributes.POSITION];box.union(new T.Box3(new T.Vector3(...a.min),new T.Vector3(...a.max)).applyMatrix4(world));}for(const child of n.children||[])box.union(bounds(child,world));return box;}
 const p=read(path.join(editor,'projects/vigiliaturbinas1.json'));p.name='vigiliaturbinas2';p.reference={...p.reference,structure:'Closed hull tips and continuous roof landing',source:'research/vigilia-ajustes-estructura/Vigilia-estructura.blend'};
 let hull;
 for(const node of ['VIG_00_Casco','VIG_05_Techo','VIG_15_Azotea']){const o=p.objects.find(o=>o.node===node);o.asset=id;o.position=bounds(g.nodes.findIndex(n=>n.name===node)).getCenter(new T.Vector3()).toArray();if(node==='VIG_00_Casco')hull=o;}
 p.cameras[4]={position:[-22,3.8,7],target:[-14.3,2.8,0],fov:40};
 p.cameras[5]={position:[-16.6,9.4,-6.6],target:[-11.9,6.1,-.3],fov:38};
 for(const [name,project] of [['vigiliaturbinas2',p],['vigiliaturbinas2-escala',{...structuredClone(p),name:'vigiliaturbinas2-escala'}]]){
  if(name.endsWith('escala')){for(const o of project.objects)if(o.node==='VIG_01_Globo')o.visible=false;else if(o.node==='VIG_13_Escala')o.visible=true;}
  const folder=path.join(root,'mapas editados',name);fs.mkdirSync(folder,{recursive:true});const file=path.join(editor,'projects',name+'.json');
  if(fs.existsSync(file)&&!process.argv.includes('--rebuild'))throw Error('New project already exists. Preserve user edits.');write(file,project);write(path.join(folder,name+'.json'),project);
 }
 write(path.join(__dirname,'project-registration.json'),{name:p.name,objects:p.objects.length,hullCenter:hull.position,headCenter:p.objects.at(-1).position,asset});console.log({name:p.name,objects:p.objects.length,headCenter:p.objects.at(-1).position});
})().catch(e=>{console.error(e);process.exitCode=1;});
