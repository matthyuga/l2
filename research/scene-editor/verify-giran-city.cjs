const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');

(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 try{
  await page.goto('http://127.0.0.1:32290');
  await page.waitForFunction(()=>window.editorState?.().ready&&document.body.dataset.state==='ready',null,{timeout:60000});
  assert(await page.locator('#scene option[value="giran_city"]').count(),'Giran city must be present in the shared scene selector');
  await page.selectOption('#scene','giran_city');
  await page.waitForFunction(()=>window.editorState?.().scene==='giran_city'&&document.body.dataset.state==='ready',null,{timeout:180000});
  await page.waitForFunction(()=>window.editorState().triangles>100000,null,{timeout:30000});
  const state=await page.evaluate(()=>window.editorState());
  assert(state.objects.length>=1938,'Giran city must expose its native actors, terrain and BSP');
  assert(state.objects.some(object=>object.name==='Giran_BSP'),'Giran city must include its plaza, street and interior BSP surfaces');
  // renderer.info counts only this frame's visible triangles; aspect ratio
  // changes frustum culling. Check the source geometry independently.
  const gltf=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../model-catalog/exports/scene-giran-city/scene.gltf'),'utf8'));
  const sourceTriangles=gltf.nodes.reduce((total,node)=>total+(node.mesh===undefined?0:gltf.meshes[node.mesh].primitives.reduce((sum,p)=>sum+gltf.accessors[p.indices===undefined?p.attributes.POSITION:p.indices].count/3,0)),0);
  assert(sourceTriangles>524000,'Giran city source must contain the complete geometry');
  assert((await page.locator('#status').textContent()).includes('189 pinceles BSP'),'scene description must report the recovered BSP');
  assert(state.objects.every(object=>object.locked),'native Giran city actors must start protected');
  assert.deepEqual(errors,[]);
  await page.screenshot({path:path.join(__dirname,'preview-ciudad-giran-integrada.png')});
  const result={passed:true,scene:state.scene,objects:state.objects.length,triangles:state.triangles,errors};
  fs.writeFileSync(path.join(__dirname,'giran-city-verification.json'),JSON.stringify(result,null,2));
  console.log('PASS: Giran city integrated in shared editor',result);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
