const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const root=__dirname,lab=path.resolve(root,'../..'),base='http://127.0.0.1:32290',read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const manifest=read(path.join(lab,'research/model-catalog/exports/gludio-floral-beds/manifest.json')),assign=manifest.assignments;
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],results=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().includes('favicon'))errors.push(r.status()+' '+r.url());});
 for(const name of ['gludiobrisas1','gludiobrisas1-animado']){
  const before=read(path.join(lab,'backups/gludio-arbustos-florales-20261020/research/scene-editor/projects',name+'.json')),p=read(path.join(root,'projects',name+'.json')),expected=structuredClone(before);
  for(const o of expected.objects)if(assign[o.id])o.asset=assign[o.id];assert.deepEqual(p,expected);assert.deepEqual(p,read(path.join(lab,'mapas editados',name,name+'.json')));
  const draft=structuredClone(before);draft.objects.find(o=>assign[o.id]).position[0]+=.025;draft.objects.find(o=>assign[o.id]).name='Mi arriate editado';
  await page.goto(base);await page.evaluate(({name,draft})=>{localStorage.clear();localStorage.setItem('l2-scene-editor-draft:'+name+'.json',JSON.stringify(draft));},{name,draft});
  await page.goto(base+'/?project='+name+'.json');await page.waitForFunction(n=>window.editorState?.().ready&&window.editorState().objects.length===n,p.objects.length,{timeout:120000});
  const state=await page.evaluate(()=>window.editorState()),draftExpected=structuredClone(draft);for(const o of draftExpected.objects)if(assign[o.id])o.asset=assign[o.id];assert.deepEqual(state.objects,draftExpected.objects);
  assert.equal(state.objects.filter(o=>/^custom_gludio_flower_shrub_/.test(o.asset)).length,16);assert.equal(new Set(state.objects.filter(o=>assign[o.id]).map(o=>o.asset)).size,4);
  const key='l2-scene-editor-draft:'+name+'.json:before-floral-beds-v1';assert.deepEqual(await page.evaluate(k=>JSON.parse(localStorage.getItem(k)),key),draft);
  assert.equal(state.objects.filter(o=>o.asset==='custom_gludio_brisas_carved_bench').length,2);
  if(name.endsWith('animado')){assert.equal(state.effects.emitters.length,8);await page.waitForTimeout(400);const next=await page.evaluate(()=>window.editorState());for(let i=0;i<8;i++)assert.notDeepEqual(state.effects.emitters[i].sample,next.effects.emitters[i].sample);}
  const save=await page.evaluate(async p=>{const r=await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});return {status:r.status,body:await r.json()};},p);assert.equal(save.status,201,JSON.stringify(save));
  await page.reload();await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});assert.deepEqual((await page.evaluate(()=>window.editorState())).objects,draftExpected.objects);
  await page.locator('.camera-load').nth(2).click();await page.locator('#viewport-maximize').click();await page.waitForTimeout(500);await page.screenshot({path:path.join(lab,'mapas editados',name,'arriates-florales-general.jpg'),type:'jpeg',quality:92});
  await page.evaluate(()=>localStorage.clear());await page.route('**/api/projects/'+name+'.json',route=>route.fulfill({json:{...p,camera:{position:[5.2,2.08,3.6],target:[3.45,1.78,1.55],fov:40}}}));await page.reload();await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});await page.locator('#viewport-maximize').click();await page.waitForTimeout(500);await page.screenshot({path:path.join(lab,'mapas editados',name,'arriates-florales-detalle.jpg'),type:'jpeg',quality:93});await page.unroute('**/api/projects/'+name+'.json');
  results.push({name,only16BedInstancesChanged:true,variants:4,otherPlantsAndBenchesPreserved:true,oldDraftMigrated:true,userEditsPreserved:true,backup:true,save:save.body.saved,reload:true,effects:state.effects.emitters.length});
 }
 await page.route('**/thumbnail-render.js',route=>route.fulfill({contentType:'text/javascript',body:`
  import * as T from 'three';import {GLTFLoader} from '/assets/vendor/addons/loaders/GLTFLoader.js';
  document.documentElement.style.cssText='width:1000px;height:900px';document.body.style.cssText='margin:0;width:1000px;height:900px';const r=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setSize(1000,900);r.outputColorSpace=T.SRGBColorSpace;r.setClearColor('#29302b');document.body.append(r.domElement);
  const s=new T.Scene();s.add(new T.HemisphereLight(0xfffaf0,0x6c7b6c,2.1));const l=new T.DirectionalLight(0xffefda,2.8);l.position.set(2,4,3);s.add(l);
  const model=await new GLTFLoader().loadAsync('/assets/exports/gludio-floral-beds/mixed-0.gltf');s.add(model.scene);const c=new T.PerspectiveCamera(36,1000/900,.001,10);c.position.set(.35,.34,.47);c.lookAt(0,.09,0);r.render(s,c);document.body.dataset.ready='true';
 `}));await page.setViewportSize({width:1000,height:900});await page.goto(base+'/thumbnail-render.html?asset=exports/gludio-floral-beds/mixed-0.gltf');await page.waitForFunction(()=>document.body.dataset.ready==='true');await page.screenshot({path:path.join(lab,'mapas editados/gludiobrisas1-animado/mata-floral-diseno.jpg'),type:'jpeg',quality:95});
 assert.deepEqual(errors,[]);const report={passed:true,results,errors};fs.writeFileSync(path.join(root,'gludio-floral-beds-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
