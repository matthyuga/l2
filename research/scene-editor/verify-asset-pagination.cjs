const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const assert=require('assert');

(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1360,height:900},baseURL:'http://127.0.0.1:32290'});
 page.setDefaultTimeout(20000);
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 try{
  await page.goto('/',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>document.querySelector('#asset-count')?.textContent);
  await page.locator('#tab-library').click();
  await page.locator('#filter').selectOption('all');
  await page.locator('#asset-pages .asset-page').first().waitFor();
  assert.equal(await page.locator('.asset').count(),30);
  assert.equal(await page.locator('.asset-page.active').innerText(),'1');
  const first=await page.locator('.asset').first().getAttribute('data-asset');
  await page.locator('.asset-page').filter({hasText:/^2$/}).click();
  assert.equal(await page.locator('.asset-page.active').innerText(),'2');
  assert.notEqual(await page.locator('.asset').first().getAttribute('data-asset'),first);
  await page.locator('#search').fill('bandera roja');
  assert.equal(await page.locator('.asset').count(),2);
  assert(await page.locator('#asset-pages').isHidden());
  await page.locator('#search').fill('');
  assert.equal(await page.locator('.asset-page.active').innerText(),'1');
  assert.deepEqual(errors,[]);
  console.log('PASS: 30 recursos por página, navegación numerada y reinicio de filtros.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
