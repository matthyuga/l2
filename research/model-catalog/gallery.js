const $=id=>document.getElementById(id), size=48;
let models=[],filtered=[],page=0,onlyFavorites=false,current=null,viewer=null;
let habitatIndex={npcs:{},zones:[]},habitatZones=new Map();
let npcFacts={};
const roleLabels={npc:'NPC',monster:'Monstruo',creature:'Criatura / mascota',raid:'Jefe de raid',epic:'Jefe épico',object:'Objeto',item:'Ítem / accesorio',effect:'Efecto visual',scene:'Escenario',unknown:'Sin clasificar'};
function npcRole(n){
 const type=n.type||'';
 if(type==='GrandBoss')return 'epic';if(type==='RaidBoss')return 'raid';
 if(['Pet','BabyPet','Servitor','TamedBeast','FeedableBeast','FriendlyMob'].includes(type))return 'creature';
 if(['Monster','RiftInvader','FestivalMonster'].includes(type))return 'monster';
 if(['Chest','EffectPoint','Artefact','ControlTower','FlameTower','BroadcastingTower','FlyTerrainObject'].includes(type))return 'object';
 return type?'npc':'unknown';
}
function cardFacts(m,npcs){
 const roles=[...new Set(npcs.map(npcRole))];
 if(!roles.length)roles.push(m.catalog_role||(m.types.includes('Escenario')?'scene':m.category==='Objetos'?'object':'unknown'));
 const levels=npcs.map(n=>n.level).filter(Number.isFinite),min=Math.min(...levels),max=Math.max(...levels);
 return {roles,frame:roles.length===1?roles[0]:'mixed',level:['item','effect'].includes(m.catalog_role)?'No aplica nivel de NPC':levels.length?'Lv. '+min+(min!==max?'–'+max:'')+(levels.length<npcs.length?' · parcial':''):'Nivel sin datos',tooltip:['item','effect'].includes(m.catalog_role)?'Este recurso no es una plantilla de NPC.':levels.length?'Nivel de las plantillas del servidor'+(min!==max?'; este modelo representa varios NPC.':'.'):'No hay un nivel de plantilla disponible para este recurso.'};
}
const habitatEntries=id=>habitatIndex.npcs[String(id)]||[];
function npcMatchesLocation(n){return habitatEntries(n.id).some(e=>{const z=habitatZones.get(e.zone);return z&&(!$('region').value||z.region===$('region').value)&&(!$('zone').value||z.id===$('zone').value);});}
function modelMatchesLocation(m){if($('zone').value==='__unknown')return !m.habitats.length;return (!$('region').value&&!$('zone').value)||m.npcs.some(npcMatchesLocation);}
function updateZoneOptions(){
 $('zone').replaceChildren(element('option','Todos los lugares'));$('zone').firstChild.value='';
 for(const z of habitatIndex.zones.filter(z=>!$('region').value||z.region===$('region').value)){
  const o=element('option',z.name+' · '+z.npc_count+' NPC');o.value=z.id;$('zone').append(o);
 }
 if(!$('region').value){const o=element('option','Sin ubicación registrada');o.value='__unknown';$('zone').append(o);}
}
function showHabitats(npc){
 $('habitats').replaceChildren();
 const entries=npc?habitatEntries(npc.id):[];
 if(!entries.length){$('habitats').append(element('p','Sin ubicación registrada en los archivos revisados. Puede ser personalizado, invocado o aparecer mediante un script.','small'));return;}
 $('habitats').append(element('strong','Apariciones registradas de este NPC'));
 for(const e of entries){const z=habitatZones.get(e.zone);if(!z)continue;
  const row=element('details'),summary=element('summary',z.region+' / '+z.name+(z.method==='approximate'?' [aproximado]':z.method==='grid'?' [sector sin nombre]':''));row.append(summary);
  row.append(element('p',habitatIndex.methods[z.method]+'. Fuentes: '+e.sources.join(', ')+(e.example?' · Ejemplo X/Y/Z: '+e.example.join(' / '):''),'small'));$('habitats').append(row);
 }
}
let chosen={};try{chosen=JSON.parse(localStorage.getItem('l2-model-choices')||'{}');}catch{}
const save=()=>localStorage.setItem('l2-model-choices',JSON.stringify(chosen));
const planningFields={name:'planningName',territory:'planningTerritory',level:'planningLevel',power:'planningPower',faction:'planningFaction'};
let draftTags=[];
const fold=value=>String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
function uniqueTags(values){const seen=new Set();return values.map(v=>String(v).trim()).filter(v=>{const key=fold(v);if(!key||seen.has(key))return false;seen.add(key);return true;});}
function planning(entry){const value=entry?.planning||{},result={};for(const key of Object.keys(planningFields))result[key]=typeof value[key]==='string'||typeof value[key]==='number'?String(value[key]):'';result.tags=uniqueTags(Array.isArray(value.tags)?value.tags:[]);return result;}
function planningSearch(m){const item=chosen[m.key],p=planning(item);return fold([m.search,p.name,p.territory,p.level,p.power,p.faction,...p.tags,item?.idea||''].join(' '));}
function updatePlanningFilters(){
 const drafts=Object.values(chosen).map(planning);
 for(const [id,values,label] of [['plannedRegion',drafts.map(p=>p.territory),'Todos los territorios propuestos'],['plannedTag',drafts.flatMap(p=>p.tags),'Todas las etiquetas']]){
  const select=$(id),previous=select.value;select.replaceChildren(element('option',label));select.firstChild.value='';
  for(const value of uniqueTags(values).sort((a,b)=>a.localeCompare(b,'es'))){const option=element('option',value);option.value=value;select.append(option);}
  if([...select.options].some(o=>o.value===previous))select.value=previous;
 }
 const list=$('planningTerritories');list.replaceChildren();for(const value of uniqueTags(drafts.map(p=>p.territory))){const option=element('option');option.value=value;list.append(option);}
}
function renderDraftTags(){
 $('draftTags').replaceChildren();for(const tag of draftTags){const button=element('button',tag+' ×','planningTag');button.type='button';button.setAttribute('aria-label','Quitar etiqueta '+tag);button.onclick=()=>{draftTags=draftTags.filter(v=>v!==tag);renderDraftTags();markPlanningDirty();};$('draftTags').append(button);}
}
function commitDraftTags(){const value=$('planningTagInput').value.trim();if(!value)return;draftTags=uniqueTags([...draftTags,...value.split(/[,;\n]+/)]);$('planningTagInput').value='';renderDraftTags();markPlanningDirty();}
function markPlanningDirty(){$('planningSaveStatus').textContent='Cambios sin guardar';if(current){const original=current.npcs.find(n=>String(n.id)===$('npc').value)?.name||current.title,proposed=$('planningName').value.trim();$('detailTitle').textContent=proposed||original;$('detailOriginalName').textContent=proposed?'Referencia original: '+original:'';}}
function toast(text){$('toast').textContent=text;$('toast').style.display='block';clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').style.display='none',3300);}
function element(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
function update(){const query=fold($('search').value.trim());filtered=models.filter(m=>
 ($('unused').checked||m.npc_count>0||m.external_source)&&($('unavailable').checked||m.has_thumbnail)&&(!$('batch').value||m.batch===$('batch').value)&&(!$('category').value||($('category').value==='Escenarios'?(m.types||[]).includes('Escenario'):m.category===$('category').value))&&(!$('package').value||m.package===$('package').value)&&(!$('textureQuality').value||m.material_review?.status===$('textureQuality').value)&&modelMatchesLocation(m)&&(!onlyFavorites||chosen[m.key])&&(!$('plannedRegion').value||fold(planning(chosen[m.key]).territory)===fold($('plannedRegion').value))&&(!$('plannedTag').value||planning(chosen[m.key]).tags.some(tag=>fold(tag)===fold($('plannedTag').value)))&&(!query||planningSearch(m).includes(query)));
 if(!onlyFavorites){const seen=new Set();filtered=filtered.filter(m=>{if(!m.item_group)return true;if(seen.has(m.item_group))return false;seen.add(m.item_group);return true;});}
 page=Math.min(page,Math.max(0,Math.ceil(filtered.length/size)-1));render();}
function goToPage(number){
 const total=Math.max(1,Math.ceil(filtered.length/size));
 if(!Number.isInteger(number)||number<1||number>total)return;
 page=number-1;render();$('paginationTop').scrollIntoView({block:'start',behavior:'smooth'});
}
function renderPagination(){
 const total=Math.max(1,Math.ceil(filtered.length/size)),active=page+1;
 const numbers=[...new Set([1,...Array.from({length:5},(_,i)=>active+i-2),total])].filter(n=>n>=1&&n<=total).sort((a,b)=>a-b);
 for(const id of ['paginationTop','paginationBottom']){
  const nav=$(id);nav.replaceChildren();
  const previous=element('button','← Anterior');previous.disabled=page===0;previous.onclick=()=>goToPage(active-1);nav.append(previous);
  const links=element('div',undefined,'pageNumbers');let last=0;
  for(const number of numbers){
   if(last&&number-last>1){const dots=element('span','…','pageGap');dots.setAttribute('aria-hidden','true');links.append(dots);}
   const button=element('button',String(number),'pageNumber');button.setAttribute('aria-label','Página '+number);button.onclick=()=>goToPage(number);
   if(number===active)button.setAttribute('aria-current','page');links.append(button);last=number;
  }
  nav.append(links);
  const next=element('button','Siguiente →');next.disabled=active===total;next.onclick=()=>goToPage(active+1);nav.append(next);
  const form=element('form',undefined,'pageJump'),label=element('label','Ir a página '),input=element('input');
  input.type='number';input.min='1';input.max=String(total);input.step='1';input.required=true;input.value=String(active);input.setAttribute('aria-label','Número de página');
  label.append(input);form.append(label,element('span','de '+total),element('button','Ir'));
  form.onsubmit=event=>{event.preventDefault();if(form.reportValidity())goToPage(Number(input.value));};nav.append(form);
 }
}
function render(){$('grid').replaceChildren();const first=page*size;
 for(const m of filtered.slice(first,first+size)){
  const localNpcs=($('region').value||$('zone').value)&&$('zone').value!=='__unknown'?m.npcs.filter(npcMatchesLocation):[];
  const displayTitle=localNpcs.length?[...new Set(localNpcs.map(n=>n.name||'NPC'))].join(' / '):m.title;
  const facts=cardFacts(m,localNpcs.length?localNpcs:m.npcs);
  const plan=planning(chosen[m.key]);
  const card=element('article',undefined,'card');card.dataset.modelKey=m.key;card.tabIndex=0;card.setAttribute('aria-label','Ver '+(plan.name||displayTitle));card.addEventListener('click',()=>detail(m));card.addEventListener('keydown',e=>{if(e.target!==card)return;if(e.key==='Enter'||e.key===' '){e.preventDefault();detail(m);}});
  card.dataset.role=facts.frame;
  const banner=element('div',undefined,'cardBanner'),badges=element('div',undefined,'roleBadges');
  for(const role of facts.roles){const badge=element('span',roleLabels[role],'roleBadge');badge.dataset.role=role;badges.append(badge);}
  const level=element('span',facts.level,'levelBadge');level.title=facts.tooltip;banner.append(badges,level);card.append(banner);
  if(m.has_thumbnail){const img=element('img');img.src=m.thumbnail;img.alt=m.title;img.loading='lazy';card.append(img);}else card.append(element('div','Recurso sin vista previa','missing'));
  const star=element('button',chosen[m.key]?'★':'☆','star');star.setAttribute('aria-label','Elegir '+m.title);star.onclick=e=>{e.stopPropagation();toggle(m);update();};card.append(star);
  const info=element('div',undefined,'cardinfo');const title=element('span',plan.name||displayTitle,'cardtitle');title.title=plan.name||displayTitle;info.append(title);
  if(plan.name)info.append(element('span','Modelo: '+displayTitle,'cardmeta originalTitle'));
  info.append(element('span',m.batch+' · '+m.category+' · '+(m.npc_count?m.npc_count+' NPC asociados':'Sin NPC asociado'),'cardmeta'));
  const metadata=[plan.territory,plan.faction,plan.level?'Nivel propuesto: '+plan.level:'',plan.power?'IP propuesto: '+plan.power:'',...plan.tags].filter(Boolean);
  if(metadata.length){const tags=element('div',undefined,'cardPlanning');for(const label of metadata.slice(0,6))tags.append(element('span',label,'planningBadge'));if(metadata.length>6)tags.append(element('span','+'+(metadata.length-6)+' más','planningBadge'));info.append(tags);}
  if(m.item_group)info.append(element('span',models.filter(v=>v.item_group===m.item_group).length+' versiones · elegir en la ficha','cardmeta'));
  if(localNpcs.length)info.append(element('span','En este lugar: '+localNpcs.map(n=>(n.name||'NPC')+' #'+n.id).join(', '),'cardmeta habitatMatches'));
  else if(m.habitats.length){const places=[...new Set(m.habitats.map(e=>habitatZones.get(e.zone)?.region).filter(Boolean))];info.append(element('span','Ubicación: '+places.slice(0,3).join(', ')+(places.length>3?' y otras':''),'cardmeta'));}
  if(m.material_review?.status==='pending')info.append(element('span',m.material_review.text,'cardmeta texturePending'));
  else if(m.material_issue&&m.material_review?.status!=='complete')info.append(element('span',m.material_issue,'cardmeta'));
  if(m.scene_review)info.append(element('span',m.scene_review,'cardmeta'));card.append(info);$('grid').append(card);
 }
 if(!filtered.length)$('grid').append(element('p','No hay modelos que coincidan con estos filtros.','empty'));
 $('counter').textContent=filtered.length+' modelos · '+Object.keys(chosen).length+' elegidos';renderPagination();
}
function toggle(m){if(chosen[m.key])delete chosen[m.key];else chosen[m.key]={key:m.key,mesh:m.mesh,title:m.title,npc_id:m.npcs[0]?.id||null,idea:''};save();updatePlanningFilters();}
function reference(){const npc=current.npcs.find(n=>String(n.id)===$('npc').value);$('reference').textContent=npc?['ID '+npc.id,npc.name,roleLabels[npcRole(npc)],Number.isFinite(npc.level)?'Nivel '+npc.level:'Nivel sin datos',npc.type].filter(Boolean).join(' · '):current.catalog_role==='item'?'Ítem / accesorio de cabeza. Sin nivel ni ID de NPC.':current.catalog_role==='effect'?'Recurso de efecto visual. Sin nivel de NPC.':'Esta malla no tiene un NPC asociado en el catálogo base.';const proposed=$('planningName').value.trim();$('detailTitle').textContent=proposed||npc?.name||current.title;$('detailOriginalName').textContent=proposed?'Referencia original: '+(npc?.name||current.title):'';$('copy').disabled=!npc;showHabitats(npc);$('habitats').hidden=['item','effect'].includes(current.catalog_role);}
function showAssetSource(m){
 let panel=$('assetSource');if(!panel){panel=element('section',undefined,'assetSource small');panel.id='assetSource';$('materialNote').after(panel);}panel.replaceChildren();panel.hidden=!m.external_asset;if(!m.external_asset)return;
 panel.append(element('strong','Asset externo · adaptación a Interlude pendiente'));
 if(m.preview_review?.status==='partial')panel.append(element('p','Revisión visual pendiente: '+m.preview_review.text));
 const source=m.source||{},facts=m.asset_analysis||{};
 if(source.author)panel.append(element('p','Autor: '+source.author));
 if(source.license_label)panel.append(element('p','Licencia declarada: '+source.license_label));
 if(source.url){const link=element('a','Ver publicación original');link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';panel.append(link);}
 if(m.rig_analysis){const paragraph=element('p'),link=element('a','Abrir ficha técnica de huesos y animaciones');link.href='rig-inspector.html?model='+encodeURIComponent(m.key);link.target='_blank';link.rel='noopener noreferrer';paragraph.append(link);panel.append(paragraph);}
 const parts=[];if(Number.isFinite(facts.triangles))parts.push(facts.triangles.toLocaleString('es')+' triángulos');if(Number.isFinite(facts.bones))parts.push(facts.bones+' huesos');if(Number.isFinite(facts.animations))parts.push(facts.animations+' animaciones');panel.append(element('p',parts.join(' · ')));
 if(facts.animations)panel.append(element('p','Elegí una animación desde la vista 3D.'));else panel.append(element('p',facts.bones?'Incluye esqueleto; este archivo no trae animaciones.':'Modelo estático; no se detectó un esqueleto.'));
}
function detail(m){current=m;showAssetSource(m);
 const variants=m.item_group?models.filter(v=>v.item_group===m.item_group):[];
 $('itemVersions').hidden=!variants.length;$('itemVariant').replaceChildren();
 for(const v of variants){const option=element('option',v.item_variant+(v.status!=='ready'?' · sin vista disponible':'')+(chosen[v.key]?' · ★ guardado':''));option.value=v.key;$('itemVariant').append(option);}
 $('itemVariant').value=m.key;
viewer?.dispose();viewer=null;$('view3d').replaceChildren();$('view3d').hidden=true;$('detailImage').hidden=false;$('detailImage').src=m.has_thumbnail?m.thumbnail:'';$('detailImage').alt=m.title;
 $('terrain').hidden=!m.terrain_included;$('terrain').disabled=true;$('terrain').dataset.visible=String(m.terrain_visible!==false);$('terrain').textContent=m.terrain_visible===false?'Mostrar terreno':'Ocultar terreno';
 $('detailCategory').textContent=m.batch+' / '+m.category+' / '+m.package;$('detailTitle').textContent=m.title;$('mesh').textContent=m.mesh;$('viewstatus').textContent='';$('show3d').textContent='Vista 3D';$('show3d').disabled=m.status!=='ready';$('native').disabled=m.status!=='ready'||!!m.preview_only;$('native').textContent=m.external_asset?'Solo visor web':'Abrir con animaciones';$('native').title=m.external_asset?'Este recurso externo todavía no está adaptado al cliente de Lineage II.':m.preview_only?'Montaje disponible en la vista 3D web; las piezas originales se abren por separado en UModel.':'';
 $('materialNote').textContent=(m.material_review?.text?m.material_review.text+'. ':'')+(m.status==='failed'?(m.note||'La referencia del catálogo no pudo leerse en este cliente.'):m.classification_note||m.note||'Vista representativa del cuerpo. El NPC elegido puede usar otros colores o efectos.');
 $('npc').replaceChildren();for(const n of m.npcs){const option=element('option',(n.name||'NPC')+' · '+n.id+(Number.isFinite(n.level)?' · Lv. '+n.level:''));option.value=n.id;$('npc').append(option);}
 $('npc').disabled=!m.npcs.length;if(chosen[m.key]?.npc_id)$('npc').value=chosen[m.key].npc_id;
 if($('region').value||$('zone').value){const matched=m.npcs.find(npcMatchesLocation);if(matched)$('npc').value=matched.id;}
 const plan=planning(chosen[m.key]);for(const [key,id] of Object.entries(planningFields))$(id).value=plan[key];draftTags=[...plan.tags];$('planningTagInput').value='';renderDraftTags();
 $('idea').value=chosen[m.key]?.idea||'';$('planningSaveStatus').textContent=chosen[m.key]?'Ficha guardada en este navegador':'Completá los datos y guardá la ficha';$('saveFavorite').textContent=chosen[m.key]?'★ Guardar cambios':'☆ Guardar entre mis elegidos';reference();if(!$('detail').open)$('detail').showModal();}
$('itemVariant').onchange=()=>{const variant=models.find(m=>m.key===$('itemVariant').value);if(variant)detail(variant);};
$('terrain').onclick=()=>{if(!viewer)return;const visible=$('terrain').dataset.visible!=='true';viewer.setTerrainVisible(visible);$('terrain').dataset.visible=String(visible);$('terrain').textContent=visible?'Ocultar terreno':'Mostrar terreno';};
function close(){$('detail').close();viewer?.dispose();viewer=null;}
$('close').onclick=close;$('detail').addEventListener('close',()=>{viewer?.dispose();viewer=null;});$('npc').onchange=()=>{reference();markPlanningDirty();};
for(const id of [...Object.values(planningFields),'idea','planningTagInput'])$(id).addEventListener('input',markPlanningDirty);
$('addPlanningTag').onclick=commitDraftTags;
$('planningTagInput').addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===','||event.key===';'){event.preventDefault();commitDraftTags();}});
$('saveFavorite').onclick=()=>{commitDraftTags();const previous=chosen[current.key]||{},draft={...(previous.planning||{})};for(const [key,id] of Object.entries(planningFields))draft[key]=$(id).value.trim();draft.tags=[...draftTags];chosen[current.key]={...previous,key:current.key,mesh:current.mesh,title:current.title,npc_id:Number($('npc').value)||null,idea:$('idea').value.trim(),planning:draft};save();$('saveFavorite').textContent='★ Guardar cambios';$('planningSaveStatus').textContent='Ficha guardada en este navegador';updatePlanningFilters();update();toast('Ficha y etiquetas guardadas.');};
$('copy').onclick=async()=>{try{await navigator.clipboard.writeText($('npc').value);toast('ID copiado.');}catch{toast('ID: '+$('npc').value);}};
$('native').onclick=async()=>{$('native').disabled=true;try{const res=await fetch('/api/viewer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:current.key})});const result=await res.json();if(!res.ok)throw new Error(result.error);toast(result.message);}catch(e){toast(e.message);}finally{$('native').disabled=current.status!=='ready'||!!current.preview_only;}};
$('show3d').onclick=async()=>{if(viewer){$('view3d').hidden=!$('view3d').hidden;$('detailImage').hidden=!$('view3d').hidden;$('show3d').textContent=$('view3d').hidden?'Vista 3D':'Ver imagen';return;}
 const selected=current;
 $('view3d').hidden=false;$('detailImage').hidden=true;$('viewstatus').textContent='Cargando modelo 3D…';$('show3d').disabled=true;
 try{const module=await import('./viewer.js?v=20261028-round4');const created=await module.createViewer($('view3d'),selected.gltf,selected.view_bounds,selected.terrain_visible!==false);if(current!==selected||!$('detail').open){created.dispose();return;}viewer=created;$('terrain').disabled=false;$('viewstatus').textContent='';$('show3d').textContent='Ver imagen';}catch(e){$('viewstatus').textContent=selected.external_asset?'No se pudo abrir este asset externo.':'No se pudo abrir la vista 3D. Probá el visor con animaciones.';$('view3d').hidden=true;$('detailImage').hidden=false;console.error(e);}finally{$('show3d').disabled=false;}};
for(const id of ['search','category','package','batch','unused','unavailable','textureQuality'])$(id).addEventListener(id==='search'?'input':'change',()=>{page=0;update();});
$('region').onchange=()=>{updateZoneOptions();page=0;update();};$('zone').onchange=()=>{page=0;update();};
for(const id of ['plannedRegion','plannedTag'])$(id).onchange=()=>{page=0;update();};
$('favorites').onclick=()=>{onlyFavorites=!onlyFavorites;$('favorites').setAttribute('aria-pressed',onlyFavorites);page=0;update();};
$('import').onclick=()=>$('importFile').click();
$('importFile').onchange=async()=>{
 const file=$('importFile').files[0];if(!file)return;
 try{
  if(file.size>20*1024*1024)throw new Error('El archivo supera 20 MB.');
  const data=JSON.parse((await file.text()).replace(/^\uFEFF/,''));
  if(!data||!Array.isArray(data.selections)||![1,2].includes(data.schema_version??1))throw new Error('Formato de selección no reconocido.');
  const next={...chosen},seen=new Set(),byKey=new Map(models.map(m=>[m.key,m]));
  for(const entry of data.selections){
   if(!entry||typeof entry!=='object'||Array.isArray(entry)||typeof entry.key!=='string'||!entry.key||['__proto__','prototype','constructor'].includes(entry.key)||seen.has(entry.key))throw new Error('Hay fichas inválidas o claves duplicadas.');
   seen.add(entry.key);
   for(const field of ['mesh','title','idea'])if(entry[field]!=null&&typeof entry[field]!=='string')throw new Error('Los textos de una ficha no son válidos.');
   const plan=entry.planning;
   if(plan!=null){
    if(typeof plan!=='object'||Array.isArray(plan))throw new Error('Los datos de planificación no son válidos.');
    for(const field of ['name','territory','level','power','faction'])if(plan[field]!=null&&typeof plan[field]!=='string')throw new Error('Los textos de planificación no son válidos.');
    if(plan.tags!=null&&(!Array.isArray(plan.tags)||plan.tags.some(t=>typeof t!=='string')))throw new Error('Las etiquetas no son válidas.');
   }
   const match=byKey.get(entry.key)||models.find(m=>m.mesh.toLowerCase()===String(entry.mesh||'').toLowerCase());
   if(match&&entry.mesh&&match.mesh.toLowerCase()!==entry.mesh.toLowerCase())throw new Error('Una clave del archivo pertenece a otra malla.');
   const key=match?.key||entry.key,old=next[key],merged={...entry,...old,key};
   if(!old?.idea&&entry.idea)merged.idea=entry.idea;
   if(plan||old?.planning){
    merged.planning={...plan,...old?.planning};
    for(const field of ['name','territory','level','power','faction'])if(!old?.planning?.[field]&&plan?.[field])merged.planning[field]=plan[field];
    merged.planning.tags=uniqueTags([...(old?.planning?.tags||[]),...(plan?.tags||[])]);
   }
   next[key]=merged;
  }
  localStorage.setItem('l2-model-choices',JSON.stringify(next));chosen=next;updatePlanningFilters();page=0;update();
  toast('Selección recuperada: '+data.selections.length+' fichas. Se conservaron los datos ya guardados.');
 }catch(e){toast('No se importó el archivo: '+e.message);}
 finally{$('importFile').value='';}
};
$('export').onclick=()=>{const selections=Object.values(chosen);if(!selections.length)return toast('Elegí al menos un modelo con la estrella.');const blob=new Blob([JSON.stringify({schema_version:2,selections},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=element('a');a.href=url;a.download='modelos-l2-elegidos.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
function normalizeModel(m){
 const names=Array.isArray(m.names)?m.names:[],npcs=Array.isArray(m.npcs)?m.npcs.filter(n=>n&&typeof n==='object').map(n=>{const facts=npcFacts[String(n.id)];return {...n,...(facts?{level:facts.level,type:facts.type||n.type,race:facts.race}:{level:Number.isFinite(n.level)?n.level:null})};}):[];
 const mesh=String(m.mesh||''),title=String(m.title||mesh||m.key||'Modelo sin nombre'),batch=m.batch||'Tanda original';
 const habitats=npcs.flatMap(n=>habitatEntries(n.id)),placeNames=[...new Set(habitats.flatMap(e=>{const z=habitatZones.get(e.zone);return z?[z.name,z.region]:[];}))];
 return {...m,mesh,title,batch,names,npcs,habitats,types:Array.isArray(m.types)?m.types:[],npc_count:m.npc_count??npcs.length,
  search:[title,mesh,batch,m.archive_title||'',m.chronicle||'',m.source?.author||'',...(m.source?.tags||[]),...names,...npcs.map(n=>n.id),...placeNames].join(' ').toLocaleLowerCase()};
}
try{const res=await fetch('/api/catalog');if(!res.ok)throw new Error('Catálogo no disponible');const data=await res.json();
 try{const hr=await fetch('habitats.json?v=20261023');if(!hr.ok)throw new Error('Índice no disponible');habitatIndex=await hr.json();habitatZones=new Map(habitatIndex.zones.map(z=>[z.id,z]));}
 catch(e){$('locationNote').textContent='El catálogo está disponible, pero no se pudo cargar el índice de zonas.';$('region').disabled=true;$('zone').disabled=true;console.error(e);}
 try{const response=await fetch('npc-facts.json?v=20261023');if(!response.ok)throw new Error('Niveles no disponibles');npcFacts=(await response.json()).npcs;}
 catch(e){$('factsNote').textContent='No se pudieron cargar los niveles del servidor. Los tipos disponibles se conservan; no se asignan niveles estimados.';console.error(e);}
 models=data.models.map(normalizeModel).sort((a,b)=>a.title.localeCompare(b.title,'es'));
 $('import').disabled=false;
 $('batch').replaceChildren(element('option','Todas'));$('batch').firstChild.value='';for(const batch of [...new Set(models.map(m=>m.batch))].sort((a,b)=>a.localeCompare(b,'es'))){const option=element('option',batch);option.value=batch;$('batch').append(option);}
 const usedRegions=[...new Set(models.flatMap(m=>m.habitats.map(e=>habitatZones.get(e.zone)?.region).filter(Boolean)))].sort((a,b)=>a.localeCompare(b,'es'));
 for(const region of usedRegions){const o=element('option',region);o.value=region;$('region').append(o);}updateZoneOptions();
 const remapped={};for(const [oldKey,entry] of Object.entries(chosen)){const match=models.find(m=>m.key===entry.key)||models.find(m=>m.mesh.toLowerCase()===String(entry.mesh).toLowerCase());if(match)remapped[match.key]={...entry,key:match.key};else remapped[oldKey]=entry;}chosen=remapped;save();updatePlanningFilters();
 for(const pkg of [...new Set(models.map(m=>m.package))].sort()){const o=element('option',pkg);o.value=pkg;$('package').append(o);}
 const params=new URLSearchParams(location.search);$('search').value=params.get('q')||'';$('batch').value=params.get('batch')||'';$('category').value=params.get('category')||'';$('region').value=params.get('region')||'';updateZoneOptions();$('zone').value=params.get('zone')||'';update();const selected=models.find(m=>m.key===params.get('model'));if(selected){detail(selected);if(params.get('view')==='3d')$('show3d').click();}}
catch(e){$('counter').textContent='No se pudo cargar el catálogo.';$('grid').append(element('p','Error al cargar la galería: '+e.message+'. Si el servicio está cerrado, abrí GALERIA-MODELOS-L2.cmd.','empty'));console.error(e);}
