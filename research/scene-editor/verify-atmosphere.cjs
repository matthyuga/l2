const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core'),fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const context=await browser.newContext({viewport:{width:1440,height:900},acceptDownloads:true});const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());page.setDefaultTimeout(30000);
  await page.goto('http://127.0.0.1:32290/');await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});
  assert.equal((await page.evaluate(()=>editorState())).atmosphere.sky,null);
  const api=await (await page.request.get('http://127.0.0.1:32290/api/atmosphere')).json();assert(api.items.filter(i=>i.type==='sky').length>0);
  const sky=api.items.find(i=>i.type==='sky'&&i.provider==='Kenney'&&i.title.includes('day'))||api.items.find(i=>i.type==='sky');
  await page.locator('#atmosphere-open').click();await page.locator('#atmosphere-search').fill(sky.title);await page.locator(`.atmosphere-card[data-id="${sky.id}"]`).click();
  await page.waitForFunction(id=>editorState().atmosphere.skyLoaded===id,sky.id);assert.equal(await page.locator('#atmosphere-library').evaluate(d=>d.open),false);
  console.log('Sky image loaded and applied');
  await page.locator('#tab-view').click();await page.locator('#atmosphere-weather').selectOption('sand');await page.waitForFunction(()=>editorState().atmosphere.weather==='sand');
  const a=await page.evaluate(()=>editorState().atmosphere);await page.waitForTimeout(500);const b=await page.evaluate(()=>editorState().atmosphere);assert(b.particles>0);assert.notDeepEqual(a.sample,b.sample);
  await page.locator('#animate-effects').uncheck();await page.waitForTimeout(250);const paused=await page.evaluate(()=>editorState().atmosphere);await page.waitForTimeout(300);assert.deepEqual((await page.evaluate(()=>editorState().atmosphere)).sample,paused.sample);await page.locator('#animate-effects').check();
  await page.screenshot({path:path.join(__dirname,'preview-ambiente-arena.png')});
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#export').click()]);const project=JSON.parse(fs.readFileSync(await download.path()));assert.equal(project.atmosphere.sky,sky.id);assert.equal(project.atmosphere.weather,'sand');
  const post=async p=>page.evaluate(async project=>{const r=await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(project)});return {status:r.status,body:await r.json()};},p);
  const saved=await post(project);assert.equal(saved.status,201,JSON.stringify(saved));
  const bad=structuredClone(project);bad.atmosphere.sky='ffffffffffffffffffff';assert.equal((await post(bad)).status,400);
  const legacy=structuredClone(project);delete legacy.atmosphere;assert.equal((await post(legacy)).status,201);
  await page.locator('#undo').click();await page.waitForFunction(()=>editorState().ready&&editorState().atmosphere.weather==='none');await page.locator('#redo').click();await page.waitForFunction(()=>editorState().ready&&editorState().atmosphere.weather==='sand');
  await page.reload();await page.waitForFunction(id=>window.editorState?.().ready&&editorState().atmosphere.skyLoaded===id&&editorState().atmosphere.weather==='sand',sky.id,{timeout:120000});
  const missing=await page.request.get('http://127.0.0.1:32290/atmosphere/ffffffffffffffffffff.jpg');assert.equal(missing.status(),404);
  await page.locator('#atmosphere-open').click();await page.screenshot({path:path.join(__dirname,'preview-biblioteca-ambientes.png')});
  // Other downloaded categories become available while the builder indexes audio.
  const current=await (await page.request.get('http://127.0.0.1:32290/api/atmosphere')).json();
  let particleTest=false,audioTest=false;
  if(current.items.some(i=>i.type==='particle')){
   await page.locator('#atmosphere-close').click();await page.locator('#atmosphere-open').click();await page.locator('[data-type="particle"]').click();
   const id=current.items.find(i=>i.type==='particle').id;await page.locator(`.atmosphere-card[data-id="${id}"]`).click();await page.waitForFunction(id=>editorState().atmosphere.particle===id,id);particleTest=true;
  }
  if(current.items.some(i=>i.type==='audio')){
   if(!await page.locator('#atmosphere-library').evaluate(d=>d.open))await page.locator('#atmosphere-open').click();await page.locator('[data-type="audio"]').click();await page.locator('.atmosphere-card').first().click();
   await page.waitForFunction(()=>document.getElementById('atmosphere-player').readyState>=1);assert((await page.locator('#atmosphere-player').evaluate(a=>a.duration))>0);
   const sound=current.items.find(i=>i.type==='audio'),range=await page.request.get('http://127.0.0.1:32290'+sound.url,{headers:{Range:'bytes=0-43'}});assert.equal(range.status(),206);assert.equal((await range.body()).length,44);audioTest=true;
  }
  if(await page.locator('#atmosphere-library').evaluate(d=>d.open))await page.locator('#atmosphere-close').click();
  await page.locator('#file').setInputFiles({name:'legacy-atmosphere-qa.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(legacy))});
  await page.waitForFunction(()=>editorState().ready&&editorState().atmosphere.sky===null&&editorState().atmosphere.weather==='none');
  assert.deepEqual((await page.evaluate(()=>editorState().objects)).map(o=>o.id),legacy.objects.map(o=>o.id));
  await page.goto('http://127.0.0.1:32290/?ambientes=1');await page.waitForFunction(()=>window.editorState?.().ready&&document.getElementById('atmosphere-library').open);
  const forbidden=await page.request.post('http://127.0.0.1:32290/api/atmosphere/refresh',{headers:{Origin:'https://example.org'}});assert.equal(forbidden.status(),403);
  assert.deepEqual(errors,[]);const report={passed:true,sky:true,weatherMoves:true,pause:true,export:true,apiSave:saved.body.saved,invalidSkyRejected:true,legacyAccepted:true,legacyOpened:true,undoRedo:true,reload:true,particleTest,audioTest,autoOpen:true,foreignRefreshRejected:true,counts:Object.fromEntries(['sky','particle','audio'].map(k=>[k,current.items.filter(i=>i.type===k).length])),errors};
  fs.writeFileSync(path.join(__dirname,'atmosphere-verification.json'),JSON.stringify(report,null,2));console.log(report);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
