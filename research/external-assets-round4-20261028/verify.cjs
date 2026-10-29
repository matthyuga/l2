const {chromium}=require('E:/l2-local/tools/rea-runtime/node_modules/playwright-core');
const fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const context=await browser.newContext({viewport:{width:1500,height:1100}}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const origin='http://127.0.0.1:32280';const data=await (await context.request.get(origin+'/api/catalog')).json();const models=data.models.filter(m=>m.batch==='Assets externos · Tanda 4'&&m.status==='ready');assert(models.length>0);
 await page.goto(origin+'/?batch='+encodeURIComponent('Assets externos · Tanda 4'));await page.waitForFunction(()=>document.querySelector('#grid .card'));assert.equal(await page.locator('#batch').inputValue(),'Assets externos · Tanda 4');await page.screenshot({path:__dirname+'/catalogo.png'});
 const result=await page.evaluate(async models=>{
  const {GLTFLoader}=await import('/vendor/addons/loaders/GLTFLoader.js'),{preparePlaybackClip}=await import('/viewer.js?v=20261028-round4'),results=[];
  for(const m of models){try{
   const g=await new GLTFLoader().loadAsync(m.gltf);let meshes=0;g.scene.traverse(o=>{if(o.isMesh)meshes++;});if(!meshes)throw Error('No meshes');
   for(const original of g.animations){const before=original.tracks.map(t=>[t.times[0],t.times[t.times.length-1]]),p=preparePlaybackClip(original),starts=p.tracks.filter(t=>t.times.length).map(t=>t.times[0]);if(starts.length&&Math.abs(Math.min(...starts))>1e-5)throw Error('Playback clip does not start at zero');if(!original.tracks.every((t,i)=>t.times[0]===before[i][0]&&t.times[t.times.length-1]===before[i][1]))throw Error('Original time arrays changed');}
   results.push({key:m.key,title:m.title,meshes,clips:g.animations.length});
   g.scene.traverse(o=>{o.geometry?.dispose();for(const mat of o.material?Array.isArray(o.material)?o.material:[o.material]:[]){for(const v of Object.values(mat))if(v?.isTexture){v.dispose();v.source?.data?.close?.();}mat.dispose();}});
  }catch(e){results.push({key:m.key,error:e.message});}}
  return results;
 },models);
 assert.equal(result.filter(r=>r.error).length,0,JSON.stringify(result.filter(r=>r.error)));
 const animated=models.find(m=>m.asset_analysis.animations>1)||models.find(m=>m.asset_analysis.animations>0);assert(animated);await page.goto(origin+'/?model='+animated.key+'&view=3d');await page.waitForFunction(()=>document.querySelector('#view3d canvas')&&!document.querySelector('#viewstatus').textContent);assert.equal(await page.locator('#native').isDisabled(),true);await page.locator('.modelAnimationControls select').selectOption('0');await page.locator('.modelAnimationControls button').click();await page.locator('#visual').scrollIntoViewIfNeeded();await page.screenshot({path:__dirname+'/modelo-animado.png'});
 const technical=models.find(m=>m.rig_analysis);assert(technical);await page.goto(origin+'/rig-inspector.html?model='+technical.key);await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('lectura técnica disponible'));assert.match(await page.locator('#status').innerText(),/SHA-256 verificado/);
 assert.equal(errors.length,0,JSON.stringify(errors));fs.writeFileSync(__dirname+'/browser-verification.json',JSON.stringify({ready:models.length,loaded:result,playback_zero_start:true,source_time_arrays_unchanged:true,technical_hash_verified:true,errors},null,2));console.log('ROUND4_PASS '+models.length+' GLBs, zero-start playback, source times preserved, technical view.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
