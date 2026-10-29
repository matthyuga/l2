'use strict';
const http=require('http'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname, gallery=path.resolve(root,'../model-catalog'),port=Number(process.env.L2_SCENE_EDITOR_PORT||32290);
const data=JSON.parse(fs.readFileSync(path.join(root,'data.json'),'utf8'));
const assetIds=new Set(data.assets.map(a=>a.id));
const textureCatalog=require('./texture-catalog.cjs');
const atmosphereCatalog=require('./atmosphere-catalog.cjs');
const {validAtmosphere}=require('./atmosphere-schema.js');
let atmosphereBuild=null,atmosphereBuildError=null;
const {validStructure}=require('./structure-schema.js');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gltf':'model/gltf+json','.glb':'model/gltf-binary','.bin':'application/octet-stream'};
function validCamera(v){return !!v&&[v.position,v.target].every(a=>Array.isArray(a)&&a.length===3&&a.every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<1e7))&&Number.isFinite(v.fov)&&v.fov>=5&&v.fov<=150&&v.position.some((n,i)=>Math.abs(n-v.target[i])>1e-6);}
function validProject(p){
 const surfaceIds=new Set(['grass','soil','sand','l2_center_kserth_medallion','l2_center_kserth_rosette','l2_center_kserth_inlay',...textureCatalog().map(t=>t.id)]);
 if(!p||p.format!=='l2-scene-editor-v1'||!Array.isArray(p.objects)||p.objects.length>4000||!data.scenes.some(s=>s.id===p.scene))return false;
 if(!validAtmosphere(p.atmosphere,atmosphereCatalog().items))return false;
 if(p.camera!==undefined&&!validCamera(p.camera))return false;
 if(p.cameras!==undefined&&(!Array.isArray(p.cameras)||p.cameras.length!==10||p.cameras.some(v=>v!==null&&!validCamera(v))))return false;
 const validSurfaces=value=>value===undefined||(Array.isArray(value)&&value.length<=100&&value.every(v=>v&&typeof v.slot==='string'&&v.slot.length<=200&&surfaceIds.has(v.texture)&&['replace','layer'].includes(v.mode)&&Number.isFinite(v.repeat)&&v.repeat>=.1&&v.repeat<=100&&Number.isFinite(v.opacity)&&v.opacity>=.05&&v.opacity<=1)&&new Set(value.map(v=>v.slot)).size===value.length);
 return validStructure(p.objects,{assetIds,validSurfaces});
}
function json(res,status,obj){res.writeHead(status,{'Content-Type':mime['.json'],'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(obj));}
const server=http.createServer(async(req,res)=>{try{
 const u=new URL(req.url,'http://127.0.0.1:'+port);
 if(req.method==='GET'&&u.pathname==='/api/status')return json(res,200,{app:'l2-scene-editor',assets:data.assets.length,port});
 if(req.method==='GET'&&u.pathname==='/api/texture-progress')return json(res,200,textureCatalog.progress());
 if(req.method==='GET'&&u.pathname==='/api/textures')return json(res,200,textureCatalog());
 if(req.method==='GET'&&u.pathname==='/api/data')return json(res,200,data);
 if(req.method==='GET'&&u.pathname==='/api/atmosphere')return json(res,200,{...atmosphereCatalog(),building:!!atmosphereBuild,buildError:atmosphereBuildError});
 if(req.method==='POST'&&u.pathname==='/api/atmosphere/refresh'){
  if(req.headers.origin!=='http://127.0.0.1:'+port)return json(res,403,{error:'Origen no permitido.'});
  if(!atmosphereBuild){
   atmosphereBuildError=null;
   const log=fs.openSync(path.join(atmosphereCatalog.root,'preview-build.log'),'a');
   atmosphereBuild=require('child_process').spawn('python',['-u',path.join(atmosphereCatalog.root,'build-preview.py')],{windowsHide:true,stdio:['ignore',log,log]});fs.closeSync(log);
   atmosphereBuild.on('error',e=>{atmosphereBuildError=e.message;atmosphereBuild=null;});
   atmosphereBuild.on('close',code=>{if(code)atmosphereBuildError='No se completó la actualización; revisar preview-build.log.';atmosphereBuild=null;});
  }
  return json(res,202,{building:true});
 }
 if((req.method==='GET'||req.method==='HEAD')&&u.pathname.startsWith('/atmosphere/')){
  const allowed=new Set(atmosphereCatalog().items.flatMap(i=>[i.url,i.thumbnail].filter(Boolean)));
  if(!allowed.has(u.pathname)||!/^\/atmosphere\/[a-f0-9]{20}(-thumb)?\.(jpg|png|wav)$/.test(u.pathname))return json(res,404,{error:'Recurso no disponible.'});
  const file=path.join(atmosphereCatalog.root,'preview',path.basename(u.pathname));
  if(!fs.existsSync(file))return json(res,404,{error:'Vista previa no disponible.'});
  const size=fs.statSync(file).size,type=file.endsWith('.wav')?'audio/wav':file.endsWith('.png')?'image/png':'image/jpeg';
  let start=0,end=size-1,status=200;
  if(req.headers.range){const match=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);if(!match||Number(match[1])>=size){res.writeHead(416,{'Content-Range':'bytes */'+size});return res.end();}start=Number(match[1]);end=match[2]?Math.min(Number(match[2]),end):end;if(end<start){res.writeHead(416);return res.end();}status=206;}
  res.writeHead(status,{'Content-Type':type,'Content-Length':end-start+1,'Accept-Ranges':'bytes','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff',...(status===206?{'Content-Range':`bytes ${start}-${end}/${size}`}:{})});
  if(req.method==='HEAD')return res.end();return fs.createReadStream(file,{start,end}).on('error',()=>res.destroy()).pipe(res);
 }
 if(req.method==='GET'&&u.pathname.startsWith('/api/projects/')){
  const name=u.pathname.slice('/api/projects/'.length);
  if(!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}\.json$/.test(name))return json(res,400,{error:'Nombre de proyecto inválido.'});
  const file=path.join(root,'projects',name);
  if(!fs.existsSync(file)||!fs.statSync(file).isFile())return json(res,404,{error:'Proyecto no encontrado.'});
  if(fs.statSync(file).size>3e6)return json(res,413,{error:'Proyecto demasiado grande.'});
  return json(res,200,JSON.parse(fs.readFileSync(file,'utf8')));
 }
 if(req.method==='POST'&&u.pathname==='/api/projects'){
  if(req.headers.origin!=='http://127.0.0.1:'+port)return json(res,403,{error:'Origen no permitido.'});
  let body='';for await(const c of req){body+=c;if(body.length>3e6)return json(res,413,{error:'Proyecto demasiado grande.'});}
  let project;try{project=JSON.parse(body);}catch{return json(res,400,{error:'JSON inválido.'});}
  if(!validProject(project))return json(res,400,{error:'Proyecto o transformaciones inválidas.'});
  const name=new Date().toISOString().replace(/[:.]/g,'-')+'-'+crypto.randomBytes(3).toString('hex')+'.json';
  fs.mkdirSync(path.join(root,'projects'),{recursive:true});fs.writeFileSync(path.join(root,'projects',name),JSON.stringify(project,null,2),{flag:'wx'});
  return json(res,201,{saved:name});
 }
 if(req.method!=='GET'&&req.method!=='HEAD')return json(res,405,{error:'Método no permitido.'});
 let base=root,name=decodeURIComponent(u.pathname);
 if(name.startsWith('/assets/')){base=gallery;name=name.slice(7);if(!/^\/(exports|thumbs|vendor)\//.test(name))return json(res,404,{error:'Recurso no disponible.'});}
 if(name==='/')name='/index.html';
 if(base===root&&!/^\/(index\.html|app\.js|style\.css|atmosphere(-schema)?\.js|atmosphere\.css|lock-controls\.js|model-motion\.js|sidebar-ui\.js|selection-highlights\.js|scene-tree\.js|merge-meshes\.js|structure-schema\.js|effect-schema\.js|scene-effects\.js|workspace\.css|panel-layout\.(js|css)|surfaces\.(js|css)|asset-library\.(js|css)|studio-controls\.css|studio-navigation\.js|camera-slots\.js|thumbnail-render\.(html|js)|vendor\/(TransformControls|SkeletonUtils)\.js)$/.test(name))return json(res,404,{error:'Recurso no disponible.'});
 const file=path.resolve(base,'.'+name),ext=path.extname(file);
 if(!file.startsWith(base+path.sep)||!mime[ext]||!fs.existsSync(file)||!fs.statSync(file).isFile())return json(res,404,{error:'Archivo no disponible.'});
 res.writeHead(200,{'Content-Type':mime[ext],'X-Content-Type-Options':'nosniff','Cache-Control':'no-cache'});if(req.method==='HEAD')return res.end();fs.createReadStream(file).on('error',()=>res.destroy()).pipe(res);
 }catch(e){console.error(e);if(!res.headersSent)json(res,500,{error:'No se pudo completar la operación.'});else res.destroy();}});
server.listen(port,'127.0.0.1',()=>console.log('Editor L2: http://127.0.0.1:'+port));
server.on('error',e=>{console.error(e);process.exitCode=1;});
