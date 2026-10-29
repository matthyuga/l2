'use strict';
const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core'),fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().includes('favicon'))errors.push(r.status()+' '+r.url());});
 await page.goto('http://127.0.0.1:32290');await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:60000});
 const file=path.join(__dirname,'projects/giranrenovada1.json'),project=JSON.parse(fs.readFileSync(file));
 await page.locator('#file').setInputFiles(file);await page.waitForFunction(()=>window.editorState?.().scene==='giran_city'&&window.editorState().objects.length>2200&&document.body.dataset.state==='ready',null,{timeout:180000});
 const state=await page.evaluate(()=>window.editorState());assert.equal(state.objects.length,project.objects.length);assert.equal(state.objects.filter(o=>o.kind==='group').length,8);assert.equal(state.objects.filter(o=>!o.visible).length,2);
 const shots=['general','plaza','mercado','catedral','rio','norte','memoria','comercios','panorama','planta'];
 const folder=path.resolve(__dirname,'../../mapas editados/giranrenovada1');fs.mkdirSync(folder,{recursive:true});
 for(let i=0;i<shots.length;i++){await page.locator('.camera-load').nth(i).click();await page.locator('#viewport-maximize').click();await page.waitForTimeout(600);await page.screenshot({path:path.join(folder,shots[i]+'.png')});await page.locator('#viewport-maximize').click();}
 const api=await page.evaluate(async p=>{const r=await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});return {status:r.status,body:await r.json()};},project);assert.equal(api.status,201,JSON.stringify(api));
 assert.deepEqual(errors,[]);
 // An isolated reload must restore the same scene from the saved draft.
 await page.reload();await page.waitForFunction(n=>window.editorState?.().objects.length===n&&document.body.dataset.state==='ready',project.objects.length,{timeout:180000});
 assert.deepEqual(errors,[]);
 const report={passed:true,objects:project.objects.length,added:project.objects.length-1945,zones:8,views:shots,savedSnapshot:api.body.saved,reload:true,errors};fs.writeFileSync(path.join(__dirname,'giran-renovada-verification.json'),JSON.stringify(report,null,2));console.log(report);
 // Furniture thumbnail for the local library.
 const thumb=await browser.newPage({viewport:{width:384,height:420}});await thumb.goto('http://127.0.0.1:32290/thumbnail-render.html?asset=exports/giran-renovada/furniture.gltf');await thumb.waitForFunction(()=>document.body.dataset.ready||document.body.dataset.error,null,{timeout:30000});assert.equal(await thumb.locator('body').getAttribute('data-error'),null);await thumb.locator('canvas').screenshot({path:path.resolve(__dirname,'../model-catalog/thumbs/giran-renovada-furniture.png')});
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
