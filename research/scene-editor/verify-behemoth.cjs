const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,'data.json'))),asset=data.assets.find(a=>a.id==='l2lab_behemoth_two_riders');assert(asset);
 const project={format:'l2-scene-editor-v1',scene:'gludio',reference:data.reference,camera:{position:[10,7,11],target:[0,2.8,0],fov:40},cameras:Array(10).fill(null),objects:[{id:'behemoth-two-riders-v1',name:'Behemoth - dos ocupantes - prototipo visual',asset:asset.id,node:'',base:false,locked:false,visible:true,position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]}]};
 const projectPath=path.join(__dirname,'projects/BEHEMOTH-DOS-OCUPANTES-V1.json');fs.writeFileSync(projectPath,JSON.stringify(project,null,2));
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
 const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:32290');await page.waitForFunction(()=>window.editorState?.().ready&&document.body.dataset.state==='ready',null,{timeout:60000});
 const served=await page.evaluate(()=>fetch('/api/data').then(r=>r.json()));assert(served.assets.some(x=>x.id===asset.id),'live server registers custom mount');
 await page.locator('#file').setInputFiles(projectPath);try{await page.waitForFunction(()=>window.editorState?.().objects.length===1&&window.editorState().objects[0].asset==='l2lab_behemoth_two_riders'&&document.body.dataset.state==='ready');}catch(e){console.log(await page.locator('#status').textContent());console.log(errors);await page.screenshot({path:path.join(__dirname,'behemoth-import-debug.png')});throw e;}
 const state=await page.evaluate(()=>window.editorState());assert(state.triangles>5000);assert.equal(state.objects[0].locked,false);
 await page.locator('#tab-scene').click();await page.locator('.object').first().click();
 await page.screenshot({path:path.join(__dirname,'preview-behemoth-editor.png')});
 const saved=await page.evaluate(async p=>{const r=await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(p)});return {status:r.status,body:await r.json()}},project);assert.equal(saved.status,201);
 assert.equal(errors.length,0,errors.join('\n'));
 fs.writeFileSync(path.join(__dirname,'behemoth-verification.json'),JSON.stringify({passed:true,checks:['custom asset served','gltf loaded in editor','dedicated project imported','editable selection','project save accepted','no browser errors'],triangles:state.triangles,errors},null,2));console.log('Behemoth editor verification passed');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
