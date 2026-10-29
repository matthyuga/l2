'use strict';
const {chromium}=require('../../tools/rea-runtime/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{
 const root=__dirname,catalog=path.resolve(root,'../model-catalog');
 const gallery=JSON.parse(fs.readFileSync(path.join(catalog,'gallery.json'),'utf8'));
 const assets=gallery.models.filter(v=>v.key?.startsWith('web_')&&v.gltf);
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:384,height:420}});page.setDefaultTimeout(20000);
 let done=0;const failed=[];
 for(const asset of assets){
  const extension=asset.key.startsWith('web_3td_')?'.png':(path.extname(asset.thumbnail||'')||'.png');
  const folder=asset.key.startsWith('web_3td_')?'web-3td-fantasy-ruins':'web-kenney-nature';
  const target=path.join(catalog,'thumbs',folder,path.basename(asset.gltf,path.extname(asset.gltf))+extension);
  if(fs.existsSync(target))continue;
  fs.mkdirSync(path.dirname(target),{recursive:true});
  try{await page.goto('http://127.0.0.1:32290/thumbnail-render.html?asset='+encodeURIComponent(asset.gltf),{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.body.dataset.ready||document.body.dataset.error);const error=await page.locator('body').getAttribute('data-error');if(error)throw Error(error);await page.locator('canvas').screenshot({path:target});done++;}catch(error){failed.push({key:asset.key,error:error.message});}
 }
 await browser.close();console.log(JSON.stringify({assets:assets.length,rendered:done,failed},null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
