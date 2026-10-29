const {chromium}=require('E:/l2-local/tools/rea-runtime/node_modules/playwright-core');
const fs=require('node:fs'),assert=require('node:assert/strict');
const out=__dirname,origin='http://127.0.0.1:32280';
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1100}}),page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto(origin+'/?batch='+encodeURIComponent('Assets externos · Tanda 3'));await page.waitForFunction(()=>document.querySelector('#grid .card'));
  const models=(await (await context.request.get(origin+'/api/catalog')).json()).models,external=models.filter(m=>m.external_asset&&m.status==='ready');
  assert(external.length>0);assert.equal(await page.locator('#batch').inputValue(),'Assets externos · Tanda 3');
  await page.screenshot({path:out+'/catalogo.png',fullPage:false});
  const animated=external.find(m=>m.asset_analysis.animations>0);assert(animated);
  await page.goto(origin+'/?model='+animated.key+'&view=3d');await page.waitForFunction(()=>document.querySelector('#view3d canvas')&&!document.querySelector('#viewstatus').textContent,{timeout:90000});
  assert.equal(await page.locator('#native').isDisabled(),true);assert.match(await page.locator('#assetSource').innerText(),/Autor:|Licencia/);
  const select=page.locator('.modelAnimationControls select');await select.selectOption('0');await page.waitForTimeout(300);await page.locator('.modelAnimationControls button').click();assert.equal(await page.locator('.modelAnimationControls button').innerText(),'Reanudar');
  await page.locator('#planningName').fill('Prueba externa');await page.locator('#planningTagInput').fill('externo, capitán');await page.locator('#saveFavorite').click();
  let choice=await page.evaluate(key=>JSON.parse(localStorage.getItem('l2-model-choices'))[key],animated.key);assert.equal(choice.planning.name,'Prueba externa');assert.equal(choice.npc_id,null);
  await page.locator('#visual').scrollIntoViewIfNeeded();await page.screenshot({path:out+'/ficha-animada.png'});await page.locator('#close').click();
  // Load every new GLB in Three.js and release resources after each import.
  const loaded=await page.evaluate(async entries=>{
   const {GLTFLoader}=await import('/vendor/addons/loaders/GLTFLoader.js'),results=[];
   for(const m of entries){try{const gltf=await new GLTFLoader().loadAsync(m.gltf);let meshes=0;gltf.scene.traverse(o=>{if(o.isMesh)meshes++;});if(!meshes)throw Error('No meshes');results.push({key:m.key,meshes,animations:gltf.animations.length});gltf.scene.traverse(o=>{o.geometry?.dispose();for(const mat of o.material?Array.isArray(o.material)?o.material:[o.material]:[]){for(const value of Object.values(mat))if(value?.isTexture)value.dispose();mat.dispose();}});}catch(e){results.push({key:m.key,error:e.message});}}
   return results;
  },external);
  assert.equal(loaded.filter(r=>r.error).length,0,JSON.stringify(loaded.filter(r=>r.error)));
  const native=models.find(m=>m.title==='Baium');assert(native);await page.goto(origin+'/?model='+native.key+'&view=3d');await page.waitForFunction(()=>document.querySelector('#view3d canvas')&&!document.querySelector('#viewstatus').textContent,{timeout:90000});assert.equal(await page.locator('#assetSource').isVisible(),false);assert.equal(await page.locator('#native').isDisabled(),false);
  assert.equal(errors.length,0,JSON.stringify(errors));fs.writeFileSync(out+'/browser-verification.json',JSON.stringify({ready:external.length,loaded,animated: animated.key,source_panel:true,animation_play_pause:true,favorite_planning:true,native_regression:true,errors},null,2));console.log('PASS: '+external.length+' external GLBs, source, animation, planning, native model.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
