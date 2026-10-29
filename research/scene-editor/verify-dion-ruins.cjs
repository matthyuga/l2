const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));try{
 await page.goto('http://127.0.0.1:32290');await page.waitForFunction(()=>window.editorState?.().ready,null,{timeout:60000});await page.selectOption('#scene','dion_ruins_blocks');
 await page.waitForFunction(()=>window.editorState?.().scene==='dion_ruins_blocks'&&document.body.dataset.state==='ready',null,{timeout:60000});
 const project=await page.evaluate(()=>JSON.parse(localStorage.getItem('l2-scene-editor-draft')));
 project.name='dion-casas-destruidas-bloques-v1';for(const o of project.objects)o.locked=o.asset.includes('floor');
 const output=path.join(__dirname,'projects/dion-casas-destruidas-bloques-v1.json');if(!fs.existsSync(output))fs.writeFileSync(output,JSON.stringify(project,null,2));
 const dataPath=path.join(__dirname,'data.json'),data=JSON.parse(fs.readFileSync(dataPath));data.scenes.find(s=>s.id==='dion_ruins_blocks').project=path.basename(output);fs.writeFileSync(dataPath,JSON.stringify(data,null,2));
 await page.goto('http://127.0.0.1:32290/?project='+path.basename(output));await page.waitForFunction(()=>window.editorState?.().ready&&window.editorState().scene==='dion_ruins_blocks',null,{timeout:60000});
 const report=await page.evaluate(async()=>{
  const T=await import('three'),{GLTFLoader}=await import('/assets/vendor/addons/loaders/GLTFLoader.js');const loader=new GLTFLoader(),houses=[];
  for(let i=1;i<=3;i++){const g=await loader.loadAsync('/assets/exports/dion-ruins-blocks-v1/house'+i+'.glb');let textured=0;g.scene.traverse(n=>{if(n.isMesh)for(const m of Array.isArray(n.material)?n.material:[n.material])if(m.map)textured++;});houses.push({fragments:g.scene.children.length,animations:g.animations.length,textured});}
  return houses;
 });assert.equal(report.reduce((n,h)=>n+h.fragments,0),132);assert(report.every(h=>h.animations===0&&h.textured>0));
 const initial=await page.evaluate(()=>window.editorState());assert.equal(initial.objects.length,4);assert.equal(initial.modelMotion,null);
 await page.screenshot({path:path.join(__dirname,'preview-dion-casas-destruidas.png')});
 // Expand the first ruined house and select its actual independent fragment.
 const first=initial.objects[0].id;const rootRow=page.locator('.tree-row').filter({has:page.locator('.object[data-id="'+first+'"]')});
 const expand=rootRow.locator('button').first();await expand.click();
 const piece=page.locator('.object[data-id^="'+first+'::"]').first();await piece.click();
 const selected=await page.evaluate(()=>window.editorState());assert(selected.selected.includes('::'));assert.equal(selected.picking.selectedMeshes>0,true);
 await page.locator('#tab-transform').click();const oldX=Number(await page.locator('#position-0').inputValue());await page.locator('#position-0').fill(String(oldX+1.5));await page.locator('#position-0').press('Tab');
 const changed=await page.evaluate(()=>window.editorState());const edit=changed.objects[0].parts.find(p=>p.path===selected.selected.split('::')[1]);assert(edit&&Math.abs(edit.position[0]-oldX-1.5)<.001);assert.deepEqual(changed.objects.slice(1),initial.objects.slice(1),'Moving one fragment must not alter other houses');
 const draft=await page.evaluate(()=>JSON.parse(localStorage.getItem('l2-scene-editor-draft:dion-casas-destruidas-bloques-v1.json')));const response=await page.request.post('http://127.0.0.1:32290/api/projects',{headers:{Origin:'http://127.0.0.1:32290'},data:draft});assert(response.ok(),await response.text());const saved=await response.json();
 await page.goto('http://127.0.0.1:32290/?project='+saved.saved);await page.waitForFunction(()=>window.editorState?.().ready&&window.editorState().scene==='dion_ruins_blocks');const reopened=await page.evaluate(()=>window.editorState());assert.deepEqual(reopened.objects[0].parts,changed.objects[0].parts,'Fragment transform must survive saved project reopening');
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(__dirname,'dion-ruins-verification.json'),JSON.stringify({passed:true,houses:report,editablePiece:selected.selected,objects:initial.objects.length,triangles:initial.triangles,errors},null,2));console.log(JSON.stringify({passed:true,houses:report,selected:selected.selected}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
