const {chromium}=require('E:/l2-local/tools/rea-runtime/node_modules/playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const qa='E:/l2-local/tmp/gallery-planning-20261027';fs.mkdirSync(qa,{recursive:true});
const origin='http://127.0.0.1:32280';
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
 const context=await browser.newContext({viewport:{width:1440,height:1100},acceptDownloads:true});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const catalog=await (await context.request.get(origin+'/api/catalog')).json();
 const hardin=catalog.models.find(m=>m.key==='m0435'),noble=catalog.models.find(m=>m.key==='m0439');
 const fixture={
  m0435:{key:hardin.key,mesh:hardin.mesh,title:hardin.title,npc_id:30832,idea:'Nota que ya existía',legacy_flag:'conservar',planning:{custom_field:'también conservar'}},
  m0439:{key:noble.key,mesh:noble.mesh,title:noble.title,npc_id:35064,idea:'Otra nota intacta'},
  missing_legacy:{key:'missing_legacy',mesh:'Missing.Unavailable',title:'Referencia antigua',idea:'No borrar al cargar'}
 };
 await context.addInitScript(seed=>{if(!sessionStorage.getItem('planning-test-seeded')){localStorage.setItem('l2-model-choices',JSON.stringify(seed));sessionStorage.setItem('planning-test-seeded','yes');}},fixture);
 await page.goto(origin+'/?model=m0435');
 await page.waitForFunction(()=>document.querySelector('#detail').open&&document.querySelector('#grid .card'));
 let saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('l2-model-choices')));
 assert.equal(saved.m0435.idea,fixture.m0435.idea);assert.deepEqual(saved.missing_legacy,fixture.missing_legacy);
 assert.equal(await page.locator('#idea').inputValue(),fixture.m0435.idea);
 const original=await page.locator('#reference').innerText();
 await page.locator('#planningName').fill('Raoul - el Unificador');
 await page.locator('#planningTerritory').fill('Aden');
 await page.locator('#planningFaction').fill('Defensores del sur');
 await page.locator('#planningLevel').fill('75-80');
 await page.locator('#planningPower').fill('400k / 850k máximo');
 await page.locator('#planningTagInput').fill('prólogo, capitán, PRÓLOGO');
 await page.locator('#addPlanningTag').click();
 assert.equal(await page.locator('#draftTags button').count(),2);
 await page.locator('#planningTagInput').fill('veterano');
 await page.locator('#saveFavorite').click();
 saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('l2-model-choices')));
 assert.equal(saved.m0435.idea,fixture.m0435.idea);
 assert.equal(saved.m0435.legacy_flag,'conservar');assert.equal(saved.m0435.planning.custom_field,'también conservar');
 assert.equal(saved.m0435.title,hardin.title);assert.equal(saved.m0435.npc_id,30832);
 assert.deepEqual(saved.m0435.planning.tags,['prólogo','capitán','veterano']);
 assert.equal(saved.m0435.planning.name,'Raoul - el Unificador');
 assert.deepEqual(saved.m0439,fixture.m0439);
 assert.equal(await page.locator('#reference').innerText(),original);
 assert.match(await page.locator('#detailOriginalName').innerText(),/Hardin/);
 assert.equal(await page.locator('#detailTitle').innerText(),'Raoul - el Unificador');
 await page.locator('#planningHeading').scrollIntoViewIfNeeded();
 await page.screenshot({path:path.join(qa,'ficha.png')});
 await page.locator('#close').click();
 await page.locator('#favorites').click();
 await page.locator('#plannedRegion').selectOption('Aden');
 await page.locator('#plannedTag').selectOption('capitán');
 assert.equal(await page.locator('#grid .card').count(),1);
 assert.match(await page.locator('#grid .card .cardtitle').innerText(),/Raoul/);
 for(const query of ['raoul','capitan','400k','defensores','Nota que ya existia']){
  await page.locator('#search').fill(query);assert.equal(await page.locator('#grid .card').count(),1,query);
 }
 await page.locator('#search').fill('');
 await page.screenshot({path:path.join(qa,'catalogo-filtrado.png'),fullPage:true});
 const downloadEvent=page.waitForEvent('download');await page.locator('#export').click();
 const download=await downloadEvent;const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));
 assert.equal(exported.schema_version,2);assert.equal(exported.selections.length,3);
 assert.deepEqual(exported.selections.find(r=>r.key==='m0435'),saved.m0435);
 assert.deepEqual(exported.selections.find(r=>r.key==='missing_legacy'),fixture.missing_legacy);
 await page.reload();await page.waitForFunction(()=>document.querySelector('#detail').open&&document.querySelector('#grid .card'));
 assert.equal(await page.locator('#planningName').inputValue(),'Raoul - el Unificador');
 assert.equal(await page.locator('#planningPower').inputValue(),'400k / 850k máximo');
 assert.equal(await page.locator('#draftTags button').count(),3);
 await page.getByRole('button',{name:'Quitar etiqueta capitán',exact:true}).click();
 await page.locator('#planningTagInput').fill('Sin etiqueta');await page.locator('#planningTagInput').press('Enter');
 await page.locator('#planningTagInput').fill('<img src=x onerror=alert(1)>');await page.locator('#addPlanningTag').click();
 assert.equal(await page.locator('#draftTags img').count(),0);
 await page.locator('#saveFavorite').click();
 assert.equal(await page.locator('#plannedTag option[value="capitán"]').count(),0);
 saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('l2-model-choices')));
 assert(saved.m0435.planning.tags.includes('Sin etiqueta'));
 assert(!saved.m0435.planning.tags.includes('capitán'));
 await page.setViewportSize({width:390,height:844});
 await page.locator('#planningHeading').scrollIntoViewIfNeeded();
 assert(await page.locator('#planningName').evaluate(e=>e.getBoundingClientRect().right<=window.innerWidth));
 assert(await page.locator('#detail').evaluate(e=>e.scrollWidth<=e.clientWidth+1));
 await page.screenshot({path:path.join(qa,'ficha-movil.png')});
 await page.locator('#close').click();
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 // Native reference switching continues to show the actual source NPC level.
 await page.setViewportSize({width:1440,height:1100});
 await page.goto(origin+'/?model=m0439');await page.waitForFunction(()=>document.querySelector('#detail').open);
 const opts=await page.locator('#npc option').evaluateAll(os=>os.map(o=>o.value));
 if(opts.length>1){await page.locator('#npc').selectOption(opts[1]);assert.match(await page.locator('#reference').innerText(),new RegExp('ID '+opts[1]));}
 // An external resource with no NPC can be planned and exported too.
 const external=catalog.models.find(m=>m.key==='b2_7df2a6e630e45ac11e');assert(external);
 await page.goto(origin+'/?model='+external.key);await page.waitForFunction(()=>document.querySelector('#detail').open);
 assert(await page.locator('#copy').isDisabled());
 await page.locator('#planningName').fill('Capitán de la frontera');
 await page.locator('#planningTagInput').fill('rescate');await page.locator('#saveFavorite').click();
 const npcFree=await page.evaluate(key=>JSON.parse(localStorage.getItem('l2-model-choices'))[key],external.key);
 assert.equal(npcFree.npc_id,null);assert.equal(npcFree.planning.name,'Capitán de la frontera');
 assert.deepEqual(errors,[]);
 const result={legacy_favorites:'preserved',missing_favorite:'preserved',unknown_fields:'preserved',tags:'add/deduplicate/remove/enter/pending-save',search:'name/tag/power/faction/note/accent',filters:'territory/tag',export:'schema2 with old and new fields',reload:'persisted',mobile:'no overflow',references:'unchanged',no_npc_resource:'saved',errors};
 fs.writeFileSync(path.join(qa,'verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
