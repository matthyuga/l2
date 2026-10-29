const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const root=__dirname,lab=path.resolve(root,'../..'),base='http://127.0.0.1:32290',asset='custom_gludio_brisas_carved_bench';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],results=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().includes('favicon'))errors.push(r.status()+' '+r.url());});
 for(const name of ['gludiobrisas1','gludiobrisas1-animado']){
  const before=read(path.join(lab,'backups/gludio-bancos-pergolas-20261020/research/scene-editor/projects',name+'.json')),p=read(path.join(root,'projects',name+'.json'));
  const ids=['dfe8dd19-a1f3-4074-868e-304f82c21dcc','134fd162-e6e5-49e6-aa0b-8150524a94d0'],expected=structuredClone(before);for(const o of expected.objects)if(ids.includes(o.id))o.asset=asset;assert.deepEqual(p,expected);assert.deepEqual(p,read(path.join(lab,'mapas editados',name,name+'.json')));
  // Restore a user's old browser draft, keeping their moved bench and rename.
  const draft=structuredClone(before);draft.objects.find(o=>o.id===ids[0]).position[0]+=.03;draft.objects.find(o=>o.id===ids[0]).name='Mi banco';
  await page.goto(base);await page.evaluate(({name,draft})=>{localStorage.clear();localStorage.setItem('l2-scene-editor-draft:'+name+'.json',JSON.stringify(draft));},{name,draft});
  await page.goto(base+'/?project='+name+'.json');await page.waitForFunction(n=>window.editorState?.().ready&&window.editorState().objects.length===n,p.objects.length,{timeout:120000});
  const state=await page.evaluate(()=>window.editorState()),draftExpected=structuredClone(draft);for(const o of draftExpected.objects)if(ids.includes(o.id))o.asset=asset;assert.deepEqual(state.objects,draftExpected.objects);assert.equal(state.objects.filter(o=>o.asset===asset).length,2);assert.equal(state.objects.filter(o=>o.node==='Banco'&&o.asset==='custom_gludio_brisas_decor').length,4);
  const key='l2-scene-editor-draft:'+name+'.json:before-carved-benches-v1';assert.deepEqual(await page.evaluate(k=>JSON.parse(localStorage.getItem(k)),key),draft);
  if(name.endsWith('animado')){assert.equal(state.effects.emitters.length,8);await page.waitForTimeout(350);const later=await page.evaluate(()=>window.editorState());for(let i=0;i<8;i++)assert.notDeepEqual(state.effects.emitters[i].sample,later.effects.emitters[i].sample);}
  const save=await page.evaluate(async p=>{const r=await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});return {status:r.status,body:await r.json()};},p);assert.equal(save.status,201,JSON.stringify(save));
  await page.reload();await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});assert.deepEqual((await page.evaluate(()=>window.editorState())).objects,draftExpected.objects);
  await page.evaluate(()=>localStorage.clear());await page.route('**/api/projects/'+name+'.json',route=>route.fulfill({json:{...p,camera:{position:[-10.8,2.35,-.75],target:[-12,1.45,-4.15],fov:40}}}));await page.reload();await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});await page.locator('#viewport-maximize').click();await page.waitForTimeout(650);await page.screenshot({path:path.join(lab,'mapas editados',name,'banco-pergola-detalle.jpg'),type:'jpeg',quality:93});await page.unroute('**/api/projects/'+name+'.json');
  results.push({name,onlyTwoBenchesChanged:true,otherFourPreserved:true,oldDraftUpdated:true,userEditsPreserved:true,backup:true,save:save.body.saved,reload:true,effects:state.effects.emitters.length});
 }
 await page.route('**/thumbnail-render.js',route=>route.fulfill({contentType:'text/javascript',body:`
  import * as T from 'three';import {GLTFLoader} from '/assets/vendor/addons/loaders/GLTFLoader.js';
  document.documentElement.style.cssText='width:1200px;height:900px';document.body.style.cssText='margin:0;width:1200px;height:900px';
  const r=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setSize(1200,900);r.outputColorSpace=T.SRGBColorSpace;r.setClearColor('#252b2d');document.body.append(r.domElement);
  const s=new T.Scene();s.add(new T.HemisphereLight(0xfff8ee,0x637580,2.3));const l=new T.DirectionalLight(0xffe3b5,3.2);l.position.set(2,4,4);s.add(l);const fill=new T.DirectionalLight(0xbce7ff,1.2);fill.position.set(-3,2,-1);s.add(fill);
  const model=await new GLTFLoader().loadAsync('/assets/exports/gludio-carved-bench/bench.gltf');s.add(model.scene);
  const floor=new T.Mesh(new T.PlaneGeometry(200,200),new T.MeshStandardMaterial({color:'#30383b',roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.012;s.add(floor);
  const c=new T.PerspectiveCamera(36,1200/900,.01,100);c.position.set(2.8,2.05,3.9);c.lookAt(0,.73,0);r.render(s,c);document.body.dataset.ready='true';
 `}));
 await page.setViewportSize({width:1200,height:900});await page.goto(base+'/thumbnail-render.html?asset=exports/gludio-carved-bench/bench.gltf');await page.waitForFunction(()=>document.body.dataset.ready==='true');await page.screenshot({path:path.join(lab,'mapas editados/gludiobrisas1-animado/banco-tallado-diseno.jpg'),type:'jpeg',quality:95});
 assert.deepEqual(errors,[]);const report={passed:true,results,errors};fs.writeFileSync(path.join(root,'gludio-carved-bench-verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
