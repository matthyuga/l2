'use strict';
const http=require('http'),fs=require('fs'),path=require('path'),{execFile}=require('child_process');
const root=__dirname, port=Number(process.env.L2_MODEL_PORT||32280);
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.gltf':'model/gltf+json','.glb':'model/gltf-binary','.bin':'application/octet-stream'};
let catalog=null,mtime=0;
function getCatalog(){const file=path.join(root,'gallery.json'),stamp=fs.statSync(file).mtimeMs;
 if(!catalog||stamp!==mtime){catalog=JSON.parse(fs.readFileSync(file,'utf8'));mtime=stamp;}
 return {...catalog,models:catalog.models.map(m=>({...m,batch:m.batch||'Tanda original',has_thumbnail:!!m.thumbnail&&fs.existsSync(path.join(root,m.thumbnail))}))};}
function json(res,status,data){res.writeHead(status,{'Content-Type':mime['.json'],'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(JSON.stringify(data));}
const server=http.createServer(async(req,res)=>{try{
 const url=new URL(req.url,'http://127.0.0.1:'+port);
 if(req.method==='GET'&&url.pathname==='/api/status'){const c=getCatalog();return json(res,200,{app:'l2-model-gallery',model_count:c.models.length,thumbnails:c.models.filter(m=>m.has_thumbnail).length,port});}
 if(req.method==='GET'&&url.pathname==='/api/catalog')return json(res,200,getCatalog());
 if(req.method==='POST'&&url.pathname==='/api/viewer'){
  if(req.headers.origin!=='http://127.0.0.1:'+port)return json(res,403,{error:'Origen no permitido.'});
  let body='';for await(const chunk of req){body+=chunk;if(body.length>1024)return json(res,413,{error:'Solicitud demasiado grande.'});}
  let data;try{data=JSON.parse(body);}catch{return json(res,400,{error:'Solicitud inválida.'});}
  const model=getCatalog().models.find(m=>m.key===data.key);
  if(!model||model.status!=='ready')return json(res,400,{error:'Modelo no disponible en este cliente.'});
  const [pkg,...parts]=(model.viewer_mesh||model.mesh).split('.'),mesh=parts.join('.');
  if(!/^[A-Za-z0-9_-]+$/.test(pkg)||!/^[A-Za-z0-9_.-]+$/.test(mesh))return json(res,400,{error:'Nombre de modelo inválido.'});
  execFile('powershell.exe',['-NoProfile','-ExecutionPolicy','Bypass','-File',path.join(root,'Open-L2Models.ps1'),'-Package',pkg,'-Mesh',mesh,...(model.asset_root?['-AssetRoot',model.asset_root,'-Extension',model.viewer_extension||'ukx']:[])],{windowsHide:true,timeout:30000},(error,stdout,stderr)=>{
   if(error)return json(res,500,{error:(stderr||error.message).slice(-1200)});
   json(res,200,{ok:true,message:'El visor con animaciones se está abriendo.'});
  });return;
 }
 if(req.method!=='GET'&&req.method!=='HEAD')return json(res,405,{error:'Método no permitido.'});
 const name=decodeURIComponent(url.pathname==='/'?'/gallery.html':url.pathname);
 const file=path.resolve(root,'.'+name);
 if(!file.startsWith(root+path.sep)||!mime[path.extname(file)]||!fs.existsSync(file)||!fs.statSync(file).isFile())return json(res,404,{error:'Archivo no disponible.'});
 res.writeHead(200,{'Content-Type':mime[path.extname(file)],'Cache-Control':path.extname(file)==='.html'?'no-store':'public, max-age=60','X-Content-Type-Options':'nosniff'});
 if(req.method==='HEAD')return res.end();fs.createReadStream(file).on('error',()=>res.destroy()).pipe(res);
 }catch(error){console.error(error);if(!res.headersSent)json(res,500,{error:'No se pudo cargar el catálogo.'});else res.destroy();}});
server.listen(port,'127.0.0.1',()=>console.log('Galería L2 en http://127.0.0.1:'+port));
server.on('error',e=>{console.error(e.message);process.exitCode=1;});
