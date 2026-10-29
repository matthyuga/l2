const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1000},baseURL:'http://127.0.0.1:32290'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto('http://127.0.0.1:32290');await page.waitForFunction(()=>window.editorState?.().ready&&document.body.dataset.state==='ready',null,{timeout:60000});
  let s=await page.evaluate(()=>window.editorState());assert.equal(s.scene,'gludio');assert.equal(s.objects.length,8);assert(s.triangles>1000);assert(s.objects.every(o=>o.locked));
  await page.screenshot({path:path.join(__dirname,'preview-muelle.png')});
  const layout=await page.evaluate(()=>{const a=document.querySelector('#studio').getBoundingClientRect(),v=document.querySelector('#viewport').getBoundingClientRect();return {left:a.x,right:a.right,viewport:v.x,panelsAlpha:getComputedStyle(document.querySelector('#studio')).backgroundColor};});assert.equal(layout.left,0);assert(layout.right<=layout.viewport+1);assert(layout.panelsAlpha.includes('0.78'));
  await page.locator('#tab-view').click();await page.locator('#show-grid').check();await page.locator('#show-grid').uncheck();await page.locator('#panel-opacity').fill('60');assert.equal(await page.locator('#opacity-value').textContent(),'60 %');await page.locator('#panel-opacity').fill('78');await page.locator('#tab-library').click();
  await page.locator('#tab-library').click();await page.locator('#search').fill('Christmas Tree');await page.locator('.asset').first().click();
  const bounds=await page.locator('#viewport canvas').boundingBox();for(const [x,y] of [[.54,.45],[.5,.5],[.56,.52]]){await page.mouse.click(bounds.x+bounds.width*x,bounds.y+bounds.height*y);try{await page.waitForFunction(()=>window.editorState().objects.length===9&&document.body.dataset.state==='ready',null,{timeout:2500});break;}catch{}}
  assert.equal((await page.evaluate(()=>window.editorState())).objects.length,9,'placing a library item on the dock');
  await page.screenshot({path:path.join(__dirname,'preview-decoracion.png')});
  await page.locator('#undo').click();await page.waitForFunction(()=>window.editorState().objects.length===8&&document.body.dataset.state==='ready');await page.locator('#tab-library').click();await page.locator('#search').fill('');await page.locator('#asset-close').click();await page.locator('#tab-scene').click();
  await page.locator('.object').first().click();await page.locator('.tree-row').filter({has:page.locator('.object[data-id="'+(await page.evaluate(()=>window.editorState().selected))+'"]')}).locator('.tree-lock').click();
  await page.locator('#tab-transform').click();const original=await page.locator('#position-0').inputValue();await page.locator('#position-0').fill(String(Number(original)+3));await page.locator('#position-0').press('Tab');
  assert.equal((await page.evaluate(()=>window.editorState())).objects[0].position[0],Number(original)+3);
  await page.locator('#undo').click();await page.waitForFunction(x=>Math.abs(window.editorState().objects[0].position[0]-x)<.01,Number(original));
  await page.locator('#redo').click();await page.waitForFunction(x=>Math.abs(window.editorState().objects[0].position[0]-x)<.01,Number(original)+3);
  await page.locator('.object').first().click();await page.locator('#tab-scene').click();await page.locator('#duplicate').click();await page.waitForFunction(()=>window.editorState().objects.length===9&&document.body.dataset.state==='ready');
  await page.locator('#name').fill('Prueba de decoración');await page.locator('#name').press('Tab');
  await page.locator('.tree-row.active .tree-visibility').click();assert.equal((await page.evaluate(()=>window.editorState())).objects.at(-1).visible,false);await page.locator('.tree-row.active .tree-visibility').click();
  const project=await page.evaluate(()=>({format:'l2-scene-editor-v1',scene:window.editorState().scene,reference:{qa:true},objects:window.editorState().objects}));
  await page.locator('#save').click();await page.waitForFunction(()=>document.querySelector('#status').textContent.startsWith('Versión guardada'));const saved=await page.locator('#status').textContent();
  const filename=saved.replace('Versión guardada en projects/','');const disk=JSON.parse(fs.readFileSync(path.join(__dirname,'projects',filename)));assert.equal(disk.objects.length,9);
  await page.locator('#remove').click();assert.equal((await page.evaluate(()=>window.editorState())).objects.length,8);
  await page.locator('#file').setInputFiles({name:'restaurar.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(project))});await page.waitForFunction(()=>window.editorState().objects.length===9&&document.body.dataset.state==='ready');
  assert.equal((await page.evaluate(()=>window.editorState())).objects.at(-1).name,'Prueba de decoración');
  const invalid=await page.request.post('/api/projects',{headers:{Origin:'http://127.0.0.1:32290'},data:{format:'l2-scene-editor-v1',scene:'gludio',objects:[{asset:'../../client'}]}});assert.equal(invalid.status(),400);
  const wrongOrigin=await page.request.post('/api/projects',{headers:{Origin:'https://example.com'},data:project});assert.equal(wrongOrigin.status(),403);
  const secret=await page.request.get('/projects/'+filename);assert.equal(secret.status(),404);
  await page.selectOption('#scene','gracia');await page.waitForFunction(()=>window.editorState().scene==='gracia'&&document.body.dataset.state==='ready',null,{timeout:60000});
  s=await page.evaluate(()=>window.editorState());assert(s.objects.length>1);assert(s.triangles>1000);
  await page.screenshot({path:path.join(__dirname,'preview-aeronave.png')});assert.deepEqual(errors,[]);
  await page.reload();await page.waitForFunction(()=>window.editorState?.().scene==='gracia'&&document.body.dataset.state==='ready',null,{timeout:60000});assert.equal((await page.evaluate(()=>window.editorState())).objects.length,4);
  await page.setViewportSize({width:1360,height:768});await page.locator('#tab-scene').click();await page.locator('.object').first().click();
  await page.screenshot({path:path.join(__dirname,'preview-studio-1360.png')});
  assert(await page.locator('#name').isVisible());const overflows=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);assert(!overflows,'workspace must fit without horizontal overflow');
  fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify({passed:true,gludioPieces:8,airshipPieces:s.objects.length,checks:['real WebGL render','library object placement on dock','base locked','numeric transform','undo/redo','duplicate','rename','visibility','versioned disk save','remove','project import','invalid project rejected','foreign origin rejected','private project files not served','airship scene loads'],errors,qaProject:filename},null,2));
  console.log('PASS: scene editor functional checks; aircraft parts:',s.objects.length);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
