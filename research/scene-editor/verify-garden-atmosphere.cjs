const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto'),{chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage({viewport:{width:1440,height:900}}),errors=[],dialogs=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',async d=>{dialogs.push(d.message());await d.accept();});page.setDefaultTimeout(30000);
 const file=path.join(__dirname,'projects/gludiobrisas1-animado.json'),original=fs.readFileSync(file),hash=b=>crypto.createHash('sha256').update(b).digest('hex'),project=JSON.parse(original);
 await page.goto('http://127.0.0.1:32290/');await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:120000});
 const previous=await page.evaluate(()=>localStorage.getItem('l2-scene-editor-draft'));
 await page.locator('#scene').selectOption('project:gludiobrisas1-animado.json');await page.waitForURL('**/?project=gludiobrisas1-animado.json&ambientes=1');
 await page.waitForFunction(n=>window.editorState?.().ready&&editorState().objects.length===n,project.objects.length,{timeout:120000});
 assert.equal(await page.locator('#scene').inputValue(),'project:gludiobrisas1-animado.json');assert.equal(await page.evaluate(()=>localStorage.getItem('l2-scene-editor-draft')),previous);
 const state=await page.evaluate(()=>editorState());assert.equal(state.effects.emitters.length,9);assert.equal(await page.locator('#atmosphere-library').evaluate(d=>d.open),true);
 const catalog=await (await page.request.get('http://127.0.0.1:32290/api/atmosphere')).json(),sky=catalog.items.find(i=>i.type==='sky'&&i.provider==='Kenney'&&i.title.includes('day'));
 await page.locator('#atmosphere-search').fill(sky.title);await page.locator(`.atmosphere-card[data-id="${sky.id}"]`).click();await page.waitForFunction(id=>editorState().atmosphere.skyLoaded===id,sky.id);
 await page.locator('.camera-load').first().click();await page.waitForTimeout(600);await page.screenshot({path:path.join(__dirname,'preview-muelle-jardin-ambientes.png')});
 assert.deepEqual(dialogs,[]);await page.reload();await page.waitForFunction(n=>window.editorState?.().ready&&editorState().objects.length===n,project.objects.length,{timeout:120000});
 assert.equal((await page.evaluate(()=>editorState())).atmosphere.sky,sky.id);assert.equal(await page.locator('#scene').inputValue(),'project:gludiobrisas1-animado.json');assert.equal(await page.evaluate(()=>localStorage.getItem('l2-scene-editor-draft')),previous);
 assert.equal(hash(fs.readFileSync(file)),hash(original));assert.deepEqual(errors,[]);assert.equal(dialogs.length,1);assert.equal(dialogs[0],'');
 const report={passed:true,objects:state.objects.length,emitters:state.effects.emitters.length,selector:true,opensAtmospheres:true,skyPreview:true,reload:true,separateDraft:true,originalUnchanged:true,errors};fs.writeFileSync(path.join(__dirname,'garden-atmosphere-verification.json'),JSON.stringify(report,null,2));console.log(report);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
