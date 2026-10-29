const fs=require('fs'),path=require('path'),assert=require('assert'),{chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
(async()=>{const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});try{
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const html=fs.readFileSync(path.join(__dirname,'alturas-muelle-aeronaves.html'),'utf8');
 const wrapper='<style>:root{--foreground:#202833;--background:#fff;--border:#d6dde4;--viz-series-1:#166b99;--viz-series-2:#946b16}body{font-family:Arial,sans-serif;margin:16px}.viz-controls{display:flex;gap:16px;flex-wrap:wrap}.form-label{display:flex;flex:1;min-width:130px;flex-direction:column;gap:6px}.form-select{width:100%;min-width:0;font:inherit;padding:8px;box-sizing:border-box}.text-small{font-size:12px}h3{font-weight:500}</style>';
 for(const width of [736,360,320]){
  await page.setViewportSize({width,height:1300});await page.setContent(wrapper+html);await page.waitForSelector('#l2-height-reference[data-delta-z]');
  assert.equal(Number(await page.locator('#l2-height-reference').getAttribute('data-delta-z')),15419);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#l2-height-from').selectOption('dock');await page.locator('#l2-height-to').selectOption('ship');
  assert.equal(Number(await page.locator('#l2-height-reference').getAttribute('data-delta-z')),24);assert.equal(Number(await page.locator('#l2-height-reference').getAttribute('data-horizontal')),3000);
  await page.locator('#l2-height-to').selectOption('sky');assert.equal(await page.locator('#l2-height-reference').getAttribute('data-celestial'),'true');assert((await page.locator('#l2-height-measure').textContent()).includes('no representa'));
  await page.locator('#l2-height-from').selectOption('ground');await page.locator('#l2-height-to').selectOption('vigilia-gallery');
  assert.equal(Number(await page.locator('#l2-height-reference').getAttribute('data-delta-z')),16163);
  const outside=await page.locator('svg').evaluateAll(list=>list.flatMap(svg=>{const r=svg.getBoundingClientRect();return [...svg.querySelectorAll('text')].filter(t=>{const b=t.getBoundingClientRect();return b.x<r.x-1||b.right>r.right+1;}).map(t=>t.textContent);}));assert.deepEqual(outside,[]);
  await page.locator('#l2-height-to').selectOption('dock');await page.screenshot({path:path.join(__dirname,`alturas-preview-${width}.png`),fullPage:true});
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(__dirname,'altitude-verification.json'),JSON.stringify({passed:true,widths:[736,360,320],dockHeight:15419,shipHorizontalFromDock:3000,shipDeltaFromDock:24,galleryHeight:16163,celestialDistanceSeparated:true,errors},null,2));console.log('PASS altitude arithmetic, selections, sky distinction and responsive layouts');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
