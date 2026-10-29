const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=__dirname,lab=path.resolve(root,'../..'),base='http://127.0.0.1:32290';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],results=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().includes('favicon'))errors.push(r.status()+' '+r.url());});
  for(const name of ['gludiobrisas1','gludiobrisas1-animado']){
   const file=path.join(root,'projects',name+'.json'),p=read(file),before=read(path.join(lab,'backups/gludio-flores-20261020/research/scene-editor/projects',name+'.json'));
   const expected=structuredClone(before);for(const o of expected.objects){if(o.asset==='web_kenney_nature_flower_purplea')o.asset='custom_gludio_cosmos_lavender';if(o.asset==='web_kenney_nature_flower_yellowa')o.asset='custom_gludio_cosmos_ivory';}assert.deepEqual(p,expected);
   assert.deepEqual(p,read(path.join(lab,'mapas editados',name,name+'.json')));
   await page.goto(base+'/?project='+name+'.json');await page.waitForFunction(n=>window.editorState?.().ready&&window.editorState().objects.length===n,p.objects.length,{timeout:120000});
   const state=await page.evaluate(()=>window.editorState());assert.equal(state.objects.filter(o=>o.asset.startsWith('custom_gludio_cosmos_')).length,66);
   const dest=path.join(lab,'mapas editados',name);
   await page.locator('#viewport-maximize').click();await page.waitForTimeout(600);await page.screenshot({path:path.join(dest,'flores-general.jpg'),type:'jpeg',quality:85});
   if(name.endsWith('animado')){assert.equal(state.effects.emitters.length,8);await page.waitForTimeout(500);const later=await page.evaluate(()=>window.editorState());for(let i=0;i<8;i++)assert.notDeepEqual(state.effects.emitters[i].sample,later.effects.emitters[i].sample);}
   const save=await page.evaluate(async p=>{const r=await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});return {status:r.status,body:await r.json()};},p);assert.equal(save.status,201,JSON.stringify(save));
   await page.reload();await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});assert.equal((await page.evaluate(()=>window.editorState())).objects.filter(o=>o.asset.startsWith('custom_gludio_cosmos_')).length,66);
   // Override the camera only in this test response to inspect planter-scale detail.
   const plant=p.objects.find(o=>o.name==='Flores de las Brisas');const [x,y,z]=plant.position;
   await page.route('**/api/projects/'+name+'.json',route=>route.fulfill({json:{...p,camera:{position:[x+1.5,y+1.0,z+1.5],target:[x,y+.22,z],fov:38}}}));
   // Fresh context has no saved browser draft to mask the test camera.
   await page.evaluate(()=>localStorage.clear());await page.reload();await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});await page.locator('#viewport-maximize').click();await page.waitForTimeout(650);await page.screenshot({path:path.join(dest,'flores-detalle.jpg'),type:'jpeg',quality:92});await page.unroute('**/api/projects/'+name+'.json');
   results.push({name,flowers:66,unchangedExceptAsset:true,loadReload:true,save:save.body.saved,effects:state.effects.emitters.length});
  }
  // Standalone asset portrait, also used as the catalog thumbnail.
  await page.route('**/thumbnail-render.js',route=>route.fulfill({contentType:'text/javascript',body:`
   import * as T from 'three';import {GLTFLoader} from '/assets/vendor/addons/loaders/GLTFLoader.js';
   document.documentElement.style.cssText='width:800px;height:800px';document.body.style.cssText='margin:0;width:800px;height:800px';const r=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setSize(800,800);r.setPixelRatio(1);r.outputColorSpace=T.SRGBColorSpace;r.setClearColor('#252c29');document.body.append(r.domElement);
   const s=new T.Scene();s.add(new T.HemisphereLight(0xfff8ef,0x77816e,2));const l=new T.DirectionalLight(0xfff3dc,2.6);l.position.set(2,4,3);s.add(l);
   const file=new URLSearchParams(location.search).get('asset'),model=await new GLTFLoader().loadAsync('/assets/'+file);s.add(model.scene);const c=new T.PerspectiveCamera(35,1,.001,10);c.position.set(.29,.34,.39);c.lookAt(0,.11,0);r.render(s,c);document.body.dataset.ready='true';
  `}));
  for(const variant of ['lavender','ivory']){await page.setViewportSize({width:800,height:800});await page.goto(base+'/thumbnail-render.html?asset=exports/gludio-botanical/'+variant+'.gltf');await page.waitForFunction(()=>document.body.dataset.ready==='true');await page.screenshot({path:path.join(lab,'research/model-catalog/thumbs/custom_gludio_cosmos_'+variant+'.png')});}
  assert.deepEqual(errors,[]);const report={passed:true,projects:results,errors};fs.writeFileSync(path.join(root,'gludio-flowers-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
