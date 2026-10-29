const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const original=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../backups/gludio-flores-20261020/research/scene-editor/projects/gludiobrisas1-animado.json'),'utf8'));
 // Represent edits made after the saved file: placement, label, visibility and camera.
 const old=structuredClone(original),flower=old.objects.find(o=>o.name==='Flor de urna');flower.position[0]+=.125;flower.name='Mi flor editada';
 old.objects.find(o=>o.name==='Banco').visible=false;
 const expected=structuredClone(old);for(const o of expected.objects){if(o.asset==='web_kenney_nature_flower_purplea')o.asset='custom_gludio_cosmos_lavender';if(o.asset==='web_kenney_nature_flower_yellowa')o.asset='custom_gludio_cosmos_ivory';}
 const results=[];
 for(const suffix of ['',':gludiobrisas1-animado.json']){
  const context=await browser.newContext({viewport:{width:1400,height:950}}),page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(({key,old})=>{if(!localStorage.getItem(key))localStorage.setItem(key,JSON.stringify(old));},{key:'l2-scene-editor-draft'+suffix,old});
  await page.goto('http://127.0.0.1:32290/'+(suffix?'?project=gludiobrisas1-animado.json':''));
  await page.waitForFunction(()=>window.editorState?.().ready&&window.editorState().effects.emitters.length===8,null,{timeout:120000});
  const state=await page.evaluate(()=>window.editorState());assert.deepEqual(state.objects,expected.objects);
  const key='l2-scene-editor-draft'+suffix+':before-botanical-v1';
  assert.deepEqual(await page.evaluate(key=>JSON.parse(localStorage.getItem(key)),key),old);
  await page.reload();await page.waitForFunction(()=>window.editorState?.().ready&&window.editorState().effects.emitters.length===8,null,{timeout:120000});
  assert.deepEqual((await page.evaluate(()=>window.editorState())).objects,expected.objects);
  assert.deepEqual(await page.evaluate(key=>JSON.parse(localStorage.getItem(key)),key),old);
  assert.deepEqual(errors,[]);results.push({draft:suffix||'default',flowers:66,userEditsPreserved:true,originalDraftBackedUp:true,reload:true,errors});
  if(suffix){await page.locator('.camera-load').nth(2).click();await page.locator('#viewport-maximize').click();await page.waitForTimeout(500);await page.screenshot({path:path.resolve(__dirname,'../../mapas editados/gludiobrisas1-animado/flores-borrador-corregido.jpg'),type:'jpeg',quality:90});}
  await context.close();
 }
 const report={passed:true,results};fs.writeFileSync(path.join(__dirname,'gludio-flower-drafts-verification.json'),JSON.stringify(report,null,2));console.log(report);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
