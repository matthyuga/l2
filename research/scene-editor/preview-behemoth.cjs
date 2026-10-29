const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
const page=await browser.newPage({viewport:{width:1400,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.route('**/app.js',route=>route.fulfill({contentType:'text/javascript',body:''}));
await page.goto('http://127.0.0.1:32290/');await page.waitForTimeout(500);
await page.evaluate(asset=>window.requestAsset=asset,process.env.BEHEMOTH_ASSET||null);
await page.evaluate(time=>window.previewTime=time,Number(process.env.BEHEMOTH_TIME||0));
const result=await page.evaluate(async()=>{
 const THREE=await import('/assets/vendor/three.module.js');const {GLTFLoader}=await import('/assets/vendor/addons/loaders/GLTFLoader.js');
 document.querySelectorAll('style,link').forEach(x=>x.remove());document.body.innerHTML='';document.body.style.cssText='margin:0;background:#10151b';
 const r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});r.setSize(1400,1000);r.setPixelRatio(1);r.outputColorSpace=THREE.SRGBColorSpace;r.setClearColor(0x10151b);document.body.append(r.domElement);
 const scene=new THREE.Scene();scene.add(new THREE.HemisphereLight(0xf4e7d0,0x45556c,2.8));const light=new THREE.DirectionalLight(0xffe6c7,3.2);light.position.set(6,10,7);scene.add(light);const fill=new THREE.DirectionalLight(0xb9d7ff,2);fill.position.set(-6,5,-5);scene.add(fill);
 const url=new URL(location.href).searchParams.get('asset')||window.requestAsset;
 const g=await new GLTFLoader().loadAsync('/assets/'+(url||'exports/LineageMonsters3/SkeletalMesh/antaras_ex_a_m00.gltf'));scene.add(g.scene);g.scene.updateMatrixWorld(true);
 if(g.animations.length){const mixer=new THREE.AnimationMixer(g.scene);const clip=g.animations.find(a=>a.name==='Walk')||g.animations[0];mixer.clipAction(clip).play();mixer.setTime(window.previewTime);g.scene.updateMatrixWorld(true);}
 const box=new THREE.Box3().setFromObject(g.scene);const center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()),extent=Math.max(...size.toArray());
 const camera=new THREE.PerspectiveCamera(36,1.4,.01,1000);const target=center.clone();camera.position.copy(center).add(new THREE.Vector3(1,.52,1.5).normalize().multiplyScalar(extent*1.85));camera.lookAt(target);
 const grid=new THREE.GridHelper(extent*2,20,0x354354,0x202a36);grid.position.y=box.min.y-.01;scene.add(grid);
 window.preview={THREE,scene,r,camera,target,extent,model:g.scene,render:()=>r.render(scene,camera)};r.render(scene,camera);
 return {bounds:{min:box.min.toArray(),max:box.max.toArray()},nodes:g.scene.children.map(x=>x.name),animations:g.animations.map(a=>a.name)};
});
console.log(JSON.stringify(result));await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>{window.preview.render();resolve()})));await page.screenshot({path:path.join(__dirname,process.env.BEHEMOTH_ASSET?'preview-behemoth-equipped.png':'preview-behemoth-source.png')});
if(process.env.BEHEMOTH_ASSET){
 const thumb=await page.evaluate(()=>{const p=window.preview;p.r.setSize(384,420);p.camera.aspect=384/420;p.camera.position.copy(p.target).add(new p.THREE.Vector3(1,.6,1.5).normalize().multiplyScalar(p.extent*2.15));p.camera.updateProjectionMatrix();p.camera.lookAt(p.target);p.render();return p.r.domElement.toDataURL('image/png').split(',')[1]});
 fs.writeFileSync(path.join(__dirname,'../model-catalog/thumbs/l2lab_behemoth_two_riders.png'),Buffer.from(thumb,'base64'));
 await page.evaluate(()=>{const p=window.preview;p.r.setSize(1400,1000);p.camera.aspect=1.4;p.camera.updateProjectionMatrix();});
 await page.evaluate(()=>{const p=window.preview;p.camera.position.copy(p.target).add(new p.THREE.Vector3(-1,.7,-1.3).normalize().multiplyScalar(p.extent*1.85));p.camera.lookAt(p.target);p.render();});
 await page.screenshot({path:path.join(__dirname,'preview-behemoth-rear.png')});
 await page.evaluate(()=>{const p=window.preview;p.camera.position.copy(p.target).add(new p.THREE.Vector3(1,.45,.25).normalize().multiplyScalar(p.extent*1.65));p.camera.lookAt(p.target);p.render();});
 await page.screenshot({path:path.join(__dirname,'preview-behemoth-side.png')});
}
await browser.close();if(errors.length){console.error(errors);process.exitCode=1;}
})().catch(e=>{console.error(e);process.exitCode=1});
