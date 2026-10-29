const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const results=[];
 for(const mode of ['normal','no-effects','effects-only']){
  const page=await browser.newPage({viewport:{width:1600,height:1000}});
  await page.route('**/api/projects/dion-hecatombe-v1.json',async route=>{
   const project=JSON.parse(fs.readFileSync(path.join(__dirname,'projects/dion-hecatombe-v1.json')));
   if(mode==='no-effects'){project.objects=project.objects.filter(o=>o.kind!=='effect');project.atmosphere.weather='none';}
   if(mode==='effects-only')project.objects=project.objects.filter(o=>o.kind==='effect');
   await route.fulfill({json:project});
  });
  await page.goto('http://127.0.0.1:32290/?project=dion-hecatombe-v1.json');
  await page.waitForFunction(()=>document.body.dataset.state==='ready'&&window.editorState?.().scene==='dion_hecatombe',null,{timeout:180000});
  await page.waitForTimeout(1000);
  const result=await page.evaluate(()=>new Promise(resolve=>{const samples=[];let start=performance.now(),last=start;function tick(now){samples.push(now-last);last=now;if(now-start<1800)return requestAnimationFrame(tick);const s=window.editorState();samples.sort((a,b)=>a-b);resolve({fps:Math.round(samples.length*1000/(now-start)),medianMs:samples[Math.floor(samples.length/2)],p95Ms:samples[Math.floor(samples.length*.95)],drawCalls:s.drawCalls,triangles:s.triangles});}requestAnimationFrame(tick);}));
  results.push({mode,...result});await page.close();
 }
 fs.writeFileSync(path.join(__dirname,process.argv[2]||'dion-performance.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
