const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto('http://127.0.0.1:32290/?project=dion-hecatombe-v1.json');
  await page.waitForFunction(()=>document.body.dataset.state==='ready'&&window.editorState?.().scene==='dion_hecatombe',null,{timeout:180000});
  const before=await page.evaluate(()=>window.editorState());
  const highlight=await page.evaluate(async()=>{
   const T=await import('three'),{createSelectionHighlights}=await import('/selection-highlights.js');
   const scene=new T.Scene(),group=new T.Group(),geometry=new T.BoxGeometry(1,1,1),material=new T.MeshBasicMaterial();
   for(let i=0;i<160;i++){const mesh=new T.Mesh(geometry,material);mesh.position.x=i;group.add(mesh);}scene.add(group);
   const highlights=createSelectionHighlights(scene),start=performance.now();highlights.show('hover',group);highlights.update();
   const broad=highlights.state.hoverMeshes,ms=performance.now()-start;
   highlights.show('selected',group.children[0]);const piece=highlights.state.selectedMeshes;
   highlights.setEnabled(false);highlights.show('hover',group);const disabled=highlights.state.hoverMeshes;
   highlights.show('selected',null);highlights.clearHover();geometry.dispose();material.dispose();return {broad,piece,disabled,ms};
  });
  assert.equal(highlight.broad,1);assert.equal(highlight.piece,1);assert.equal(highlight.disabled,0);
  assert.equal(before.effects.emitters.length,28);assert.equal(before.atmosphere.weather,'ash');
  await page.waitForTimeout(1400);
  const after=await page.evaluate(()=>window.editorState());
  assert(after.effects.emitters.some((e,i)=>JSON.stringify(e.sample)!==JSON.stringify(before.effects.emitters[i].sample)),'Fire and smoke must animate');
  await page.screenshot({path:path.join(__dirname,'preview-dion-hecatombe-v1.png')});
  const project=await page.evaluate(()=>JSON.parse(localStorage.getItem('l2-scene-editor-draft:dion-hecatombe-v1.json')));
  const res=await page.request.post('http://127.0.0.1:32290/api/projects',{headers:{Origin:'http://127.0.0.1:32290'},data:project});assert(res.ok(),await res.text());
  const saved=await res.json();
  await page.goto('http://127.0.0.1:32290/?project='+saved.saved);
  await page.waitForFunction(()=>document.body.dataset.state==='ready'&&window.editorState?.().effects.emitters.length===28,null,{timeout:180000});
  await page.selectOption('#scene','gludio');
  await page.waitForFunction(()=>document.body.dataset.state==='ready'&&window.editorState?.().scene==='gludio');
  await page.selectOption('#scene','dion_hecatombe');
  await page.waitForFunction(()=>document.body.dataset.state==='ready'&&window.editorState?.().scene==='dion_hecatombe'&&window.editorState().effects.emitters.length===28,null,{timeout:180000});
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(__dirname,'dion-hecatombe-verification.json'),JSON.stringify({passed:true,objects:after.objects.length,triangles:after.triangles,emitters:after.effects.emitters.length,qaSaved:saved,errors},null,2));
  console.log(JSON.stringify({passed:true,triangles:after.triangles,objects:after.objects.length,saved}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
