const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const assert=require('assert'),path=require('path'),fs=require('fs');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1314,height:622}}),errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 try{
  await page.goto('http://127.0.0.1:32290');
  await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:60000});
  const geometry=()=>page.evaluate(()=>Object.fromEntries(['studio','viewport','scene-workspace'].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return[id,{x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom}];})));
  for(const size of [{width:1314,height:622},{width:1600,height:1000},{width:900,height:650}]){
   await page.setViewportSize(size);
   await page.waitForTimeout(150);
   const g=await geometry();
   assert(Math.abs(g.viewport.y-g['scene-workspace'].y)<1,'Scene tree and viewport must share one row');
   assert(Math.abs(g.viewport.height-g.studio.height)<1,'Viewport must fill workspace height');
   assert(g['scene-workspace'].x>=g.viewport.x+g.viewport.width-1,'Scene tree must remain on the right');
   assert(g.viewport.height>size.height-160,'No empty lower half');
  }
  await page.setViewportSize({width:1314,height:622});
  await page.screenshot({path:path.join(__dirname,'preview-visor-completo.png')});
  const objects=(await page.evaluate(()=>window.editorState())).objects.map(object=>object.id);
  await page.locator('#viewport-float').click();
  const floating=await page.locator('#viewport').boundingBox();
  const bar=await page.locator('.viewport-window-bar').boundingBox();
  await page.mouse.move(bar.x+30,bar.y+15);await page.mouse.down();await page.mouse.move(bar.x+65,bar.y+45);await page.mouse.up();
  const moved=await page.locator('#viewport').boundingBox();assert(moved.x>floating.x+20&&moved.y>floating.y+20,'Floating window must move');
  assert.equal(await page.locator('#viewport').evaluate(el=>getComputedStyle(el).resize),'both');
  await page.locator('#viewport').evaluate(el=>{el.style.width='700px';el.style.height='350px';});
  await page.waitForFunction(()=>Math.abs(document.querySelector('#viewport canvas').clientHeight-350)<3);
  await page.locator('#viewport-maximize').click();
  await page.waitForFunction(()=>document.querySelector('#viewport canvas').clientHeight===innerHeight);
  const maximized=await page.locator('#viewport').boundingBox();assert.equal(maximized.width,1314);assert.equal(maximized.height,622);
  await page.screenshot({path:path.join(__dirname,'preview-visor-maximizado.png')});
  await page.locator('#viewport-maximize').click();assert.equal(await page.locator('#viewport').getAttribute('data-window-mode'),'floating');
  await page.locator('#viewport-fullscreen').click();
  await page.waitForFunction(()=>document.fullscreenElement?.id==='viewport');
  await page.locator('#viewport-fullscreen').click();
  await page.waitForFunction(()=>!document.fullscreenElement);
  await page.locator('#viewport-dock').click();
  assert.equal(await page.locator('#viewport').getAttribute('data-window-mode'),'docked');
  await page.locator('#show-studio-panel').uncheck();await page.locator('#toggle-scene-workspace').click();
  const collapsed=await geometry();assert(collapsed.viewport.width>1200);assert.equal(collapsed.viewport.y,collapsed.studio.y);
  assert.deepEqual((await page.evaluate(()=>window.editorState())).objects.map(object=>object.id),objects);
  assert.deepEqual(errors,[]);
  const report={passed:true,checks:['single row at three resolutions','full workspace height','floating drag','resize and renderer adaptation','maximize and restore','browser fullscreen and exit','dock','collapsed panels','objects preserved'],errors};
  fs.writeFileSync(path.join(__dirname,'viewport-window-verification.json'),JSON.stringify(report,null,2));console.log(report);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
