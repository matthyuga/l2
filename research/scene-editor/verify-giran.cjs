const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');

(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 try{
  await page.goto('http://127.0.0.1:32290');
  await page.waitForFunction(()=>window.editorState?.().ready&&document.body.dataset.state==='ready',null,{timeout:60000});
  assert(await page.locator('#scene option[value="giran"]').count(),'Giran must be present in the shared scene selector');
  await page.selectOption('#scene','giran');
  await page.waitForFunction(()=>window.editorState?.().scene==='giran'&&document.body.dataset.state==='ready',null,{timeout:180000});
  const state=await page.evaluate(()=>window.editorState());
  assert(state.objects.length>=1638,'the complete Giran map must expose its native actors');
  assert(state.triangles>10000,'the Giran map must contain rendered geometry');
  assert(state.objects.every(object=>object.locked),'native Giran actors must start protected');
  assert.deepEqual(errors,[]);
  await page.screenshot({path:path.join(__dirname,'preview-giran-integrado.png')});
  const result={passed:true,scene:state.scene,objects:state.objects.length,triangles:state.triangles,errors};
  fs.writeFileSync(path.join(__dirname,'giran-verification.json'),JSON.stringify(result,null,2));
  console.log('PASS: Giran integrated in shared editor',result);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
