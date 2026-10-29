const $=id=>document.getElementById(id), size=48;
let models=[],filtered=[],page=0,onlyFavorites=false,current=null,viewer=null;
let chosen={};try{chosen=JSON.parse(localStorage.getItem('l2-model-choices')||'{}');}catch{}
const save=()=>localStorage.setItem('l2-model-choices',JSON.stringify(chosen));
function toast(text){$('toast').textContent=text;$('toast').style.display='block';clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').style.display='none',3300);}
function element(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
function update(){const query=$('search').value.trim().toLocaleLowerCase();filtered=models.filter(m=>
 ($('unused').checked||m.npc_count>0||m.external_source)&&($('unavailable').checked||m.has_thumbnail)&&(!$('batch').value||m.batch===$('batch').value)&&(!$('category').value||($('category').value==='Escenarios'?(m.types||[]).includes('Escenario'):m.category===$('category').value))&&(!$('package').value||m.package===$('package').value)&&(!onlyFavorites||chosen[m.key])&&(!query||m.search.includes(query)));
 page=Math.min(page,Math.max(0,Math.ceil(filtered.length/size)-1));render();}
function render(){$('grid').replaceChildren();const first=page*size;
 for(const m of filtered.slice(first,first+size)){
  const card=element('article',undefined,'card');card.tabIndex=0;card.setAttribute('aria-label','Ver '+m.title);card.addEventListener('click',()=>detail(m));card.addEventListener('keydown',e=>{if(e.target!==card)return;if(e.key==='Enter'||e.key===' '){e.preventDefault();detail(m);}});
  if(m.has_thumbnail){const img=element('img');img.src=m.thumbnail;img.alt=m.title;img.loading='lazy';card.append(img);}else card.append(element('div','Recurso sin vista previa','missing'));
  const star=element('button',chosen[m.key]?'★':'☆','star');star.setAttribute('aria-label','Elegir '+m.title);star.onclick=e=>{e.stopPropagation();toggle(m);update();};card.append(star);
  const info=element('div',undefined,'cardinfo');info.append(element('span',m.title,'cardtitle'),element('span',m.batch+' · '+m.category+' · '+(m.npc_count?m.npc_count+' NPC asociados':'Sin NPC asociado'),'cardmeta'));if(m.material_issue)info.append(element('span',m.material_issue,'cardmeta'));card.append(info);$('grid').append(card);
 }
 if(!filtered.length)$('grid').append(element('p','No hay modelos que coincidan con estos filtros.','empty'));
 $('counter').textContent=filtered.length+' modelos · '+Object.keys(chosen).length+' elegidos';$('page').textContent='Página '+(page+1)+' de '+Math.max(1,Math.ceil(filtered.length/size));$('previous').disabled=page===0;$('next').disabled=first+size>=filtered.length;
}
function toggle(m){if(chosen[m.key])delete chosen[m.key];else chosen[m.key]={key:m.key,mesh:m.mesh,title:m.title,npc_id:m.npcs[0]?.id||null,idea:''};save();}
function reference(){const npc=current.npcs.find(n=>String(n.id)===$('npc').value);$('reference').textContent=npc?['ID '+npc.id,npc.name,npc.type].filter(Boolean).join(' · '):'Esta malla no tiene un NPC asociado en el catálogo base.';$('copy').disabled=!npc;}
function detail(m){current=m;viewer?.dispose();viewer=null;$('view3d').replaceChildren();$('view3d').hidden=true;$('detailImage').hidden=false;$('detailImage').src=m.has_thumbnail?m.thumbnail:'';$('detailImage').alt=m.title;
 $('terrain').hidden=!m.terrain_included;$('terrain').disabled=true;$('terrain').dataset.visible=String(m.terrain_visible!==false);$('terrain').textContent=m.terrain_visible===false?'Mostrar terreno':'Ocultar terreno';
 $('detailCategory').textContent=m.batch+' / '+m.category+' / '+m.package;$('detailTitle').textContent=m.title;$('mesh').textContent=m.mesh;$('viewstatus').textContent='';$('show3d').textContent='Vista 3D';$('show3d').disabled=m.status!=='ready';$('native').disabled=m.status!=='ready'||!!m.preview_only;$('native').title=m.preview_only?'Montaje disponible en la vista 3D web; las piezas originales se abren por separado en UModel.':'';
 $('materialNote').textContent=m.status==='failed'?(m.note||'La referencia del catálogo no pudo leerse en este cliente.'):m.note||'Vista representativa del cuerpo. El NPC elegido puede usar otros colores o efectos.';
 $('npc').replaceChildren();for(const n of m.npcs){const option=element('option',(n.name||'NPC')+' · '+n.id);option.value=n.id;$('npc').append(option);}
 $('npc').disabled=!m.npcs.length;if(chosen[m.key]?.npc_id)$('npc').value=chosen[m.key].npc_id;
 $('idea').value=chosen[m.key]?.idea||'';$('saveFavorite').textContent=chosen[m.key]?'★ Guardado entre mis elegidos':'☆ Guardar entre mis elegidos';reference();$('detail').showModal();}
$('terrain').onclick=()=>{if(!viewer)return;const visible=$('terrain').dataset.visible!=='true';viewer.setTerrainVisible(visible);$('terrain').dataset.visible=String(visible);$('terrain').textContent=visible?'Ocultar terreno':'Mostrar terreno';};
function close(){$('detail').close();viewer?.dispose();viewer=null;}
$('close').onclick=close;$('detail').addEventListener('close',()=>{viewer?.dispose();viewer=null;});$('npc').onchange=reference;
$('saveFavorite').onclick=()=>{chosen[current.key]={key:current.key,mesh:current.mesh,title:current.title,npc_id:Number($('npc').value)||null,idea:$('idea').value.trim()};save();$('saveFavorite').textContent='★ Guardado entre mis elegidos';update();toast('Modelo guardado.');};
$('copy').onclick=async()=>{try{await navigator.clipboard.writeText($('npc').value);toast('ID copiado.');}catch{toast('ID: '+$('npc').value);}};
$('native').onclick=async()=>{$('native').disabled=true;try{const res=await fetch('/api/viewer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:current.key})});const result=await res.json();if(!res.ok)throw new Error(result.error);toast(result.message);}catch(e){toast(e.message);}finally{$('native').disabled=current.status!=='ready'||!!current.preview_only;}};
$('show3d').onclick=async()=>{if(viewer){$('view3d').hidden=!$('view3d').hidden;$('detailImage').hidden=!$('view3d').hidden;$('show3d').textContent=$('view3d').hidden?'Vista 3D':'Ver imagen';return;}
 const selected=current;
 $('view3d').hidden=false;$('detailImage').hidden=true;$('viewstatus').textContent='Cargando modelo 3D…';$('show3d').disabled=true;
 try{const module=await import('./viewer.js');const created=await module.createViewer($('view3d'),selected.gltf,selected.view_bounds,selected.terrain_visible!==false);if(current!==selected||!$('detail').open){created.dispose();return;}viewer=created;$('terrain').disabled=false;$('viewstatus').textContent='';$('show3d').textContent='Ver imagen';}catch(e){$('viewstatus').textContent='No se pudo abrir la vista 3D. Probá el visor con animaciones.';$('view3d').hidden=true;$('detailImage').hidden=false;console.error(e);}finally{$('show3d').disabled=false;}};
for(const id of ['search','category','package','batch','unused','unavailable'])$(id).addEventListener(id==='search'?'input':'change',()=>{page=0;update();});
$('favorites').onclick=()=>{onlyFavorites=!onlyFavorites;$('favorites').setAttribute('aria-pressed',onlyFavorites);page=0;update();};
$('previous').onclick=()=>{page--;render();window.scrollTo({top:0,behavior:'smooth'});};$('next').onclick=()=>{page++;render();window.scrollTo({top:0,behavior:'smooth'});};
$('export').onclick=()=>{const selections=Object.values(chosen);if(!selections.length)return toast('Elegí al menos un modelo con la estrella.');const blob=new Blob([JSON.stringify({selections},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=element('a');a.href=url;a.download='modelos-l2-elegidos.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
try{const res=await fetch('/api/catalog');if(!res.ok)throw new Error('Catálogo no disponible');const data=await res.json();models=data.models.map(m=>({...m,batch:m.batch||'Tanda original',search:[m.mesh,m.batch||'Tanda original',m.archive_title||'',m.chronicle||'',...m.names,...m.npcs.map(n=>n.id)].join(' ').toLocaleLowerCase()})).sort((a,b)=>a.title.localeCompare(b.title,'es'));
 const remapped={};for(const entry of Object.values(chosen)){const match=models.find(m=>m.key===entry.key)||models.find(m=>m.mesh.toLowerCase()===String(entry.mesh).toLowerCase());if(match)remapped[match.key]={...entry,key:match.key};}chosen=remapped;save();
 for(const pkg of [...new Set(models.map(m=>m.package))].sort()){const o=element('option',pkg);o.value=pkg;$('package').append(o);}
 const params=new URLSearchParams(location.search);$('search').value=params.get('q')||'';$('batch').value=params.get('batch')||'';$('category').value=params.get('category')||'';update();const selected=models.find(m=>m.key===params.get('model'));if(selected){detail(selected);if(params.get('view')==='3d')$('show3d').click();}}
catch(e){$('counter').textContent='No se pudo cargar el catálogo.';$('grid').append(element('p','Abrí GALERIA-MODELOS-L2.cmd para iniciar la galería.','empty'));console.error(e);}
